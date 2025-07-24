import git

class GitManager:
    """
    Enhanced GitManager for handling git operations in a safe way.
    All methods return strings (or lists), and never raise exceptions.
    """

    def __init__(self, repo_path='.'):
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except Exception as e:
            self.repo = None
            self._last_error = str(e)

    def is_repo(self):
        """Return True if this folder is a git repository."""
        return self.repo is not None

    def init(self):
        """Initialize a new git repository if one does not exist."""
        if not self.repo:
            try:
                self.repo = git.Repo.init(self.repo_path)
                return "Initialized new git repository."
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Repository already exists."

    def status(self):
        """Return status of current git repo."""
        if not self.repo:
            return "Not a git repo"
        try:
            return self.repo.git.status()
        except Exception as e:
            return f"Git error: {getattr(e, 'stderr', str(e))}"

    def add(self, path=None):
        """Stage files. If path is None, stage all."""
        if not self.repo:
            return "Not a git repo"
        try:
            if path:
                return self.repo.git.add(path)
            else:
                return self.repo.git.add('--all')
        except Exception as e:
            return f"Git error: {str(e)}"

    def commit(self, message):
        """Commit staged changes with message."""
        if self.repo:
            try:
                self.repo.git.add('--all')
                return self.repo.git.commit('-m', message)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def pull(self):
        """Pull latest changes from remote."""
        if self.repo:
            try:
                return self.repo.git.pull()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def push(self):
        """Push changes to remote."""
        if self.repo:
            try:
                return self.repo.git.push()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def fetch(self):
        """Fetch latest updates from remote."""
        if self.repo:
            try:
                return self.repo.git.fetch()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def log(self, n=30):
        """Show commit log."""
        if self.repo:
            try:
                return self.repo.git.log(f'--oneline', f'-n{n}')
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def branch(self):
        """List branches."""
        if self.repo:
            try:
                return self.repo.git.branch()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def checkout(self, branch_name):
        """Switch to another branch."""
        if self.repo:
            try:
                return self.repo.git.checkout(branch_name)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def create_branch(self, branch_name):
        """Create and switch to a new branch."""
        if self.repo:
            try:
                return self.repo.git.checkout('-b', branch_name)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def diff(self, a=None, b=None):
        """Show diff in working dir or between two commits/branches."""
        if self.repo:
            try:
                if a and b:
                    return self.repo.git.diff(f"{a}..{b}")
                else:
                    return self.repo.git.diff()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def remotes(self):
        """List remote URLs."""
        if self.repo:
            try:
                return [remote.url for remote in self.repo.remotes]
            except Exception as e:
                return [f"Git error: {str(e)}"]
        return []

    def set_remote(self, name, url):
        """Create or set a remote."""
        if self.repo:
            try:
                if name in self.repo.remotes:
                    self.repo.delete_remote(name)
                self.repo.create_remote(name, url)
                return f"Remote '{name}' set to {url}"
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def current_branch(self):
        """Get the current branch name."""
        if self.repo:
            try:
                return self.repo.active_branch.name
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def reset(self, path=None):
        """Unstage files or reset repo."""
        if self.repo:
            try:
                if path:
                    return self.repo.git.reset(path)
                else:
                    return self.repo.git.reset()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def tags(self):
        """List tags."""
        if self.repo:
            try:
                return self.repo.git.tag()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def create_tag(self, tag_name, message=""):
        """Create a new tag, optionally with a message."""
        if self.repo:
            try:
                return self.repo.create_tag(tag_name, message=message)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def delete_tag(self, tag_name):
        """Delete a tag by name."""
        if self.repo:
            try:
                return self.repo.git.tag('-d', tag_name)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def stash(self):
        """Stash changes."""
        if self.repo:
            try:
                return self.repo.git.stash()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def stash_pop(self):
        """Apply the latest stashed changes."""
        if self.repo:
            try:
                return self.repo.git.stash('pop')
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def last_commit(self):
        """Show details of last commit."""
        if self.repo:
            try:
                commit = self.repo.head.commit
                return f"{commit.hexsha[:7]} - {commit.message.strip()} (by {commit.author.name})"
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def blame(self, file_path):
        """Show who last edited each line of a file."""
        if self.repo:
            try:
                return self.repo.git.blame(file_path)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def fetch(self):
        """Fetch updates from remote."""
        if self.repo:
            try:
                return self.repo.git.fetch()
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def cherry_pick(self, commit_hash):
        """Apply changes from a specific commit."""
        if self.repo:
            try:
                return self.repo.git.cherry_pick(commit_hash)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"

    def revert(self, commit_hash):
        """Revert a specific commit."""
        if self.repo:
            try:
                return self.repo.git.revert(commit_hash)
            except Exception as e:
                return f"Git error: {str(e)}"
        return "Not a git repo"
