from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerHTML
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor   # <-- Add this import

class Editor(QsciScintilla):
    def __init__(self, parent=None, language='python'):
        super().__init__(parent)
        self.setUtf8(True)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, '00000')
        self.setFolding(QsciScintilla.PlainFoldStyle)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('#f0f0f0'))  # <-- Fixed
        self.setLexer(self._get_lexer(language))
        
    def _get_lexer(self, language):
        if language == 'python':
            return QsciLexerPython()
        elif language == 'cpp':
            return QsciLexerCPP()
        elif language == 'html':
            return QsciLexerHTML()
        # Add more lexers as needed
        return None

    def set_language(self, language):
        self.setLexer(self._get_lexer(language))