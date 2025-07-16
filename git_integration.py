import git

class GitManager:
    def __init__(self, repo_path='.'):
        try:
            self.repo = git.Repo(repo_path)
        except Exception:
            self.repo = None

    def status(self):
        if not self.repo:
            return "Not a git repo"
        return self.repo.git.status()

    def commit(self, message):
        if self.repo:
            self.repo.git.add('--all')
            return self.repo.git.commit('-m', message)

    def pull(self):
        if self.repo:
            return self.repo.git.pull()

    def push(self):
        if self.repo:
            return self.repo.git.push()

    def log(self):
        if self.repo:
            return self.repo.git.log('--oneline')

    def branch(self):
        if self.repo:
            return self.repo.git.branch()