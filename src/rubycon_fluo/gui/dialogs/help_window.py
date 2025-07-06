from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

class AboutWindow(QMainWindow):
    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent, flags=Qt.Window)
        self.setWindowTitle("User Guide")
        self.resize(900, 700)

        webview = QWebEngineView(self)
        self.setCentralWidget(webview)

        html_path: Path = (
            Path(__file__).resolve().parent / "user_guide.html"
        )
        webview.load(QUrl.fromLocalFile(str(html_path)))
