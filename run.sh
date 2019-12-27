#!/usr/bin/env bash
gunicorn -b 0.0.0.0:9999 app:app -w 3 --log-level=debug