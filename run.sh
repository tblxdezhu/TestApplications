#!/usr/bin/env bash
ps -ef |grep gunicorn |awk '{print "kill -9 "$2}'|sh
gunicorn -b 127.0.0.1:9999 app:app -w 3 --log-level=debug --access-logfile gunicorn.log $*