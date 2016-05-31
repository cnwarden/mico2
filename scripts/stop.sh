#!/bin/bash

ps -ef | grep console.py | grep -v grep | awk -F ' ' '{ print $2 }' | xargs kill -9