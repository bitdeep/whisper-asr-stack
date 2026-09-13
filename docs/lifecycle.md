# Making explicit Whisper unload work

The pinned Speaches base has two problems on its experimental model lifecycle route. This project fixes both during the image build and tests the actual upstream classes and FastAPI route.

## 1. A lock held across its own callback

`WhisperModelManager.unload_model()` holds the manager lock and calls the model's `unload()`. That method invokes a callback which acquires the manager lock again. Because the manager lock is not reentrant, the request hangs even after the model logs that it was unloaded.

The patch looks up the model under the manager lock, then releases that lock before calling `model.unload()`. The model's own lock and reference count still protect an active inference. This also avoids holding the manager lock while acquiring the model lock, which TTL-driven unload acquires in the opposite order.

The regression test loads a dummy model, unloads it in a bounded thread, checks that the callback removes it, then loads another instance. A separate test checks that unloading a model in use still fails.

## 2. Alias resolution on the unload route

Transcription and explicit load resolve `whisper-1` to a concrete model identifier. The original DELETE route accepted a plain string, so it searched for a loaded model literally named `whisper-1` and returned 404.

The patch applies the same `ModelId` validator to DELETE. A FastAPI test confirms that the actual unload handler receives the resolved model ID.

## How to verify

Build the image and run the CPU tests shown in the [README](../README.md#validation-and-provenance). The lock and alias tests fail against the unpatched base and pass against this project's image.

For a GPU check, transcribe synthetic speech, inspect `GET /api/ps`, then unload:

```sh
curl --fail -X DELETE \
  http://localhost:8010/api/ps/Systran%2Ffaster-whisper-small
curl --fail http://localhost:8010/api/ps
```

Use the model identifier from your transcription request. A successful unload returns 204; an absent model returns 404; a model still in use returns 409. Transcribe again to verify reload from the persistent cache.

This route releases memory. It does not delete downloaded model weights. The patch script checks complete source hashes before changing the two reviewed snippets, so a different upstream image requires a fresh review.
