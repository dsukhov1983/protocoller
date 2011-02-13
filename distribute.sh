#!/bin/bash -x

dest=s7.wservices.ch

git push &&

rsync -avz -e ssh src/protocoller/db/main $dest:devel/protocoller/src/protocoller/db/main &&

ssh $dest "cd devel/protocoller && git pull &&  ~/init/protocoller restart"

