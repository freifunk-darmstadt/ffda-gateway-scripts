## node-zonegen

This script builds, with jinja2 templating, a zone file from [gluon](https://www.github.com/freifunk-gluon/gluon)
[nodeinfo](https://api.darmstadt.freifunk.net/alfred/nodeinfo.json) responses. It respects internal and external
routing by creating two zone files with internal and external addresses, enabling a split horizon within the DNS system.
