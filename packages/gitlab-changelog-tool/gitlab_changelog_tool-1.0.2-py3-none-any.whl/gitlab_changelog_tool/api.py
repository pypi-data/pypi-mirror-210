'''
Application implementation package.
'''

from datetime import datetime, timedelta, timezone
from operator import attrgetter
from pathlib import Path
from typing import Iterable, List

import dateutil.parser
import gitlab
import semver
from jinja2 import Template


def ensure_merge_request_format(merge_requests: Iterable, merged_after: str) -> List[str]:
    '''
    Ensure merge request timestamps and return titles.

    Parameters:
        merge_requests (Iterable): Merge request iterable.
        merged_after (str): String timestamp.

    Returns:
        merge_requests (List[str]): Merge request titles.
    '''

    merged_after = dateutil.parser.parse(merged_after)

    return list(
        map(
            attrgetter('title'),
            filter(
                lambda request: (
                    dateutil.parser.parse(request.merged_at) >= merged_after
                ),
                merge_requests
            )
        )
    )


def generate(  # pylint: disable=R0914
    server_url: str,
    private_token: str,
    project_id: str,
    branch_name: str,
    template_path: Path
) -> str:
    '''
    Generate changelog content.

    Parameters:
        server_url (str): GitLab server URL.
        private_token (str): GitLab private token.
        project_id (str): GitLab project ID.
        branch_name (str): Repository branch name.
        template_path (str): Changelog template path.

    Returns:
        str: Changelog content.
    '''

    client = gitlab.Gitlab(server_url, private_token)
    project = client.projects.get(project_id)

    try:
        tag = next(project.tags.list(iterator=True))  # type: ignore
        current_tag_name = tag.name
        updated_after = (
            dateutil.parser.parse(
                tag.commit['committed_date']) + timedelta(seconds=2)
        ).isoformat()
    except StopIteration:
        current_tag_name = 'v0.0.0'
        updated_after = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

    if current_tag_name.startswith('v'):
        current_version = current_tag_name[1:]
    else:
        current_version = current_tag_name

    features = ensure_merge_request_format(
        project.mergerequests.list(
            target_branch=branch_name,
            state='merged',
            labels='type::feature',
            updated_after=updated_after,
            iterator=True
        ),
        merged_after=updated_after
    )

    improvements = ensure_merge_request_format(
        project.mergerequests.list(
            target_branch=branch_name,
            state='merged',
            labels='type::improvement',
            updated_after=updated_after,
            iterator=True
        ),
        merged_after=updated_after
    )

    bug_fixes = ensure_merge_request_format(
        project.mergerequests.list(
            target_branch=branch_name,
            state='merged',
            labels='type::bugfix',
            updated_after=updated_after,
            iterator=True
        ),
        merged_after=updated_after
    )

    breaking_changes = ensure_merge_request_format(
        project.mergerequests.list(
            target_branch=branch_name,
            state='merged',
            labels='breakingchange',
            updated_after=updated_after,
            iterator=True
        ),
        merged_after=updated_after
    )

    if len(features) + len(improvements) + len(bug_fixes) == 0:
        if project.description.endswith('.'):
            note = project.description[:-1]
        else:
            note = project.description

        features.append(note)
        breaking_changes.append(note)

    parsed_current_version = semver.Version.parse(current_version)

    if len(breaking_changes) > 0:
        parsed_version = parsed_current_version.bump_major()
    elif len(features) > 0:
        parsed_version = parsed_current_version.bump_minor()
    else:
        parsed_version = parsed_current_version.bump_patch()

    if current_tag_name.startswith('v'):
        tag_name = f'v{parsed_version}'
    else:
        tag_name = str(parsed_version)

    tag_url = f'{project.web_url}/-/tags/{tag_name}'
    tag_timestamp = datetime.utcnow()

    with open(template_path, mode='r', encoding='utf-8') as file:
        source = file.read()

    return Template(
        source,
        trim_blocks=True,
        lstrip_blocks=True
    ).render(
        tag_name=tag_name,
        tag_url=tag_url,
        tag_timestamp=tag_timestamp,
        features=features,
        improvements=improvements,
        bug_fixes=bug_fixes
    ).rstrip()


__all__ = [
    'generate'
]
