"""Exercise the actual serving image's model lifecycle without GPU or downloaded weights."""
import threading
import unittest
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from speaches.dependencies import get_model_manager
from speaches.executors.whisper.model_manager import WhisperModelManager
from speaches.model_aliases import resolve_model_id_alias
from speaches.routers.misc import router


class LifecycleTests(unittest.TestCase):
    def manager(self):
        manager = WhisperModelManager(SimpleNamespace(ttl=-1))
        manager._load_fn = lambda _: object()
        return manager

    def test_explicit_unload_returns_and_model_reloads(self):
        manager = self.manager()
        with manager.load_model("synthetic") as first:
            self.assertIsNotNone(first)
        failures = []

        def unload():
            try:
                manager.unload_model("synthetic")
            except Exception as error:
                failures.append(error)

        thread = threading.Thread(target=unload, daemon=True)
        thread.start()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive(), "Explicit unload deadlocked")
        self.assertEqual(failures, [])
        self.assertEqual(list(manager.loaded_models), [])
        with manager.load_model("synthetic") as second:
            self.assertIsNot(second, first)

    def test_in_use_model_cannot_be_unloaded(self):
        manager = self.manager()
        with manager.load_model("synthetic"):
            with self.assertRaises(ValueError):
                manager.unload_model("synthetic")

    def test_delete_route_resolves_the_transcription_alias(self):
        received = []
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_model_manager] = lambda: SimpleNamespace(unload_model=received.append)
        with TestClient(app) as client:
            response = client.delete("/api/ps/whisper-1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(received, [resolve_model_id_alias("whisper-1")])
        self.assertNotEqual(received, ["whisper-1"])


if __name__ == "__main__":
    unittest.main()
