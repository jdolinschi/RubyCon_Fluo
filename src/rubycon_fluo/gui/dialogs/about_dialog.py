from __future__ import annotations
from pathlib import Path

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

        # --- YOUR CONTENT HERE ------------------------------------------
        layout.addWidget(QLabel(
            "<h3>Insta-Raman</h3>"
            "<p>Version 1.0.0<br>"
            "Created by <b>Your Name</b></p>"
            "<p>© 2024 Your Lab – All rights reserved.</p>",
            wordWrap=True
        ))

        ok_btn = QPushButton("Close", self)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignRight)
