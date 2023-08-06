'''
Command-line application package.
'''

from pathlib import Path

import click

from . import api


@click.group(help='Automatically generate changelogs from merge requests on GitLab.')
@click.option(
    '--server-url', envvar='CI_SERVER_URL', type=str, required=True,
    help='GitLab server URL.'
)
@click.option(
    '--private-token', envvar='GITLAB_ACCESS_TOKEN', type=str, required=True,
    help='GitLab private token.'
)
@click.option(
    '--project-id', envvar='CI_PROJECT_ID', type=str, required=True,
    help='GitLab project ID.'
)
@click.option(
    '--branch-name', type=str, default='main',
    help='Repository branch name.'
)
@click.option(
    '--template-path',
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    default=Path(__file__).parent / 'templates' / 'CHANGELOG.md',
    help='Changelog template path.'
)
@click.pass_context
def cli(  # pylint: disable=R0913
    ctx: click.Context,
    server_url: str,
    private_token: str,
    project_id: str,
    branch_name: str,
    template_path: Path
):
    '''
    Initialize common command-line application options.

    Parameters:
        ctx (click.Context): Command-line application context.
        server_url (str): GitLab server URL.
        private_token (str): GitLab private token.
        project_id (str): GitLab project ID.
        branch_name (str): Repository branch name.
        template_path (str): Changelog template path.
    '''

    ctx.ensure_object(dict)

    ctx.obj['server_url'] = server_url
    ctx.obj['private_token'] = private_token
    ctx.obj['project_id'] = project_id
    ctx.obj['branch_name'] = branch_name
    ctx.obj['template_path'] = template_path


@cli.command(help='Generate changelog content.')
@click.pass_context
def generate(ctx: click.Context):
    '''
    Generate changelog content.

    Parameters:
        ctx (click.Context): Command-line application context.
    '''

    click.echo(api.generate(**ctx.obj))


__all__ = [
    'cli'
]
