#!/bin/bash -x

proj_list="/usr/share/pvappengine
/usr/share/pvstation"

for proj in ${proj_list}
do
    if [ -d ${proj} ]; then
        cd ${proj}
        git checkout -f && git clean -fx -d && git checkout master && git pull origin master
        cd -
    fi
done

/sbin/shutdown -r 3
