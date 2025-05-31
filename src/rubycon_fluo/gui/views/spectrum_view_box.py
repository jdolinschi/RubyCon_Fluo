from __future__ import annotations
from typing import Optional

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal, QEvent
import pyqtgraph as pg
from PySide6.QtWidgets import QGraphicsRectItem
from pyqtgraph import ViewBox


class SpectrumViewBox(ViewBox):
    """ViewBox with rich zoom interactions suitable for spectra."""

    interactionStarted = Signal()
    interactionFinished = Signal()

    def __init__(self, plot_widget: pg.PlotWidget):
        super().__init__(enableMenu=False)
        self._plot_widget = plot_widget

        # ------------------------------------------------------------------
        # internal state
        # ------------------------------------------------------------------
        self._zoom_mode = False                 # toolbar toggle
        self._zoom_start = None                 # QPointF – rectangle start
        self._zoom_rect: Optional[pg.RectROI] = None

        self._axis_start = None                 # QPointF – axis‑zoom start
        self._axis_rect: Optional[pg.LinearRegionItem] = None
        self._axis_orientation = None           # remember current orientation

        # base config -------------------------------------------------------
        self.setAcceptHoverEvents(True)
        self.enableAutoRange(False)
        self.setMouseMode(pg.ViewBox.PanMode)
        self._zoom_ref: tuple[tuple[float, float], tuple[float, float]] | None = None
        self._old_mouse_enabled: tuple[bool, bool] | None = None

    # ------------------------------------------------------------------
    # Public helpers (called by GUI controller buttons)
    # ------------------------------------------------------------------
    def enable_zoom_mode(self, enabled: bool) -> None:
        """Toggle rectangle‑zoom mode."""
        self._zoom_mode = enabled
        self.setMouseEnabled(not enabled, not enabled)
        self._plot_widget.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    def _clamp_to_view(self, pt):
        (xmin, xmax), (ymin, ymax) = (
            self._zoom_ref if self._zoom_ref is not None else self.viewRange()
        )
        return pg.Point(
            min(max(pt.x(), xmin), xmax),
            min(max(pt.y(), ymin), ymax),
        )

    def full_range(self):
        """Reset view to auto‑range on both axes."""
        self.autoRange()

    def scale_intensity(self):
        """Auto‑range Y to data inside the current X view (5 % padding)."""
        # 1) current visible X range
        (x0, x1), _ = self.viewRange()

        # 2) gather Y from *visible* curves whose X lies inside the view
        plot_item = self.parentItem()
        slices = []
        for item in plot_item.listDataItems():
            if hasattr(item, "isVisible") and not item.isVisible():
                continue
            x, y = item.getData()
            if x is None or y is None:
                continue
            m = (x >= x0) & (x <= x1)
            if np.any(m):
                slices.append(y[m])

        if not slices:  # nothing to scale
            return

        # 3) ignore NaNs when finding the extrema
        all_y = np.concatenate(slices)
        finite = np.isfinite(all_y)
        if not np.any(finite):  # only NaNs – bail out
            return
        y_min = float(all_y[finite].min())
        y_max = float(all_y[finite].max())

        # 4) apply with 5 % symmetric padding
        self.setYRange(y_min, y_max, padding=0.05)

    # ------------------------------------------------------------------
    # Mouse overrides
    # ------------------------------------------------------------------
    def mousePressEvent(self, ev):
        # Emit pause on any button down
        if ev.button() in (Qt.LeftButton, Qt.MiddleButton, Qt.RightButton):
            self.interactionStarted.emit()

        # Rectangle zoom start?
        if ev.button() == Qt.MiddleButton or (self._zoom_mode and ev.button() == Qt.LeftButton):
            self._zoom_ref = self.viewRange()  # freeze limits
            self._zoom_start = self._clamp_to_view(self.mapSceneToView(ev.scenePos()))

            self._old_mouse_enabled = self.mouseEnabled()  # disable default
            self.setMouseEnabled(False, False)
            ev.accept()
            return
        # Axis‑only zoom start?
        if ev.button() == Qt.LeftButton and (ev.modifiers() & Qt.AltModifier):
            self._axis_start = self.mapSceneToView(ev.scenePos())
            ev.accept()
            return

        # Otherwise delegate to default ViewBox behavior
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._zoom_start is not None:
            self._update_rect(ev)
            ev.accept()
            return
        if self._axis_start is not None:
            self._update_axis_region(ev)
            ev.accept()
            return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        # Handle end of rectangle zoom
        if self._zoom_start is not None:
            self._apply_rect_zoom(ev)
        # Handle end of axis‑zoom
        elif self._axis_start is not None:
            self._apply_axis_zoom(ev)
        else:
            super().mouseReleaseEvent(ev)

        ev.accept()
        # Always resume after any button release
        self.interactionFinished.emit()

    def mouseDoubleClickEvent(self, ev):
        # Double-click resets full range + resume
        if ev.button() == Qt.LeftButton:
            self.full_range()
            ev.accept()
            self.interactionFinished.emit()
        else:
            super().mouseDoubleClickEvent(ev)

    def wheelEvent(self, ev, axis=None):
        """Zoom with wheel; always emit interactionStarted/Finished so auto‑scale fires."""
        # announce start
        self.interactionStarted.emit()

        mods = ev.modifiers()
        # Ctrl → Y-only zoom
        if mods & Qt.ControlModifier:
            self._wheel_axis(ev, axis="y")
            ev.accept()
        # Shift → X-only zoom
        elif mods & Qt.ShiftModifier:
            self._wheel_axis(ev, axis="x")
            ev.accept()
        else:
            super().wheelEvent(ev)

        # announce finish (so auto‑scale runs if checked)
        self.interactionFinished.emit()

    def sceneEvent(self, ev):
        # Catch any GraphicsScene mouse release to ensure resume
        if ev.type() == QEvent.Type.GraphicsSceneMouseRelease:
            self.interactionFinished.emit()
        return super().sceneEvent(ev)

    # ------------------------------------------------------------------
    # Helper methods for zoom and pan rectangles
    # ------------------------------------------------------------------
    def _update_rect(self, ev):
        cur = self._clamp_to_view(self.mapSceneToView(ev.scenePos()))
        x0, y0 = self._zoom_start.x(), self._zoom_start.y()
        rect = QtCore.QRectF(QtCore.QPointF(x0, y0), cur).normalized()

        if self._zoom_rect is None:  # first drag‑move
            pen = pg.mkPen('r', width=1, style=QtCore.Qt.DashLine)
            self._zoom_rect = QGraphicsRectItem()      # ← coming from QtWidgets now
            self._zoom_rect.setPen(pen)
            self._zoom_rect.setBrush(QtCore.Qt.NoBrush)
            self._zoom_rect.setZValue(2)  # above curves
            self.addItem(self._zoom_rect)  # ViewBox is a QGraphicsItem
        self._zoom_rect.setRect(rect)  # live‑update size/pos

    def _apply_rect_zoom(self, ev):
        cur = self._clamp_to_view(self.mapSceneToView(ev.scenePos()))

        x0, x1 = sorted([self._zoom_start.x(), cur.x()])
        y0, y1 = sorted([self._zoom_start.y(), cur.y()])

        # remove the rubber‑band *before* changing the view
        if self._zoom_rect:
            self.removeItem(self._zoom_rect)
            self._zoom_rect = None
        self._zoom_start = None

        self.setXRange(x0, x1, padding=0)
        self.setYRange(y0, y1, padding=0)

        # restore normal interaction and clear the frozen limits
        if self._old_mouse_enabled is not None:
            self.setMouseEnabled(*self._old_mouse_enabled)
            self._old_mouse_enabled = None
        self._zoom_ref = None

    def _update_axis_region(self, ev):
        cur = self.mapSceneToView(ev.scenePos())
        dx = abs(cur.x() - self._axis_start.x())
        dy = abs(cur.y() - self._axis_start.y())
        orient = pg.LinearRegionItem.Vertical if dx > dy else pg.LinearRegionItem.Horizontal
        if orient != self._axis_orientation:
            if self._axis_rect:
                self.removeItem(self._axis_rect)
            self._axis_orientation = orient
            vals = ([self._axis_start.x(), cur.x()] if orient == pg.LinearRegionItem.Vertical
                    else [self._axis_start.y(), cur.y()])
            self._axis_rect = pg.LinearRegionItem(vals,
                                                  orientation=orient,
                                                  movable=False)
            self.addItem(self._axis_rect)
        else:
            region = ([self._axis_start.x(), cur.x()] if orient == pg.LinearRegionItem.Vertical
                      else [self._axis_start.y(), cur.y()])
            self._axis_rect.setRegion(region)

    def _apply_axis_zoom(self, ev):
        cur = self.mapSceneToView(ev.scenePos())
        dx = abs(cur.x() - self._axis_start.x())
        dy = abs(cur.y() - self._axis_start.y())
        if dx > dy:
            x0, x1 = sorted([self._axis_start.x(), cur.x()])
            self.setXRange(x0, x1, padding=0)
        else:
            y0, y1 = sorted([self._axis_start.y(), cur.y()])
            self.setYRange(y0, y1, padding=0)
        if self._axis_rect:
            self.removeItem(self._axis_rect)
            self._axis_rect = None
        self._axis_start = None
        self._axis_orientation = None

    def _wheel_axis(self, ev, axis: str):
        dy = ev.delta() if hasattr(ev, "delta") else ev.angleDelta().y()
        factor = 1.07 ** (dy / 120)
        if axis == "x":
            self.scaleBy((1 / factor, 1))
        elif axis == "y":
            self.scaleBy((1, 1 / factor))
