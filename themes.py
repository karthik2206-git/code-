from PyQt5.QtGui import QColor
class ThemeManager:
    def __init__(self, window, editor_getter=None, file_tree=None):
        """
        window: QMainWindow or top-level QWidget
        editor_getter: function returning list of all editor widgets (QTextEdit/QPlainTextEdit/QsciScintilla)
        file_tree: QTreeView or similar, optional
        """
        self.window = window
        self.editor_getter = editor_getter  # Should be a function
        self.file_tree = file_tree
        self.themes = {
            'light': self.light_theme(),
            'dark': self.dark_theme(),
            'light blue': self.light_blue_theme()
        }
        self.current_theme = 'light'

    def light_theme(self):
        return """
        QMainWindow { background: #ffffff; color: #222; }
        QTextEdit, QPlainTextEdit { background: #f8f8f8; color: #222; }
        QMenuBar, QMenu, QStatusBar { background: #f0f0f0; color: #222; }
        QTreeView { background: #f8f8f8; color: #222; }
        QTabBar::tab { background: #f0f0f0; color: #222; }
        QTabBar::tab:selected { background: #e0e0e0; color: #111; }
        QTabWidget::pane { background: #ffffff; }
        """

    def dark_theme(self):
        return """
        QMainWindow { background: #232629; color: #bbb; }
        QTextEdit, QPlainTextEdit { background: #181a1b; color: #ddd; selection-background-color: #2c2f31 }
        QMenuBar, QMenu, QStatusBar { background: #232629; color: #bbb; }
        QTreeView { background: #181a1b; color: #ddd; }
        QTabBar::tab { background: #232629; color: #bbb; }
        QTabBar::tab:selected { background: #181a1b; color: #fff; }
        QTabWidget::pane { background: #232629; }
        """

    def light_blue_theme(self):
        return """
        QMainWindow { background: #e6f2fb; color: #1a3d5c; }
        QTextEdit, QPlainTextEdit { background: #f7fbff; color: #1a3d5c; selection-background-color: #b3daff; }
        QMenuBar, QMenu, QStatusBar { background: #b3d8f8; color: #1a3d5c; }
        QTreeView { background: #d9ecfa; color: #1a3d5c; }
        QTabBar::tab { background: #b3d8f8; color: #1a3d5c; }
        QTabBar::tab:selected { background: #73baf7; color: #fff; }
        QTabWidget::pane { background: #e6f2fb; }
        """

    def apply_theme(self, name):
        stylesheet = self.themes.get(name)
        if stylesheet:
            self.window.setStyleSheet(stylesheet)
            self.current_theme = name
            # Editor widgets: apply background/foreground via API if needed
            if self.editor_getter:
                for editor in self.editor_getter():
                    self.apply_editor_colors(editor, name)
            # File tree: set background via API if needed
            if self.file_tree:
                self.apply_filetree_colors(self.file_tree, name)
        else:
            print(f"Theme '{name}' not found!")

    def apply_editor_colors(self, editor, theme_name):
        try:
            from PyQt5.Qsci import QsciScintilla
            if isinstance(editor, QsciScintilla):
                # ... set colors ...
                if hasattr(editor, "styleClearAll"):
                    editor.styleClearAll()
                return
        except ImportError:
            pass

        # For QTextEdit/QPlainTextEdit
        if hasattr(editor, "setStyleSheet"):
            if theme_name == 'light':
                editor.setStyleSheet("background-color: #f8f8f8; color: #222;")
            elif theme_name == 'dark':
                editor.setStyleSheet("background-color: #181a1b; color: #ddd;")
            elif theme_name == 'light blue':
                editor.setStyleSheet("background-color: #f7fbff; color: #1a3d5c;")

    def apply_filetree_colors(self, tree, theme_name):
        # For QTreeView
        if hasattr(tree, "setStyleSheet"):
            if theme_name == 'light':
                tree.setStyleSheet("background-color: #f8f8f8; color: #222;")
            elif theme_name == 'dark':
                tree.setStyleSheet("background-color: #181a1b; color: #ddd;")
            elif theme_name == 'light blue':
                tree.setStyleSheet("background-color: #d9ecfa; color: #1a3d5c;")
