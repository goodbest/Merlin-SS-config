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
    
### 配置chinadns
  - 修改 /opt/etc/init.d/SXXchinadns 文件，`-l /opt/etc/chinadns_iplist.txt -c /opt/etc/chinadns_chnroute.txt -p 35353 -s 114.114.114.114,127.0.0.1:1081,8.8.4.4,8.8.8.8,223.5.5.5`
  - 端口 35353

### 配置DNSMASQ
  - 修改/jffs/configs/dnsmasq.conf.add
  - 把 ss-tunnle、chinadns 当做路由器 DNSMASQ服务的上游
  - white domain采用local DNS解析，black domain采用remote DNS解析，其余采用chinadns解析
  - 可以由脚本生成，参见 https://github.com/goodbest/Merlin-SS-config

### 配置iptable
  - 国内ip走直连，国外ip走ss-redir
  - 文件名修改为`nat-start`, `chmod a+x`，并放入/jffs/scripts中
  - 可以由脚本生成，参见 https://github.com/goodbest/Merlin-SS-config
  
## 配置DDNS
  - 在/jffs/scripts/ddns-start 加入获取命令
  - 具体看 https://github.com/RMerl/asuswrt-merlin/wiki/Custom-DDNS
  
# 其他记录
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