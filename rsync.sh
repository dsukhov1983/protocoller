#!/bin/bash
rsync -avz -e ssh protocoller.ru:devel/protocoller/src/protocoller/db/main src/protocoller/db/main
rsync -avzr -e ssh protocoller.ru:devel/protocoller/src/protocoller/media/cache src/protocoller/media/cache
