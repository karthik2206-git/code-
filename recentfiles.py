class RecentFilesManager:
    def __init__(self, parent=None, max_files=10):
        self.recent_files = []
        self.max_files = max_files

    def add_file(self, filename):
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        self.recent_files.insert(0, filename)
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[:self.max_files]