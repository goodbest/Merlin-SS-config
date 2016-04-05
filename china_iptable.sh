#!/bin/sh
iptables -t nat -N SHADOWSOCKS

#Bypass SS Server IP
iptables -t nat -A SHADOWSOCKS -d your.ip.address.here -j RETURN
iptables -t nat -A SHADOWSOCKS -d and.add.another.here -j RETURN

#Intranet IP
iptables -t nat -A SHADOWSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 240.0.0.0/ -j RETURN

#CN IP
ipset -R </jffs/configs/china_ipset.conf
iptables -t nat -A SHADOWSOCKS -p tcp -m set --match-set china_ipset dst -j RETURN

#Redirect Other IP
iptables -t nat -A SHADOWSOCKS -p tcp -j REDIRECT --to-ports 1080

#Apply
iptables -t nat -A PREROUTING -p tcp -j SHADOWSOCKS
