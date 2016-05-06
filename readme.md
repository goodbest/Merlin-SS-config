# 任务目标
配置智能梯子，实现以下几个目标：

1. 无污染的、可加速国内的DNS
	- remote DNS —> chinadns -> DNSMASQ
	- local DNS -> chinadns -> DNSMASQ
2. 根据黑白名单域名显式指定DNS，以加速查询速度。
	- 国外网站提供跨国CDN的，尽量走国内流量，因此使用 local DNS（比如phobos.apple.com）
	- 满足上一条但被污染或线路不稳定的，走国外流量，因此使用 remote DNS
	- 国内著名域名直接使用local DNS
3. 其余情况则根据DNS查询结果，普通国外IP走ss，国内IP直连。

# 基础配置

## 安装梅林固件
  - http://asuswrt.lostrealm.ca/
  
## 安装entware-ng
  1. https://www.hqt.ro/how-to-install-new-generation-entware/
  2. 格式化U盘为ext2/3/4
  3. 打开JFFS/SSHD
  
## 安装翻墙软件
### 安装包
  - opkg install shadowsocks-libev chinadns vim
  
### 配置ss
  - 配置 /opt/etc/shadowsocks.json 文件 (local server = 0.0.0.0)
  - 修改 /opt/etc/init.d/SXXshadowsocks 文件，把`ss-local`改为`ss-redir`
  - 端口 1080
  
### 配置ss-tunnel DNS转发 (remote DNS)
  - 配置 /opt/etc/shadowsocks-dns.json 文件 (-L 8.8.8.8:53 -u)
  - 修改 /opt/etc/init.d/SXXshadowsocks-dns 文件，把`ss-local`改为`ss-tunnel`
  - 端口 1081
  - 目的是把转发的remote DNS 作为chinadns remote服务器的上游
  - 服务端需支持UDP转发
    
### 配置chinadns
  - 修改 /opt/etc/init.d/SXXchinadns 文件，`-l /opt/etc/chinadns_iplist.txt -c /opt/etc/chinadns_chnroute.txt -p 35353 -s 114.114.114.114,127.0.0.1:1081,8.8.4.4,8.8.8.8,223.5.5.5`
  - 端口 35353

### 配置DNSMASQ
  - 修改/jffs/configs/dnsmasq.conf.add
  - 把 ss-tunnle、chinadns 当做路由器 DNSMASQ服务的上游
  - white domain显式采用local DNS解析，black domain采用remote DNS解析，其余采用chinadns解析
  - 可以由脚本生成，参见 https://github.com/goodbest/Merlin-SS-config

### 配置ipset
  - 国内ip走直连，因此使用ipset来加速之后iptable的执行效率
  - 可以由脚本生成初始化脚本，参见 https://github.com/goodbest/Merlin-SS-config
  - 在路由器执行一次 `china_ipset_init.sh` 后，生成`china_ipset.conf`文件供之后读取
  
### 配置iptable
  - 国内ip走直连(根据ipset执行)，国外ip走ss-redir
  - 可以由脚本生成，参见 https://github.com/goodbest/Merlin-SS-config
  - 把`china_iptable`文件名修改为`nat-start`, `chmod a+x`，并放入/jffs/scripts中
  - iptable的`OUTPUT`表是设置路由器自身走ss


# 其他记录  
## 配置DDNS
  - 在/jffs/scripts/ddns-start 加入获取命令
  - 具体看 https://github.com/RMerl/asuswrt-merlin/wiki/Custom-DDNS
  - 示例请看 `misc/ddns-start.example`

## 安装Aria2
  - opkg install aria2c ca-certificates
  - modify /opt/etc/aria2c.conf
  - 运行在6800端口
  
## 安装lighttpd
  - opkg install lighttpd
  - modify /opt/etc/lighttpd/lighttpd.conf
  
```
#防止和管理界面冲突
#注意ISP可能会屏蔽了80端口
server.port  = 81  

#https 支持
$SERVER["socket"] == ":443" {
ssl.engine = "enable"
ssl.pemfile = "/opt/etc/lighttpd/certs/lighttpd.pem"
ssl.ca-file = "/opt/etc/lighttpd/certs/alphassl.ca.pem"
ssl.use-sslv2 = "disable"
ssl.cipher-list = "TLSv1+HIGH !SSLv2 RC4+MEDIUM !aNULL !eNULL !3DES @STRENGTH"
}
```

  - 修改防火墙策略，允许WAN链接端口 `/jffs/scripts/firewall-start`

## 定时启动任务/防止任务crash
- 在`/jffs/scripts/init-start`加入以下语句，使任务每分钟自动启动
```
#!/bin/sh
cru a AutoRestartProgram "*/1 * * * *" "/opt/bin/services start"
```

## entware启动任务
  - `/opt/etc/init.d/SXX-package-name start/stop/check/restart`

## iptable相关规则命令
  - 清空整个链 `iptables -F 链名`比如`iptables -t nat -F SHADOWSOCKS `
  - 删除指定的用户自定义链 `iptables -X 链名` 比如 `iptables -t nat -X SHADOWSOCKS`
  - 从所选链中删除规则 `iptables -D 链名 规则详情` 比如 `iptables -t nat -D SHADOWSOCKS -d 223.223.192.0/255.255.240.0 -j RETURN`

# Reference
  - http://hbprotoss.github.io/posts/da-jian-zhi-neng-fan-qiang-lu-you-qi.html
  - http://www.atgfw.org/2014/06/openwrtshadowsocks.html
  - https://hong.im/2014/03/16/configure-an-openwrt-based-router-to-use-shadowsocks-and-redirect-foreign-traffic/
  - http://liberize.me/tech/raspberry-pi-transparent-proxy.html
  - https://gist.github.com/wen-long/8644243
  - https://github.com/shadowsocks/shadowsocks-libev
  - https://github.com/shadowsocks/ChinaDNS
  - https://github.com/ashi009/bestroutetb
  - https://github.com/RMerl/asuswrt-merlin/wiki
  - https://github.com/koolshare/koolshare.github.io/tree/master/shadowsocks/shadowsocks
  - https://koolshare.cn/forum.php?mod=viewthread&tid=2613
  - https://hong.im/2014/07/08/use-ipset-with-shadowsocks-on-openwrt/
  - http://manpages.ubuntu.com/manpages/lucid/man8/ipset.8.html
  - http://www.linuxjournal.com/content/advanced-firewall-configurations-ipset
  - http://felixqu.com/2015/07/27/tomato-arm-jffs-entware-shadowsocks/

