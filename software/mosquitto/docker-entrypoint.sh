#!/bin/ash

set -e

# Fix write permissions for mosquitto directories
chown --no-dereference --recursive mosquitto /mosquitto/

mkdir -p /var/run/mosquitto \
  && chown --no-dereference --recursive mosquitto /var/run/mosquitto


if ( [ -z "${MQTT_USERNAME}" ] || [ -z "${MQTT_PASSWORD}" ] ); then
  echo "MQTT_USERNAME or MQTT_PASSWORD not defined"
  exit 1
fi

# create mosquitto password file
echo "Adding user $MQTT_USERNAME"
touch passwordfile
chown mosquitto /passwordfile
chgrp mosquitto /passwordfile
chmod 0600 /passwordfile
mosquitto_passwd -b passwordfile $MQTT_USERNAME $MQTT_PASSWORD

exec "$@"