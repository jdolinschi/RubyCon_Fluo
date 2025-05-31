import json
from pathlib import Path
from threading import RLock
from typing import Any, cast

class SettingsManager:
    """
    Reads & writes all per-device defaults into one JSON blob:
    {
      "last_selected": "<device_id>",
      "devices": {
        "<device_id>": { ... settings ... },
        ...
      }
    }
    """
    _lock = RLock()
    _data: dict[str, Any] = {"last_selected": None, "devices": {}}

    def __init__(self) -> None:
        # project_root/settings/
        project_root = Path(__file__).resolve().parent.parent
        cfg_dir = project_root / "settings"
        cfg_dir.mkdir(exist_ok=True)
        self._path = cfg_dir / "spectrometer_defaults.json"

        if self._path.exists():
            try:
                raw = json.loads(self._path.read_text())
                # tell the type‐checker this really is a dict[str, Any]
                self._data = cast(dict[str, Any], raw)
            except Exception:
                # corrupt or empty → start fresh
                self._data = {"last_selected": None, "devices": {}}

    def get_last_selected(self) -> str | None:
        return cast(str | None, self._data.get("last_selected"))

    def set_last_selected(self, device_id: str) -> None:
        with self._lock:
            self._data["last_selected"] = device_id
            self._save()

    def get_device_settings(self, device_id: str) -> dict[str, Any]:
        devices = cast(dict[str, Any], self._data.get("devices", {}))
        return cast(dict[str, Any], devices.get(device_id, {}))

    def set_device_settings(self, device_id: str, settings: dict[str, Any]) -> None:
        with self._lock:
            devices = cast(dict[str, Any], self._data.setdefault("devices", {}))
            devices[device_id] = settings
            self._save()

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))
