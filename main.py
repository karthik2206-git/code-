import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QStatusBar, QInputDialog
from tabmanager import TabManager
from git_integration import GitManager
from recentfiles import RecentFilesManager
from themes import ThemeManager

class CodePlusPlus(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("code++")
        self.setGeometry(100, 100, 900, 700)

        self.tabs = TabManager(self)
        self.setCentralWidget(self.tabs)

        self.git = GitManager()
        self.recent_files = RecentFilesManager(self)
        self.theme = ThemeManager(self)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self._create_menu()
        self._setup_shortcuts()
        self.theme.apply_theme('light')

    # --- Menu Creation ---
    def _create_menu(self):
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self._make_action("New", self.file_new, "Ctrl+N"))
        file_menu.addAction(self._make_action("Open...", self.file_open, "Ctrl+O"))
        file_menu.addAction(self._make_action("Save", self.file_save, "Ctrl+S"))
        file_menu.addAction(self._make_action("Save As...", self.file_saveas, "Ctrl+Shift+S"))
        file_menu.addAction(self._make_action("Close", self.file_close, "Ctrl+W"))
        file_menu.addSeparator()
        file_menu.addAction(self._make_action("Exit", self.close, "Ctrl+Q"))

        # Edit
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self._make_action("Undo", self.edit_undo, "Ctrl+Z"))
        edit_menu.addAction(self._make_action("Redo", self.edit_redo, "Ctrl+Y"))
        edit_menu.addSeparator()
        edit_menu.addAction(self._make_action("Cut", self.edit_cut, "Ctrl+X"))
        edit_menu.addAction(self._make_action("Copy", self.edit_copy, "Ctrl+C"))
        edit_menu.addAction(self._make_action("Paste", self.edit_paste, "Ctrl+V"))
        edit_menu.addAction(self._make_action("Select All", self.edit_selectall, "Ctrl+A"))

        # Search
        search_menu = menubar.addMenu("Search")
        search_menu.addAction(self._make_action("Find", self.search_find, "Ctrl+F"))
        search_menu.addAction(self._make_action("Replace", self.search_replace, "Ctrl+H"))

        # View
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self._make_action("Toggle Line Numbers", self.view_toggle_line_numbers))
        view_menu.addAction(self._make_action("Toggle Word Wrap", self.view_toggle_word_wrap))

        # Git
        git_menu = menubar.addMenu("Git")
        git_menu.addAction(self._make_action("Status", self.git_status))
        git_menu.addAction(self._make_action("Commit", self.git_commit))
        git_menu.addAction(self._make_action("Push", self.git_push))
        git_menu.addAction(self._make_action("Pull", self.git_pull))
        git_menu.addAction(self._make_action("Log", self.git_log))

        # Settings
        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction(self._make_action("Preferences", self.settings_preferences))
        settings_menu.addAction(self._make_action("Theme", self.settings_theme))

        # Plugins
        plugins_menu = menubar.addMenu("Plugins")
        plugins_menu.addAction(self._make_action("Manage Plugins", self.plugins_manage))

        # Help
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(self._make_action("About", self.help_about))

    def _make_action(self, name, slot, shortcut=None):
        act = QAction(name, self)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(slot)
        return act

    def _setup_shortcuts(self):
        # Most shortcuts are set in _make_action, but you can add more here if needed
        pass

    # --- Utility ---
    def current_editor(self):
        return self.tabs.currentWidget() if self.tabs.count() else None

    def show_status(self, message, timeout=2000):
        self.statusbar.showMessage(message, timeout)

    # --- File Menu Actions ---
    def file_new(self):
        self.tabs.new_tab()
        self.show_status("New file created.")

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                editor = self.tabs.new_tab(filename=os.path.basename(path), text=text)
                editor.file_path = path
                self.recent_files.add_file(path)
                self.show_status(f"Opened {path}")
            except Exception as e:
                QMessageBox.critical(self, "Open Error", str(e))

    def file_save(self):
        editor = self.current_editor()
        if not editor:
            return
        path = getattr(editor, 'file_path', None)
        if not path:
            return self.file_saveas()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(editor.text())
            self.show_status(f"Saved {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def file_saveas(self):
        editor = self.current_editor()
        if not editor:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.text())
                editor.file_path = path
                self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))
                self.recent_files.add_file(path)
                self.show_status(f"Saved as {path}")
            except Exception as e:
                QMessageBox.critical(self, "Save As Error", str(e))

    def file_close(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.tabs.removeTab(idx)
            self.show_status("Tab closed.")

    # --- Edit Menu Actions ---
    def edit_undo(self):
        editor = self.current_editor()
        if editor:
            editor.undo()

    def edit_redo(self):
        editor = self.current_editor()
        if editor:
            editor.redo()

    def edit_cut(self):
        editor = self.current_editor()
        if editor:
            editor.cut()

    def edit_copy(self):
        editor = self.current_editor()
        if editor:
            editor.copy()

    def edit_paste(self):
        editor = self.current_editor()
        if editor:
            editor.paste()

    def edit_selectall(self):
        editor = self.current_editor()
        if editor:
            editor.selectAll()

    # --- Search Menu Actions ---
    def search_find(self):
        editor = self.current_editor()
        if not editor:
            return
        text, ok = QInputDialog.getText(self, "Find", "Find:")
        if ok and text:
            editor.findFirst(text, False, False, False, True)  # for QScintilla

    def search_replace(self):
        editor = self.current_editor()
        if not editor:
            return
        find_text, ok = QInputDialog.getText(self, "Replace", "Find:")
        if ok and find_text:
            replace_text, ok2 = QInputDialog.getText(self, "Replace", "Replace with:")
            if ok2:
                # QScintilla does not have direct replace all, so a simple implementation:
                content = editor.text()
                new_content = content.replace(find_text, replace_text)
                editor.setText(new_content)
                self.show_status(f"Replaced all '{find_text}' with '{replace_text}'")

    # --- View Menu Actions ---
    def view_toggle_line_numbers(self):
        editor = self.current_editor()
        if editor:
            show = not editor.marginLineNumbers(1)
            editor.setMarginLineNumbers(1, show)
            self.show_status("Toggled line numbers.")

    def view_toggle_word_wrap(self):
        editor = self.current_editor()
        if editor:
            wrap = not editor.wordWrap()
            editor.setWordWrap(wrap)
            self.show_status("Toggled word wrap.")

    # --- Git Menu Actions ---
    def git_status(self):
        status = self.git.status()
        QMessageBox.information(self, "Git Status", status)

    def git_commit(self):
        msg, ok = QInputDialog.getText(self, "Git Commit", "Commit message:")
        if ok and msg:
            out = self.git.commit(msg)
            QMessageBox.information(self, "Git Commit", out)

    def git_push(self):
        out = self.git.push()
        QMessageBox.information(self, "Git Push", out)

    def git_pull(self):
        out = self.git.pull()
        QMessageBox.information(self, "Git Pull", out)

    def git_log(self):
        out = self.git.log()
        QMessageBox.information(self, "Git Log", out)

    # --- Settings Menu Actions ---
    def settings_preferences(self):
        QMessageBox.information(self, "Preferences", "Preferences dialog would appear here.")

    def settings_theme(self):
        theme, ok = QInputDialog.getItem(self, "Theme", "Select theme:", ["light", "dark"], editable=False)
        if ok:
            self.theme.apply_theme(theme)
            self.show_status(f"Theme set to {theme}")

    # --- Plugins Menu Actions ---
    def plugins_manage(self):
        QMessageBox.information(self, "Plugins", "Plugin manager would appear here.")

    # --- Help Menu Actions ---
    def help_about(self):
        QMessageBox.about(self, "About codeplusplus", "codeplusplus\nA modern, extensible text/code editor.\n(c) 2025")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodePlusPlus()
    window.show()
    sys.exit(app.exec())