import shlex
import subprocess


class Git:
    def __init__(self, capture_stdout: bool = False):
        """If `capture_stdout` is `True`, all functions will return their generated `stdout` as a string.
        Otherwise, the functions return the call's exit code."""
        self.capture_stdout = capture_stdout

    @property
    def capture_stdout(self) -> bool:
        """If `True`, member functions will return the generated `stdout` as a string,
        otherwise they return the command's exit code."""
        return self._capture_stdout

    @capture_stdout.setter
    def capture_stdout(self, should_capture: bool):
        self._capture_stdout = should_capture

    def _run(self, args: list[str]) -> str | int:
        if self._capture_stdout:
            return subprocess.run(args, stdout=subprocess.PIPE, text=True).stdout
        else:
            return subprocess.run(args).returncode

    def execute(self, command: str) -> str | int:
        """Execute git command.

        Equivalent to executing `git {command}` in the shell."""
        args = ["git"] + shlex.split(command)
        return self._run(args)

    def new_repo(self) -> str | int:
        """Executes `git init -b main`."""
        return self.execute("init -b main")

    def loggy(self) -> str | int:
        """Equivalent to `git log --oneline --name-only --abbrev-commit --graph`."""
        return self.execute("log --oneline --name-only --abbrev-commit --graph")

    def status(self) -> str | int:
        """Execute `git status`."""
        return self.execute("status")

    # ======================================Staging/Committing======================================
    def commit(self, args: str) -> str | int:
        """>>> git commit {args}"""
        return self.execute(f"commit {args}")

    def add(self, files: list[str] | None = None) -> str | int:
        """Stage a list of files.

        If no files are given (`files=None`), all files will be staged."""
        if not files:
            return self.execute("add .")
        else:
            files = " ".join(f'"{file}"' for file in files)  # type: ignore
            return self.execute(f"add {files}")

    def commit_files(self, files: list[str], message: str) -> str | int:
        """Stage and commit a list of files with commit message `message`."""
        return self.add(files) + self.commit(f'-m "{message}"')  # type: ignore

    def initcommit(self) -> str | int:
        """Equivalent to
        >>> git add .
        >>> git commit -m "Initial commit" """
        return self.add() + self.commit('-m "Initial commit"')  # type: ignore

    def amend(self, files: list[str] | None = None) -> str | int:
        """Stage and commit changes to the previous commit.

        If `files` is `None`, all files will be staged.

        Equivalent to:
        >>> git add {files}
        >>> git commit --amend --no-edit
        """
        return self.add(files) + self.commit("--amend --no-edit")  # type: ignore

    def tag(self, args: str = "") -> str | int:
        """Execute the `tag` command with `args`.

        e.g.

        `self.tag("--sort=-committerdate")`

        will list all the tags for this repository in descending commit date."""
        return self.execute(f"tag {args}")

    # ==========================================Push/Pull==========================================
    def add_remote_url(self, url: str, name: str = "origin") -> str | int:
        """Add remote url to repo."""
        return self.execute(f"remote add {name} {url}")

    def push(self, args: str = "") -> str | int:
        """Equivalent to `git push {args}`."""
        return self.execute(f"push {args}")

    def pull(self, args: str = "") -> str | int:
        """Equivalent to `git pull {args}`."""
        return self.execute(f"pull {args}")

    def push_new_branch(self, branch: str) -> str | int:
        """Push a new branch to origin with tracking.

        Equivalent to `git push -u origin {branch}`."""
        return self.push(f"-u origin {branch}")

    def pull_branch(self, branch: str) -> str | int:
        """Pull `branch` from origin."""
        return self.pull(f"origin {branch}")

    # ============================================Checkout/Branches============================================
    def branch(self, args: str) -> str | int:
        """Equivalent to `git branch {args}`."""
        return self.execute(f"branch {args}")

    def list_branches(self) -> str | int:
        """Print a list of branches."""
        return self.branch("-vva")

    def checkout(self, args: str) -> str | int:
        """Equivalent to `git checkout {args}`."""
        return self.execute(f"checkout {args}")

    def switch_branch(self, branch_name: str) -> str | int:
        """Switch to the branch specified by `branch_name`.

        Equivalent to `git checkout {branch_name}`."""
        return self.checkout(branch_name)

    def create_new_branch(self, branch_name: str) -> str | int:
        """Create and switch to a new branch named with `branch_name`.

        Equivalent to `git checkout -b {branch_name} --track`."""
        return self.checkout(f"-b {branch_name} --track")

    def delete_branch(self, branch_name: str, local_only: bool = True) -> str | int:
        """Delete `branch_name` from repo.

        #### :params:

        `local_only`: Only delete the local copy of `branch`, otherwise also delete the remote branch on origin and remote-tracking branch."""
        output = self.branch(f"--delete {branch_name}")
        if not local_only:
            return output + self.push(f"origin --delete {branch_name}")  # type:ignore
        return output

    def undo(self) -> str | int:
        """Undo uncommitted changes.

        Equivalent to `git checkout .`."""
        return self.checkout(".")

    def merge(self, branch_name: str) -> str | int:
        """Merge branch `branch_name` with currently active branch."""
        return self.execute(f"merge {branch_name}")

    # ===============================Requires GitHub CLI to be installed and configured===============================

    def create_remote(self, name: str, public: bool = False) -> str | int:
        """Uses GitHub CLI (must be installed and configured) to create a remote GitHub repo.

        #### :params:

        `name`: The name for the repo.

        `public`: Set to `True` to create the repo as public, otherwise it'll be created as private."""
        visibility = "--public" if public else "--private"
        return self._run(["gh", "repo", "create", name, visibility])

    def create_remote_from_cwd(self, public: bool = False) -> str | int:
        """Use GitHub CLI (must be installed and configured) to create a remote GitHub repo from
        the current working directory repo and add its url as this repo's remote origin.

        #### :params:

        `public`: Create the GitHub repo as a public repo, default is to create it as private."""
        visibility = "public" if public else "private"
        return self._run(
            ["gh", "repo", "create", "--source", ".", f"--{visibility}", "--push"]
        )

    def _change_visibility(self, owner: str, name: str, visibility: str) -> str | int:
        return self._run(
            ["gh", "repo", "edit", f"{owner}/{name}", "--visibility", visibility]
        )

    def make_private(self, owner: str, name: str) -> str | int:
        """Uses GitHub CLI (must be installed and configured) to set the repo's visibility to private.

        #### :params:

        `owner`: The repo owner.

        `name`: The name of the repo to edit."""
        return self._change_visibility(owner, name, "private")

    def make_public(self, owner: str, name: str) -> str | int:
        """Uses GitHub CLI (must be installed and configured) to set the repo's visibility to public.

        #### :params:

        `owner`: The repo owner.

        `name`: The name of the repo to edit."""
        return self._change_visibility(owner, name, "public")

    def delete_remote(self, owner: str, name: str) -> str | int:
        """Uses GitHub CLI (must be isntalled and configured) to delete the remote for this repo.

        #### :params:

        `owner`: The repo owner.

        `name`: The name of the remote repo to delete."""
        return self._run(["gh", "repo", "delete", f"{owner}/{name}", "--yes"])
