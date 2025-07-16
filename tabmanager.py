from PyQt5.QtWidgets import QTabWidget
from editor import Editor

class TabManager(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.new_tab()
    
    def new_tab(self, filename=None, text='', language='python'):
        editor = Editor(language=language)
        editor.setText(text)
        idx = self.addTab(editor, filename if filename else 'Untitled')
        self.setCurrentIndex(idx)
        return editor
        
    def close_tab(self, index):
        self.removeTab(index)