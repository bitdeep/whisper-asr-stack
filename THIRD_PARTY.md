# Upstream components

- Deployment recipe and lifecycle patch tooling: MIT, see [LICENSE](LICENSE).
- [Speaches](https://github.com/speaches-ai/speaches): HTTP serving implementation.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) and CTranslate2: model execution.
- Whisper weights and converted checkpoints retain their respective model licenses.

No upstream source tree, weights, customer audio or transcripts are copied into this repository. The serving base is fixed by digest in `Dockerfile`. `patches/fix_lifecycle.py` modifies two verified upstream source snippets during the image build; upstream notices remain in that image.
