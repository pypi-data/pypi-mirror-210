import os

from argshell import ArgShell, ArgShellParser, Namespace, with_parser
from pathier import Pathier

from gitbetter import Git


def new_remote_parser() -> ArgShellParser:
    parser = ArgShellParser()
    parser.add_argument(
        "--public",
        action="store_true",
        help=""" Set the new remote visibility as public. Defaults to private. """,
    )
    return parser


def commit_files_parser() -> ArgShellParser:
    parser = ArgShellParser()
    parser.add_argument(
        "files", type=str, nargs="*", help=""" List of files to stage and commit. """
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        required=True,
        help=""" The commit message to use. """,
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=""" If a file name is not found in the current working directory,
        search for it in subfolders. This avoids having to type paths to files in subfolders,
        but if you have multiple files in different subfolders with the same name that have changes they
        will all be staged and committed.""",
    )
    return parser


def amend_files_parser() -> ArgShellParser:
    parser = ArgShellParser()
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs="*",
        help=""" List of files to stage and commit. """,
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=""" If a file name is not found in the current working directory,
        search for it in subfolders. This avoids having to type paths to files in subfolders,
        but if you have multiple files in different subfolders with the same name that have changes they
        will all be staged and committed.""",
    )
    return parser


def delete_branch_parser() -> ArgShellParser:
    parser = ArgShellParser()
    parser.add_argument(
        "branch", type=str, help=""" The name of the branch to delete. """
    )
    parser.add_argument(
        "-r",
        "--remote",
        action="store_true",
        help=""" Delete the remote and remote-tracking branches along with the local branch.
        By default only the local branch is deleted.""",
    )
    return parser


def recurse_files(filenames: list[str]) -> list[str]:
    files = []
    for filename in filenames:
        if not Pathier(filename).exists():
            results = list(Pathier.cwd().rglob(f"{filename}"))
            if not results:
                print(f"WARNING: Could not find any files with name {filename}")
            else:
                files.extend([str(result) for result in results])
        else:
            files.append(filename)
    return files


def files_postparser(args: Namespace) -> Namespace:
    if args.recursive:
        args.files = recurse_files(args.files)
    return args


class GitBetter(ArgShell):
    """GitBetter Shell."""

    intro = "Starting gitbetter...\nEnter 'help' or '?' for command help."
    prompt = f"gitbetter::{Pathier.cwd()}>"
    execute_in_terminal_if_unrecognized = True
    git = Git()

    def default(self, line: str):
        if self.execute_in_terminal_if_unrecognized:
            os.system(line)
        else:
            super().default(line)

    def do_help(self, arg: str):
        """List available commands with "help" or detailed help with "help cmd"."""
        super().do_help(arg)
        if not arg:
            print(self.unrecognized_command_behavior_status)
            if self.execute_in_terminal_if_unrecognized:
                print(
                    "^Essentially makes this shell function as a super-shell of whatever shell you launched gitbetter from.^"
                )
        print()

    @property
    def unrecognized_command_behavior_status(self):
        return f"Unrecognized command behavior: {'Execute in shell with os.system()' if self.execute_in_terminal_if_unrecognized else 'Print unknown syntax error'}"

    def do_toggle_unrecognized_command_behavior(self, arg: str):
        """Toggle whether the shell will attempt to execute unrecognized commands as system commands in the terminal.
        When on (the default), `GitBetter` will treat unrecognized commands as if you added the `sys` command in front of the input, i.e. `os.system(your_input)`.
        When off, an `unknown syntax` message will be printed and no commands will be executed."""
        self.execute_in_terminal_if_unrecognized = (
            not self.execute_in_terminal_if_unrecognized
        )
        print(self.unrecognized_command_behavior_status)

    def do_cd(self, path: str):
        """Change current working directory to `path`."""
        os.chdir(path)
        self.prompt = f"gitbetter::{Pathier.cwd()}>"

    def do_git(self, arg: str):
        """Directly execute `git {arg}`.

        i.e. You can still do everything directly invoking git can do."""
        self.git.execute(arg)

    def do_new_repo(self, _: str):
        """Create a new git repo in this directory."""
        self.git.new_repo()

    def do_new_branch(self, name: str):
        """Create and switch to a new branch named after the supplied arg."""
        self.git.create_new_branch(name)

    @with_parser(new_remote_parser)
    def do_new_gh_remote(self, args: Namespace):
        """Create a remote GitHub repository for this repo.

        GitHub CLI must be installed and configured for this to work."""
        self.git.create_remote_from_cwd(args.public)

    def do_initcommit(self, _: str):
        """Stage and commit all files with message "Initial Commit"."""
        self.git.initcommit()

    def do_undo(self, _: str):
        """Undo all uncommitted changes."""
        self.git.undo()

    @with_parser(amend_files_parser, [files_postparser])
    def do_add(self, args: Namespace):
        """Stage a list of files.
        If no files are given, all files will be added."""
        self.git.add(None if not args.files else args.files)

    def do_commit(self, args: str):
        """Commit staged files with provided `args` string."""
        self.git.commit(args)

    @with_parser(commit_files_parser, [files_postparser])
    def do_commitf(self, args: Namespace):
        """Stage and commit a list of files."""
        self.git.commit_files(args.files, args.message)

    def do_commitall(self, message: str):
        """Stage and commit all files with this message."""
        if not message.startswith('"'):
            message = '"' + message
        if not message.endswith('"'):
            message += '"'
        self.git.add()
        self.git.commit(f"-m {message}")

    def do_switch(self, branch_name: str):
        """Switch to this branch."""
        self.git.switch_branch(branch_name)

    def do_add_url(self, url: str):
        """Add remote origin url for repo and push repo."""
        self.git.add_remote_url(url)
        self.git.push("-u origin main")

    def do_push_new(self, branch_name: str):
        """Push this new branch to origin with -u flag."""
        self.git.push_new_branch(branch_name)

    def do_push(self, args: str):
        """Execute `git push`.

        `args` can be any additional args that `git push` accepts."""
        self.git.push(args)

    def do_pull(self, args: str):
        """Execute `git pull`.

        `args` can be any additional args that `git pull` accepts."""
        self.git.pull(args)

    def do_branches(self, _: str):
        """Show local and remote branches."""
        self.git.list_branches()

    def do_loggy(self, _: str):
        """Execute `git --oneline --name-only --abbrev-commit --graph`."""
        self.git.loggy()

    def do_status(self, _: str):
        """Execute `git status`."""
        self.git.status()

    def do_merge(self, branch_name: str):
        """Merge supplied `branch_name` with the currently active branch."""
        self.git.merge(branch_name)

    def do_tag(self, tag_id: str):
        """Tag current commit with `tag_id`."""
        self.git.tag(tag_id)

    @with_parser(amend_files_parser, [files_postparser])
    def do_amend(self, args: Namespace):
        """Stage files and add to previous commit."""
        self.git.amend(args.files)

    @with_parser(delete_branch_parser)
    def do_delete_branch(self, args: Namespace):
        """Delete branch."""
        self.git.delete_branch(args.branch, not args.remote)

    def do_pull_branch(self, branch: str):
        """Pull this branch from the origin."""
        self.git.pull_branch(branch)

    def do_ignore(self, patterns: str):
        """Add the list of patterns to `.gitignore`."""
        patterns = "\n".join(patterns.split())
        path = Pathier(".gitignore")
        path.append("\n")
        path.append(patterns, False)

    def do_make_private(self, owner: str):
        """Make the GitHub remote for this repo private.

        Expects an argument for the repo owner, i.e. the `OWNER` in `github.com/{OWNER}/{repo-name}`

        This repo must exist and GitHub CLI must be installed and configured."""
        self.git.make_private(owner, Pathier.cwd().stem)

    def do_make_public(self, owner: str):
        """Make the GitHub remote for this repo public.

        Expects an argument for the repo owner, i.e. the `OWNER` in `github.com/{OWNER}/{repo-name}`

        This repo must exist and GitHub CLI must be installed and configured."""
        self.git.make_public(owner, Pathier.cwd().stem)

    def do_delete_gh_repo(self, owner: str):
        """Delete this repo from GitHub.

        Expects an argument for the repo owner, i.e. the `OWNER` in `github.com/{OWNER}/{repo-name}`

        GitHub CLI must be installed and configured.

        May require you to reauthorize and rerun command."""
        self.git.delete_remote(owner, Pathier.cwd().stem)


def main():
    GitBetter().cmdloop()


if __name__ == "__main__":
    main()
