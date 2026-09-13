# Whisper ASR stack: self-hosted speech-to-text

Serve local speech recognition through Speaches and faster-whisper with a pinned container image and persistent model storage. Use the HTTP endpoint directly or the inference SDK for VAD-enabled requests, confidence filtering and coordination with other GPU workloads.

[![Release](https://img.shields.io/github/v/release/bitdeep/whisper-asr-stack)](https://github.com/bitdeep/whisper-asr-stack/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Start here:** [Transcribe audio](#run) · [Integrate the stack](#private-deployments) · [Lifecycle fixes](docs/lifecycle.md) · [Work with me](#work-with-me)

## What this adds

- A Docker Compose service for **automatic speech recognition (ASR)** with an OpenAI-compatible transcription endpoint.
- Persistent model storage and an explicit boundary for private audio and application configuration.
- Two tested Speaches fixes: unload without deadlock, and unload aliases such as `whisper-1` correctly.
- Integration with a shared GPU owner so speech recognition and heavy voice synthesis can take turns.

## Run

Requires Docker Compose, NVIDIA Container Toolkit and enough free GPU memory for the selected Whisper model.

```sh
docker compose up -d --build
curl --fail http://localhost:8010/health
curl --fail -X POST http://localhost:8010/v1/models/Systran/faster-whisper-small
curl --fail http://localhost:8010/v1/audio/transcriptions \
  -F 'file=@sample.wav' \
  -F 'model=Systran/faster-whisper-small' \
  -F 'language=pt' \
  -F 'vad_filter=true' \
  -F 'response_format=verbose_json'
```

The model preparation request may take time on the first run. Choose `Systran/faster-whisper-large-v3` when accuracy and available memory justify it. Weights stay in the `models` volume; sample audio is not bundled.

## Private deployments

Build this project's image with an immutable tag and set `WHISPER_IMAGE`. Extend service `speaches` from `engine.compose.yaml`. Supply your cache volume, network and resource overrides in the private application. The standalone recipe binds only loopback; authentication and routing belong to the integrating application.

The shared SDK sends `vad_filter=true` and `verbose_json`, preserves language/prompt/hotwords supplied by the caller and filters segments using confidence thresholds. Domain vocabulary, customer audio, queues and transcription storage belong to the private application.

Speaches manages model loading; an active HTTP process does not prove a model is warm. Inspect a real transcription before treating the deployment as ready. Never log audio or transcript bodies in shared diagnostics.

The image applies two source-hash-checked lifecycle fixes: explicit unload releases the manager lock before invoking the model's callback, and the unload route resolves aliases just like transcription. These prevent a deadlock and ensure `whisper-1` releases the actual resident model. The SDK can then release Whisper before heavy voice synthesis without deleting cached weights.

## Validation and provenance

`docker compose config -q` checks the recipe. Functional validation should cover synthetic speech, silence, the expected response format and cancellation. WER, RTF and throughput need a declared dataset and hardware configuration.

Run the CPU lifecycle regression tests against the built image:

```sh
docker run --rm --network none --cpus 2 --memory 2g \
  --entrypoint python -v "$PWD/tests:/tests:ro" whisper-asr-stack:0.1.0 \
  -m unittest discover -s /tests -v
```

The upstream Speaches base is pinned by digest in `Dockerfile`; no package installation occurs during the build. This project supplies the isolated deployment recipe and bounded lifecycle patches; see [THIRD_PARTY.md](THIRD_PARTY.md).

## Related projects

Use [the inference SDK](https://github.com/bitdeep/gpu-worker-orchestrator) for VAD requests, confidence filtering and model handoffs. [vLLM](https://github.com/bitdeep/vllm-serving-stack) provides language-model serving; [Chatterbox PT-BR](https://github.com/bitdeep/chatterbox-ptbr-server) provides Brazilian Portuguese voice cloning.

## Work with me

I build speech-to-text services and inference pipelines, including model lifecycle, GPU sharing and application integration. For consulting or engineering opportunities, [contact bitdeep on X](https://x.com/_wrbr).

For reproducible bugs, [open an issue](https://github.com/bitdeep/whisper-asr-stack/issues) with the image version and a synthetic example. Keep transcripts, recordings and credentials from real users out of public issues.
