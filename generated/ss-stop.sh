#!/bin/sh
iptables -t nat -F SHADOWSOCKS
iptables -t nat -F OUTPUT
iptables -t nat -F PREROUTING
iptables -t nat -X SHADOWSOCKS
ipset destroy china_ipset
