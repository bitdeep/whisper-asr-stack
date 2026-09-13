# Whisper ASR stack

Serve local speech recognition through Speaches and faster-whisper with a pinned container image and persistent model storage. Use the HTTP endpoint directly or the inference SDK for VAD-enabled requests, confidence filtering and coordination with other GPU workloads.

## Run

Requires Docker Compose, NVIDIA Container Toolkit and enough free GPU memory for the selected Whisper model.

```sh
docker compose up -d
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

Extend service `speaches` from `engine.compose.yaml`. Supply your cache volume, network and resource overrides in the private application. The standalone recipe binds only loopback; authentication and routing belong to the integrating application.

The shared SDK sends `vad_filter=true` and `verbose_json`, preserves language/prompt/hotwords supplied by the caller and filters segments using confidence thresholds. Domain vocabulary, customer audio, queues and transcription storage belong to the private application.

Speaches manages model loading; an active HTTP process does not prove a model is warm. Inspect a real transcription before treating the deployment as ready. Never log audio or transcript bodies in shared diagnostics.

## Validation and provenance

`docker compose config -q` checks the recipe. Functional validation should cover synthetic speech, silence, the expected response format and cancellation. WER, RTF and throughput need a declared dataset and hardware configuration.

The upstream Speaches image is pinned by digest. This project supplies the isolated deployment recipe; see [THIRD_PARTY.md](THIRD_PARTY.md).
