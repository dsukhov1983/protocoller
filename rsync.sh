#!/bin/bash
rsync -avz -e ssh s7.wservices.ch:devel/protocoller/src/protocoller/db/main src/protocoller/db/main
