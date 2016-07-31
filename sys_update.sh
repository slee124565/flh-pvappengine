#!/bin/bash -x

proj_list="/usr/share/pvappengine
/usr/share/wordpress"

for proj in ${proj_list}
do
    if [ -d ${proj} ]; then
        cd ${proj}
        git checkout -f && git pull origin master
        cd -
    fi
done

/sbin/shutdown -r 3
