#!/bin/sh
# wrapper-script.sh


python /configurator.py && exec trojan -c /config/config.json
