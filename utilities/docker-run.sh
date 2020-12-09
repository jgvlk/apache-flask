#!/bin/sh
docker run \
    -v /private/etc/letsencrypt/live/jgv.mywire.org:/etc/letsencrypt/live/jgv.mywire.org:ro \
    -v /private/etc/letsencrypt/archive/jgv.mywire.org:/etc/letsencrypt/archive/jgv.mywire.org:ro \
    -p 8080:80 -p 8443:443 \
    --net=jgv-dockernet-bridge1 \
    --name myplaid-v1-ssl \
    myplaid:v1-latest-ssl