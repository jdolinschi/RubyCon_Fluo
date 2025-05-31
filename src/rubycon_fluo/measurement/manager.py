from pathlib import Path
from typing import List, Optional
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui  import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from insta_raman.measurement.record import MeasurementRecord


class MeasurementManager(QObject):
    # emitted whenever records are added or removed
    recordsChanged = Signal()

    def __init__(self, model: QStandardItemModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._model = model
        self._measurements: List[MeasurementRecord] = []
        self._parent: Optional[QWidget] = parent

        # NEW ── auto-save state
        self._auto_save_enabled: bool = False
        self._auto_save_folder: Optional[Path] = None

        # Track where each record was written so we can delete the right file later
        self._saved_paths: dict[MeasurementRecord, Path] = {}  # NEW

    def enable_auto_save(self, folder: str | Path) -> None:
        """Turn on auto-save and immediately sync existing rows to *folder*."""
        p = Path(folder).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)

        self._auto_save_enabled = True
        self._auto_save_folder = p

        # Write all current records so the folder is in-sync from the start
        for rec in self._measurements:
            self._write_record_file(rec)

    @staticmethod
    def _make_unique_path(folder: Path, stem: str) -> Path:
        """
        Given *folder* and a base *stem*, return a Path “stem.txt” or
        “stem_1.txt”, “stem_2.txt”, … that doesn’t already exist.
        """
        idx = 0
        while True:
            suffix = "" if idx == 0 else f"_{idx}"
            path = folder / f"{stem}{suffix}.txt"
            if not path.exists():
                return path
            idx += 1

    def disable_auto_save(self) -> None:
        """Turn off auto-save (no files are deleted at this point)."""
        self._auto_save_enabled = False
        self._auto_save_folder = None

    def _file_path(self, rec: MeasurementRecord) -> Path:
        """Return the full Path for *rec* inside the auto-save folder."""
        assert self._auto_save_folder is not None
        return self._auto_save_folder / f"{rec.name}.txt"

    def _write_record_file(self, rec: MeasurementRecord) -> None:
        """Write *rec* to the auto-save folder, never overwriting."""
        if not (self._auto_save_enabled and self._auto_save_folder):
            return
        try:
            stem = rec.name
            path = self._make_unique_path(self._auto_save_folder, stem)

            with path.open("w") as f:
                f.write(rec.to_metadata_block())
                f.write(f"\nsaved_utc: {datetime.utcnow().isoformat()}Z")
                f.write("\n\n")
                f.write(rec.to_data_dump())

            # remember where we put it, for later deletion
            self._saved_paths[rec] = path  # NEW
        except Exception as e:
            QMessageBox.warning(
                self._parent,
                "Auto-save Error",
                f"Could not auto-save “{rec.name}.txt”:\n{e}"
            )

    def _delete_record_file(self, rec: MeasurementRecord) -> None:
        """Delete the file that corresponds to *rec*, if any."""
        if not (self._auto_save_enabled and self._auto_save_folder):
            return
        try:
            path = self._saved_paths.pop(rec, None)  # NEW
            if path is None:  # fallback
                path = self._auto_save_folder / f"{rec.name}.txt"
            if path.exists():
                path.unlink()
        except Exception as e:
            QMessageBox.warning(
                self._parent,
                "Delete Error",
                f"Could not delete “{path.name}”:\n{e}"
            )

    def add(self, rec: MeasurementRecord) -> None:
        """Add to internal list *and* the table model."""
        self._measurements.append(rec)

        row = [
            QStandardItem(rec.name),
            QStandardItem(f"{rec.r1_wavelength:.3f}"),
            QStandardItem(rec.pressure),
            QStandardItem(rec.temperature),
            QStandardItem(rec.pressure_calib),
            QStandardItem(rec.temp_calib),
        ]
        for it in row:
            it.setEditable(False)

        self._model.appendRow(row)
        self.recordsChanged.emit()
        # NEW — auto-save the new record
        self._write_record_file(rec)

    @Slot()
    def save_selected(self, table_view) -> None:
        rows = [idx.row() for idx in table_view.selectionModel().selectedRows()]
        to_save = [self._measurements[i] for i in rows]
        self._save_records(to_save)

    @Slot()
    def save_all(self) -> None:
        self._save_records(self._measurements)

    def _save_records(self, recs: List[MeasurementRecord]) -> None:
        folder = QFileDialog.getExistingDirectory(
            self._parent,
            "Choose folder to save measurements"
        )
        if not folder:
            return

        folder_path = Path(folder).expanduser().resolve()

        for rec in recs:
            try:
                stem = rec.name
                path = self._make_unique_path(folder_path, stem)

                with path.open("w") as f:
                    f.write(rec.to_metadata_block())
                    f.write(f"\nsaved_utc: {datetime.utcnow().isoformat()}Z")
                    f.write("\n\n")
                    f.write(rec.to_data_dump())
            except Exception as e:
                QMessageBox.warning(
                    self._parent,
                    "Save Error",
                    f"Failed to save '{rec.name}.txt':\n{e}"
                )

    @Slot()
    def remove_selected(self, table_view) -> None:
        rows = sorted(
            {idx.row() for idx in table_view.selectionModel().selectedRows()},
            reverse=True
        )
        for row in rows:
            rec = self._measurements[row]
            # NEW — delete matching file if auto-save is on
            self._delete_record_file(rec)

            self._model.removeRow(row)
            del self._measurements[row]

        self.recordsChanged.emit()

    @Slot()
    def remove_all(self) -> None:
        """Clear the table (and auto-save folder if active), with confirmation."""
        if self._auto_save_enabled and self._measurements:
            reply = QMessageBox.question(
                self._parent,
                "Remove All Measurements",
                "Removing all measurements will also delete their corresponding "
                "files from the auto-save folder.\n\nContinue?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply != QMessageBox.Ok:
                return

            # Delete every file first
            for rec in self._measurements:
                self._delete_record_file(rec)

        # Now clear the table/model
        self._model.removeRows(0, self._model.rowCount())
        self._measurements.clear()
        self.recordsChanged.emit()
