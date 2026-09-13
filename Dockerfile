FROM ghcr.io/speaches-ai/speaches@sha256:6ec12ebf890a17e0d4b242a8ba9e0eb1fb836e60e8a3c857aea9838d541579ac

USER root
COPY patches/fix_lifecycle.py /opt/inference/fix_lifecycle.py
RUN python /opt/inference/fix_lifecycle.py
USER ubuntu

LABEL io.bitdeep.whisper-stack.version="0.1.0"
