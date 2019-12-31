#!/usr/bin/env bash
gunicorn -b 0.0.0.0:80 app:app -w 3 --log-level=debug --access-logfile gunicorn.log $*