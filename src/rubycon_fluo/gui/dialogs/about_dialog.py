from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class AboutDialog(QDialog):
    """
    A lightweight, fixed-size window that shows author / version info.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent, Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("About")
        self.resize(350, 180)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(
            "<h3>RubyCon Fluo</h3>"
            "<p>Version 1.0.0<br>"
            "Created by <b>Jonathan Dolinschi</b></p>"
            "<p>© 2025 <a href=\"https://github.com/jdolinschi/RubyCon-Fluo\">GitHub Repository</a></p>"
            "<p>Licensed under the <a href=\"https://opensource.org/licenses/MIT\">MIT License</a>. "
            "See the <a href=\"https://github.com/jdolinschi/RubyCon-Fluo/blob/main/LICENSE\">LICENSE</a> file for full text.</p>",
            wordWrap=True
        ))

        ok_btn = QPushButton("Close", self)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignRight)
