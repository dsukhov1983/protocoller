#!/bin/bash
rsync -avz -e ssh s7.wservices.ch:db/main db/main
