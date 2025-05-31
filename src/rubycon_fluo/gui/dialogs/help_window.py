from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QMainWindow, QTextBrowser


class AboutWindow(QMainWindow):
    """
    Large stand-alone window that renders the project’s HTML user guide.
    Accepts full HTML5 (anchors, images, CSS) and lets external links
    open in the user’s default web browser.
    """
    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent, flags=Qt.Window)
        self.setWindowTitle("User Guide")
        self.resize(900, 700)

        browser = QTextBrowser(self)
        browser.setOpenExternalLinks(True)
        self.setCentralWidget(browser)

        html_path: Path = (
            Path(__file__).resolve().parent       # → …/gui/dialogs
            / "user_guide.html"
        )

        browser.setSource(QUrl.fromLocalFile(str(html_path)))
