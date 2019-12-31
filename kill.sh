#!/usr/bin/env bash
ps -ef |grep gunicorn |awk '{print "kill -9 "$2}'|sh