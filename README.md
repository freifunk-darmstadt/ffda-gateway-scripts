# ffda-gateway-scripts
Some snippets we use(d) on our gateways

## check_uplink

Checks IPv4 connectivity by binding to a NATted source ip and pinging `8.8.8.8`. If the ping
fails it will retract its gateway state in batman-adv and disable the dhcpd. It it succedes it
will make sure to reenable both.

## ffapi-updater

Maintaing an ffapi file by reading a json template and substituting dynamic values.

## node-zonegen

Generating zone files for a node-only zone from gluon nodeinfo responses.

## website-api

Aggregating and exposing data collected through alfred and vnstat.
