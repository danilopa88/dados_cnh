#!/bin/sh
/usr/bin/mc alias set local http://minio:9000 minioadmin minioadmin;
/usr/bin/mc mb local/warehouse;
/usr/bin/mc anonymous set public local/warehouse;
exit 0;
