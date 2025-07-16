from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Find/Replace')
        layout = QVBoxLayout()
        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()
        find_btn = QPushButton('Find')
        replace_btn = QPushButton('Replace')
        layout.addWidget(QLabel('Find:'))
        layout.addWidget(self.find_input)
        layout.addWidget(QLabel('Replace:'))
        layout.addWidget(self.replace_input)
        layout.addWidget(find_btn)
        layout.addWidget(replace_btn)
        self.setLayout(layout)
        # Connect buttons to actions