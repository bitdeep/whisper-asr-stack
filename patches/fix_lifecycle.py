"""Apply two bounded fixes to the reviewed Speaches image, without new dependencies."""
import hashlib
from pathlib import Path

import speaches

root = Path(speaches.__file__).parent
changes = [
    (
        "executors/whisper/model_manager.py",
        "0fb6cd3886beb264bfb0e8d36acbaedeaf241f434c0847a44795b4e01773dac5",
        "            self.loaded_models[model_id].unload()",
        # The unload callback acquires _lock again. Never hold it while entering
        # the per-model lock: TTL expiry acquires those locks in the other order.
        "        model.unload()",
    ),
    (
        "routers/misc.py",
        "a2231d5eb15ac0dc4fd7bad2b86929b1d6936d60ad2c217bdf5de7e2859c352e",
        "def stop_running_model(model_manager: WhisperModelManagerDependency, model_id: str)",
        "def stop_running_model(model_manager: WhisperModelManagerDependency, model_id: ModelId)",
    ),
]
for relative, expected, before, after in changes:
    path = root / relative
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError(f"Unreviewed upstream source: {relative}")
    text = raw.decode()
    if text.count(before) != 1:
        raise RuntimeError(f"Patch target changed: {relative}")
    path.write_text(text.replace(before, after, 1))
