"""Entry point – keep it minimal on purpose."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

from insta_raman.gui.controllers.main_window_controller import MainWindowController

def _dark_palette() -> QPalette:
    p = QPalette()

    # ── active / inactive colours ───────────────────────────
    p.setColor(QPalette.ColorRole.Window,           QColor(53, 53, 53))
    p.setColor(QPalette.ColorRole.Base,             QColor(35, 35, 35))
    p.setColor(QPalette.ColorRole.AlternateBase,    QColor(53, 53, 53))
    p.setColor(QPalette.ColorRole.WindowText,       Qt.GlobalColor.white)
    p.setColor(QPalette.ColorRole.Text,             Qt.GlobalColor.white)
    p.setColor(QPalette.ColorRole.ToolTipBase,      Qt.GlobalColor.white)
    p.setColor(QPalette.ColorRole.ToolTipText,      Qt.GlobalColor.white)
    p.setColor(QPalette.ColorRole.Button,           QColor(53, 53, 53))
    p.setColor(QPalette.ColorRole.ButtonText,       Qt.GlobalColor.white)
    p.setColor(QPalette.ColorRole.Highlight,        QColor(42, 130, 218))
    p.setColor(QPalette.ColorRole.HighlightedText,  Qt.GlobalColor.black)

    # ── dimmer colours for disabled widgets ────────────────
    disabled_fg  = QColor(140, 140, 140)   # light grey text
    disabled_bg  = QColor(60, 60, 60)      # slightly lighter button face

    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.HighlightedText,
    ):
        p.setColor(QPalette.ColorGroup.Disabled, role, disabled_fg)

    for role in (
        QPalette.ColorRole.Button,
        QPalette.ColorRole.Base,
        QPalette.ColorRole.Window,
    ):
        p.setColor(QPalette.ColorGroup.Disabled, role, disabled_bg)

    return p


def main() -> None:  # noqa: D401
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())

    window = MainWindowController()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
