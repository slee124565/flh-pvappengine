#!/bin/bash
# /etc/init.d/uwsgi

### BEGIN INIT INFO
# Provides:          FLH
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: uwsgi startup script
# Description:       This service is used to manage a servo
### END INIT INFO


case "$1" in 
    start)
        echo "Starting uWSGI"
        exec /root/Env/appeng/bin/uwsgi --emperor /etc/uwsgi/apps-enabled &
        ;;
    stop)
        echo "Stopping uWSGI"
        killall uwsgi
        ;;
	restart)
		echo "Restarting uWSGI"
		killall uwsgi
        sleep 3
		exec /root/Env/appeng/bin/uwsgi --emperor /etc/uwsgi/apps-enabled &
		;;
    *)
        echo "Usage: /etc/init.d/uwsgi start|stop|restart"
        exit 1
        ;;
esac

exit 0

