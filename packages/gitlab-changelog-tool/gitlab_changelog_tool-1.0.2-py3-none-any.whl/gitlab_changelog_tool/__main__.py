'''
Package entrypoint.
'''

from gitlab_changelog_tool.cli import cli

if __name__ == '__main__':
    cli(obj={})  # pylint: disable=E1120
