#!/usr/bin/env bash
gunicorn -b 127.0.0.1:9999 app:app -w 3 --log-level=debug --access-logfile gunicorn.log $*