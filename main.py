import sys
import os
import chardet
import git

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QMessageBox, QStatusBar,
    QInputDialog, QSplitter, QTreeView, QFileSystemModel, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMenu 

from tabmanager import TabManager
from git_integration import GitManager
from recentfiles import RecentFilesManager
from themes import ThemeManager


class CodePlusPlus(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("code++")
        self.setGeometry(100, 100, 900, 700)

        # Set window icon (top left in title bar)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        self.setWindowIcon(QIcon(logo_path))

        # --- Header with logo and app name ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("[Logo]")
        logo_label.setFixedSize(40, 40)
        logo_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(logo_label)

        # App name
        app_name_label = QLabel("code++")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        app_name_label.setFont(font)
        app_name_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header_layout.addWidget(app_name_label)

        # --- Main UI ---
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        container_layout.addWidget(header_widget)

        # Main splitter for file tree and editor tabs
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # --- File tree view area ---
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(
            QtCore.QDir.AllDirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Hidden
        )
        self.file_model.setRootPath('')
        self.file_model.setRootPath('')  # Set when folder opened

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIsDecorated(True)
        self.file_tree.hide()  # Hidden by default

        self.settings = QSettings("codeplusplus", "main")
        last_folder = self.settings.value("last_folder", "")
        if last_folder:
            self.file_model.setRootPath(last_folder)
            self.file_tree.setRootIndex(self.file_model.index(last_folder))
            self.file_tree.show()
            
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.on_tree_context_menu)

        # Connect double-click to opening files in the editor
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)

        # Add the file tree to the splitter
        self.splitter.addWidget(self.file_tree)
        self.file_tree.setMaximumWidth(350)  # Set as needed

        # Initialize workspace folder
        self.workspace_folder = None
        
        # Status bar for displaying messages
        self.status_encoding_label = None
        self.status_encoding_label = QLabel("UTF-8 | CRLF")
        self.statusBar().addPermanentWidget(self.status_encoding_label)
        
        # --- Editor tab area ---
        self.tabs = TabManager(self)
        self.splitter.addWidget(self.tabs)

        self.git = GitManager()
        self.recent_files = RecentFilesManager(self)
        self.theme = ThemeManager(
            window=self,
            editor_getter=self.get_all_editor_widgets,
            file_tree=self.file_tree
        )

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self._create_menu()
        self._setup_shortcuts()
        self.theme.apply_theme('light')

    def get_all_editor_widgets(self):
        # Assumes self.tabs.tab_widgets is a list of editor widgets,
        # or that self.tabs provides a method to get all editor widgets.
        # Adjust as needed for your TabManager implementation!
        editors = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if editor:
                editors.append(editor)
        return editors

    # --- Menu Creation ---
    def _create_menu(self):
        menubar = self.menuBar()
        # File
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self._make_action("New", self.file_new, "Ctrl+N"))
        #Open File and Folder Sub-menu
        file_menu.addAction(self._make_action("Open...", self.file_open, "Ctrl+O"))
        open_file_action = QAction("Open File...", self)
        open_file_action.triggered.connect(self.file_open_file)
        open_folder_action = QAction("Open Folder...", self)
        open_folder_action.triggered.connect(self.file_open_folder)
        file_menu.addAction(open_file_action)
        file_menu.addAction(open_folder_action)
        close_folder_action = QAction("Close Folder", self)
        close_folder_action.triggered.connect(self.file_close_folder)
        file_menu.addAction(close_folder_action)       
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
        self.show_hidden_files_action = QAction("Show Hidden Files", self)
        self.show_hidden_files_action.setCheckable(True)
        self.show_hidden_files_action.setChecked(True)  # Default: show hidden files
        self.show_hidden_files_action.triggered.connect(self.toggle_hidden_files)
        view_menu.addAction(self.show_hidden_files_action)
        view_menu.addAction(self._make_action("Toggle Line Numbers", self.view_toggle_line_numbers))
        view_menu.addAction(self._make_action("Toggle Word Wrap", self.view_toggle_word_wrap))

        # Git
        git_menu = menubar.addMenu("Git")
        git_menu.addAction(self._make_action("Clone", self.git_clone))
        git_menu.addAction(self._make_action("Status", self.git_status))
        git_menu.addAction(self._make_action("Commit", self.git_commit))
        git_menu.addAction(self._make_action("Push", self.git_push))
        git_menu.addAction(self._make_action("Pull", self.git_pull))
        git_menu.addAction(self._make_action("Log", self.git_log))
        
        # --- Advanced Git Submenu ---
        advanced_menu = git_menu.addMenu("Advanced")
        advanced_menu.addAction(self._make_action("Branch List", self.git_branch_list))
        advanced_menu.addAction(self._make_action("Checkout Branch", self.git_checkout_branch))
        advanced_menu.addAction(self._make_action("Create Branch", self.git_create_branch))
        advanced_menu.addAction(self._make_action("Diff", self.git_diff))
        advanced_menu.addAction(self._make_action("Add", self.git_add))
        advanced_menu.addAction(self._make_action("Reset", self.git_reset))
        advanced_menu.addAction(self._make_action("Tags List", self.git_tags_list))
        advanced_menu.addAction(self._make_action("Create Tag", self.git_create_tag))
        advanced_menu.addAction(self._make_action("Delete Tag", self.git_delete_tag))
        advanced_menu.addAction(self._make_action("Stash", self.git_stash))
        advanced_menu.addAction(self._make_action("Stash Pop", self.git_stash_pop))
        advanced_menu.addAction(self._make_action("Last Commit", self.git_last_commit))
        advanced_menu.addAction(self._make_action("Blame", self.git_blame))
        advanced_menu.addAction(self._make_action("Fetch", self.git_fetch))
        advanced_menu.addAction(self._make_action("Cherry-pick", self.git_cherry_pick))
        advanced_menu.addAction(self._make_action("Revert", self.git_revert))
        advanced_menu.addAction(self._make_action("Init Repo", self.git_init))
        advanced_menu.addAction(self._make_action("Set Remote", self.git_set_remote))
        advanced_menu.addAction(self._make_action("Show Remotes", self.git_show_remotes))
        advanced_menu.addAction(self._make_action("Show Current Branch", self.git_show_current_branch))   
        
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
    
    def ensure_status_encoding_label(self):
            label = getattr(self, "status_encoding_label", None)
            try:
                if label is not None and label.parent() is not None:
                    return label
            except RuntimeError:
                pass  # The label was deleted
            # Create new label and add to status bar
            label = QLabel("UTF-8 | CRLF")
            self.status_encoding_label = label
            self.statusBar().addPermanentWidget(label)
            return label

    def close_tabs_for_folder(self, folder_path):
        tabs_to_close = []
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            file_path = getattr(editor, 'file_path', None)
            if file_path and file_path.startswith(folder_path):
                tabs_to_close.append((i, editor))

        # Reverse order so closing tabs doesn't affect indices
        for i, editor in reversed(tabs_to_close):
            # Check for unsaved changes
            is_modified = False
            if hasattr(editor, "isModified"):
                is_modified = editor.isModified()
            elif hasattr(editor, "document") and hasattr(editor.document(), "isModified"):
                is_modified = editor.document().isModified()
            if is_modified:
                file_name = getattr(editor, "file_path", "Untitled")
                msg = QMessageBox(self)
                msg.setWindowTitle("Unsaved Changes")
                msg.setText(f"Save changes to {file_name}?")
                msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                ret = msg.exec_()
                if ret == QMessageBox.Save:
                    if hasattr(self, "file_save"):
                        self.file_save(editor)
                elif ret == QMessageBox.Discard:
                    pass
                elif ret == QMessageBox.Cancel:
                    break  # Stop closing further tabs
            # Close the tab
            self.tabs.removeTab(i)

    def update_status_bar(self):
        label = self.ensure_status_encoding_label()
        editor = self.current_editor() if hasattr(self, "current_editor") else None
        if not editor or not hasattr(editor, "file_path") or not editor.file_path:
            label.setText("UTF-8 | CRLF")
            return
        # Guess encoding
        try:
            with open(editor.file_path, "rb") as f:
                raw = f.read(4096)
                result = chardet.detect(raw)
                encoding = result.get("encoding", "UTF-8")
        except Exception:
            encoding = "UTF-8"
        # Detect line endings
        line_ending = "CRLF"  # default
        try:
            with open(editor.file_path, "rb") as f:
                data = f.read(4096)
                if b"\r\n" in data:
                    line_ending = "CRLF"
                elif b"\n" in data:
                    line_ending = "LF"
                elif b"\r" in data:
                    line_ending = "CR"
        except Exception:
            line_ending = "CRLF"
        label.setText(f"{encoding} | {line_ending}")

        
    def file_new(self):
        self.tabs.new_tab()
        editor = self.current_editor()  # or self.tabs.current_editor()
        self.theme.apply_editor_colors(editor, self.theme.current_theme)
        self.show_status("New file created.")
        self.update_status_bar()

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
                self.theme.apply_editor_colors(editor, self.theme.current_theme)
            except Exception as e:
                QMessageBox.critical(self, "Open Error", str(e))

    def file_open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if path:
            self.open_file_in_tab(path)
            self.update_status_bar()

    def file_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            if self.workspace_folder:
                self.close_tabs_for_folder(self.workspace_folder)
            self.workspace_folder = folder
            self.git = GitManager(folder)
            self.settings.setValue("last_folder", folder)
            self.file_model.setRootPath(folder)
            self.file_tree.setRootIndex(self.file_model.index(folder))
            self.file_tree.show()
            self.show_status(f"Opened folder: {folder}")

    def open_file_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.open_file_in_tab(path)
            editor = self.current_editor()  # Get the newly opened editor
            self.theme.apply_editor_colors(editor, self.theme.current_theme)

    def open_file_in_tab(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            editor = self.tabs.new_tab(filename=os.path.basename(path), text=text)
            editor.file_path = path
            self.recent_files.add_file(path)
            self.theme.apply_editor_colors(editor, self.theme.current_theme)
            self.show_status(f"Opened {path}")
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Open Error", str(e))

    def file_close_folder(self):
        if self.workspace_folder:
            self.close_tabs_for_folder(self.workspace_folder)
            self.workspace_folder = None
            self.git = None
        self.file_tree.hide()
        self.file_model.setRootPath('')
        self.show_status("Closed folder.")

    import re

    def normalize_crlf(self, text):
        # First, replace all CRLF with LF for a clean slate
        text = text.replace('\r\n', '\n')
        # Then, replace all LF with CRLF
        text = text.replace('\n', '\r\n')
        return text

    def file_save(self,editor):
            editor = self.current_editor()
            if not editor:
                return
            path = getattr(editor, 'file_path', None)
            if not path:
                return self.file_saveas()
            try:
                text = editor.text()
                text = self.normalize_crlf(text)  # <-- use self.normalize_crlf
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    f.write(text)
                self.show_status(f"Saved {path}")
                self.update_status_bar()
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

    def on_tree_context_menu(self, point):
        index = self.file_tree.indexAt(point)
        if not index.isValid():
            return
        menu = QMenu(self)
        new_file_action = menu.addAction("New File")
        new_folder_action = menu.addAction("New Folder")
        delete_action = menu.addAction("Delete")
        rename_action = menu.addAction("Rename")
        action = menu.exec_(self.file_tree.viewport().mapToGlobal(point))
        path = self.file_model.filePath(index)

        if action == new_file_action:
            self.create_new_file(path)
        elif action == new_folder_action:
            self.create_new_folder(path)
        elif action == delete_action:
            self.delete_file_or_folder(path)
        elif action == rename_action:
            self.rename_file_or_folder(path)

    def create_new_file(self, path):
        dir_path = path if os.path.isdir(path) else os.path.dirname(path)
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            file_path = os.path.join(dir_path, name)
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('')
                self.show_status(f"Created file: {file_path}")
            else:
                QMessageBox.warning(self, "File Exists", f"File {file_path} already exists.")

    def create_new_folder(self, path):
        dir_path = path if os.path.isdir(path) else os.path.dirname(path)
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            folder_path = os.path.join(dir_path, name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                self.show_status(f"Created folder: {folder_path}")
            else:
                QMessageBox.warning(self, "Folder Exists", f"Folder {folder_path} already exists.")

    def delete_file_or_folder(self, path):
        reply = QMessageBox.question(self, "Delete", f"Are you sure you want to delete '{path}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    import shutil
                    shutil.rmtree(path)
                self.show_status(f"Deleted: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", str(e))

    def rename_file_or_folder(self, path):
        name, ok = QInputDialog.getText(self, "Rename", "Enter new name:")
        if ok and name:
            new_path = os.path.join(os.path.dirname(path), name)
            try:
                os.rename(path, new_path)
                self.show_status(f"Renamed to: {new_path}")
            except Exception as e:
                QMessageBox.critical(self, "Rename Error", str(e))

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
            # QScintilla uses wrapMode() and setWrapMode()
            from PyQt5.Qsci import QsciScintilla
            current = editor.wrapMode() != QsciScintilla.WrapNone
            # Toggle: If wrapping is on, turn off; if off, turn on
            editor.setWrapMode(QsciScintilla.WrapNone if current else QsciScintilla.WrapWord)
            self.show_status("Toggled word wrap.")

    def toggle_hidden_files(self):
        show_hidden = self.show_hidden_files_action.isChecked()
        filter_flags = (
            QtCore.QDir.AllDirs |
            QtCore.QDir.Files |
            QtCore.QDir.NoDotAndDotDot
        )
        if show_hidden:
            filter_flags |= QtCore.QDir.Hidden
        self.file_model.setFilter(filter_flags)
        # Refresh view by resetting root path (to force update)
        root_path = self.file_model.rootPath()
        self.file_model.setRootPath("")
        self.file_model.setRootPath(root_path)

    # --- Git Menu Actions ---
    def get_workspace_repo(self):
        folder = getattr(self, 'workspace_folder', None)
        if not folder:
            QMessageBox.warning(self, "No Workspace", "No folder is currently opened as workspace.")
            return None
        git_dir = os.path.join(folder, ".git")
        if not os.path.isdir(git_dir):
            QMessageBox.warning(self, "Not a Git Repo", "This folder is not a git repository.")
            return None
        try:
            from git import Repo
            return Repo(folder)
        except Exception as e:
            QMessageBox.critical(self, "Git Error", str(e))
            return None
        
    def git_clone(self):
        # Ask for the repo URL
        repo_url, ok = QInputDialog.getText(self, "Git Clone", "Enter repository URL:")
        if not ok or not repo_url:
            return

        # Ask for destination folder
        dest_dir = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest_dir:
            return

        # Ask for username (optional)
        username, uok = QInputDialog.getText(self, "Git Authentication", "Username (leave blank for anonymous):")
        password = ""
        if uok and username:
            # Ask for password/token (masked)
            password, pok = QInputDialog.getText(self, "Git Authentication", "Password or Token:", QLineEdit.Password)
            if not pok:
                return

        # Prepare authenticated URL if needed
        if username and password:
            # Insert credentials into the URL (for HTTPS)
            import re
            repo_url = re.sub(r"^(https://)", r"\1{}:{}@".format(username, password), repo_url)

        # Perform the clone
        try:
            from git import Repo
            Repo.clone_from(repo_url, dest_dir)
            QMessageBox.information(self, "Git Clone", "Repository cloned successfully to:\n" + dest_dir)
        except Exception as e:
            QMessageBox.critical(self, "Git Clone Error", str(e))
            
    def git_status(self):
        if not self.git:
            self.show_status("No workspace or not a git repo.")
            return
        status = self.git.status()
        self.show_status(status)

    def git_commit(self):
        if not self.git:
            QMessageBox.warning(self, "Git Commit", "No workspace or not a git repo.")
            return
        msg, ok = QInputDialog.getText(self, "Git Commit", "Commit message:")
        if ok and msg:
            out = self.git.commit(msg)
            QMessageBox.information(self, "Git Commit", out)

    def git_push(self):
        if not self.git:
            QMessageBox.warning(self, "Git Push", "No workspace or not a git repo.")
            return
        out = self.git.push()
        QMessageBox.information(self, "Git Push", str(out))

    def git_pull(self):
        if not self.git:
            QMessageBox.warning(self, "Git Pull", "No workspace or not a git repo.")
            return
        out = self.git.pull()
        QMessageBox.information(self, "Git Pull", str(out))

    def git_log(self):
        if not self.git:
            QMessageBox.warning(self, "Git Log", "No workspace or not a git repo.")
            return
        out = self.git.log()
        QMessageBox.information(self, "Git Log", str(out))

    def git_branch_list(self):
        if not self.git:
            QMessageBox.warning(self, "Git Branches", "No workspace or not a git repo.")
            return
        out = self.git.branch()
        QMessageBox.information(self, "Git Branches", str(out))

    def git_checkout_branch(self):
        if not self.git:
            QMessageBox.warning(self, "Checkout Branch", "No workspace or not a git repo.")
            return
        branch, ok = QInputDialog.getText(self, "Checkout Branch", "Enter branch name:")
        if ok and branch:
            out = self.git.checkout(branch)
            QMessageBox.information(self, "Checkout Branch", str(out))

    def git_create_branch(self):
        if not self.git:
            QMessageBox.warning(self, "Create Branch", "No workspace or not a git repo.")
            return
        branch, ok = QInputDialog.getText(self, "Create Branch", "Enter new branch name:")
        if ok and branch:
            out = self.git.create_branch(branch)
            QMessageBox.information(self, "Create Branch", str(out))

    def git_diff(self):
        if not self.git:
            QMessageBox.warning(self, "Git Diff", "No workspace or not a git repo.")
            return
        a, ok_a = QInputDialog.getText(self, "Diff", "Enter first commit/branch (leave blank for working dir):")
        b, ok_b = QInputDialog.getText(self, "Diff", "Enter second commit/branch (optional):")
        out = self.git.diff(a if ok_a and a else None, b if ok_b and b else None)
        QMessageBox.information(self, "Git Diff", str(out))

    def git_add(self):
        if not self.git:
            QMessageBox.warning(self, "Git Add", "No workspace or not a git repo.")
            return
        path, ok = QInputDialog.getText(self, "Git Add", "Enter file path (leave blank for all):")
        out = self.git.add(path if ok and path else None)
        QMessageBox.information(self, "Git Add", str(out))

    def git_reset(self):
        if not self.git:
            QMessageBox.warning(self, "Git Reset", "No workspace or not a git repo.")
            return
        path, ok = QInputDialog.getText(self, "Git Reset", "Enter file path (leave blank for all):")
        out = self.git.reset(path if ok and path else None)
        QMessageBox.information(self, "Git Reset", str(out))

    def git_tags_list(self):
        if not self.git:
            QMessageBox.warning(self, "Tags List", "No workspace or not a git repo.")
            return
        out = self.git.tags()
        QMessageBox.information(self, "Git Tags", str(out))

    def git_create_tag(self):
        if not self.git:
            QMessageBox.warning(self, "Create Tag", "No workspace or not a git repo.")
            return
        tag, ok_tag = QInputDialog.getText(self, "Create Tag", "Enter tag name:")
        message, ok_msg = QInputDialog.getText(self, "Create Tag", "Enter tag message (optional):")
        if ok_tag and tag:
            out = self.git.create_tag(tag, message if ok_msg else "")
            QMessageBox.information(self, "Create Tag", str(out))

    def git_delete_tag(self):
        if not self.git:
            QMessageBox.warning(self, "Delete Tag", "No workspace or not a git repo.")
            return
        tag, ok = QInputDialog.getText(self, "Delete Tag", "Enter tag name to delete:")
        if ok and tag:
            out = self.git.delete_tag(tag)
            QMessageBox.information(self, "Delete Tag", str(out))

    def git_stash(self):
        if not self.git:
            QMessageBox.warning(self, "Git Stash", "No workspace or not a git repo.")
            return
        out = self.git.stash()
        QMessageBox.information(self, "Git Stash", str(out))

    def git_stash_pop(self):
        if not self.git:
            QMessageBox.warning(self, "Git Stash Pop", "No workspace or not a git repo.")
            return
        out = self.git.stash_pop()
        QMessageBox.information(self, "Git Stash Pop", str(out))

    def git_last_commit(self):
        if not self.git:
            QMessageBox.warning(self, "Last Commit", "No workspace or not a git repo.")
            return
        out = self.git.last_commit()
        QMessageBox.information(self, "Last Commit", str(out))

    def git_blame(self):
        if not self.git:
            QMessageBox.warning(self, "Git Blame", "No workspace or not a git repo.")
            return
        file_path, ok = QInputDialog.getText(self, "Git Blame", "Enter file path to blame:")
        if ok and file_path:
            out = self.git.blame(file_path)
            QMessageBox.information(self, "Git Blame", str(out))

    def git_fetch(self):
        if not self.git:
            QMessageBox.warning(self, "Git Fetch", "No workspace or not a git repo.")
            return
        out = self.git.fetch()
        QMessageBox.information(self, "Git Fetch", str(out))

    def git_cherry_pick(self):
        if not self.git:
            QMessageBox.warning(self, "Cherry-pick", "No workspace or not a git repo.")
            return
        commit, ok = QInputDialog.getText(self, "Cherry-pick", "Enter commit hash to cherry-pick:")
        if ok and commit:
            out = self.git.cherry_pick(commit)
            QMessageBox.information(self, "Cherry-pick", str(out))

    def git_revert(self):
        if not self.git:
            QMessageBox.warning(self, "Revert", "No workspace or not a git repo.")
            return
        commit, ok = QInputDialog.getText(self, "Revert", "Enter commit hash to revert:")
        if ok and commit:
            out = self.git.revert(commit)
            QMessageBox.information(self, "Revert", str(out))

    def git_init(self):
        if not self.git:
            # Try to initialize a new repo in workspace_folder
            if self.workspace_folder:
                self.git = GitManager(self.workspace_folder)
            else:
                QMessageBox.warning(self, "Init Repo", "No workspace folder selected.")
                return
        out = self.git.init()
        QMessageBox.information(self, "Init Repo", str(out))

    def git_set_remote(self):
        if not self.git:
            QMessageBox.warning(self, "Set Remote", "No workspace or not a git repo.")
            return
        name, ok_name = QInputDialog.getText(self, "Set Remote", "Remote name:")
        url, ok_url = QInputDialog.getText(self, "Set Remote", "Remote URL:")
        if ok_name and ok_url and name and url:
            out = self.git.set_remote(name, url)
            QMessageBox.information(self, "Set Remote", str(out))

    def git_show_remotes(self):
        if not self.git:
            QMessageBox.warning(self, "Show Remotes", "No workspace or not a git repo.")
            return
        out = self.git.remotes()
        QMessageBox.information(self, "Show Remotes", "\n".join(out) if isinstance(out, list) else str(out))

    def git_show_current_branch(self):
        if not self.git:
            QMessageBox.warning(self, "Current Branch", "No workspace or not a git repo.")
            return
        out = self.git.current_branch()
        QMessageBox.information(self, "Current Branch", str(out))

    # --- Settings Menu Actions ---
    def settings_preferences(self):
        QMessageBox.information(self, "Preferences", "Preferences dialog would appear here.")

    def settings_theme(self):
        theme, ok = QInputDialog.getItem(self, "Theme", "Select theme:", ["light", "dark", "light blue"], editable=False)
        if ok:
            self.theme.apply_theme(theme)
            self.show_status(f"Theme set to {theme}")

    # --- Plugins Menu Actions ---
    def plugins_manage(self):
        QMessageBox.information(self, "Plugins", "Plugin manager would appear here.")

    # --- Help Menu Actions ---
    def help_about(self):
        try:
            with open("about.md", "r", encoding="utf-8") as f:
                about_text = f.read()
        except Exception:
            about_text = "Code++\nA modern, extensible text/code editor.\nDeveloped by: Karthik Shetty"
        QMessageBox.about(self, "About Code++", about_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodePlusPlus()
    window.show()
    sys.exit(app.exec())
