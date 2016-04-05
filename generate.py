import urllib2
import re
import math

def fetch_cnip_data(apnicfile=''):
    #fetch data from apnic
    print "Fetching data from apnic.net, it might take a few minutes, please wait..."
    if apnicfile == '':
        url=r'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'
    else:
        url=apnicfile
    data=urllib2.urlopen(url).read()

    cnregex=re.compile(r'apnic\|cn\|ipv4\|[0-9\.]+\|[0-9]+\|[0-9]+\|a.*',re.IGNORECASE)
    cndata=cnregex.findall(data)

    results=[]

    for item in cndata:
        unit_items=item.split('|')
        starting_ip=unit_items[3]
        cidr=32-int(math.log(int(unit_items[4]),2))
        results.append(str(starting_ip)+'/'+str(cidr));
    return results
    


def outputIPtable(outputFileName='china_iptable.sh', ssip=['1.1.1.1'], localport=1080, china_ipset='china_ipset'):
    outputFile=open(outputFileName,'w')
    outputFile.write('#!/bin/sh\n')
    outputFile.write('iptables -t nat -N SHADOWSOCKS\n')
    
    outputFile.write('\n#Bypass SS Server IP\n')
    for ip in ssip:
        outputFile.write('iptables -t nat -A SHADOWSOCKS -d %s -j RETURN\n' %ip)
    
    intranetCIDR=['0.0.0.0/8','10.0.0.0/8','127.0.0.0/8','169.254.0.0/16','172.16.0.0/12','192.168.0.0/16','224.0.0.0/4','240.0.0.0/']
    outputFile.write('\n#Intranet IP\n')
    for ip in intranetCIDR:
        outputFile.write('iptables -t nat -A SHADOWSOCKS -d %s -j RETURN\n' %ip)
    
    outputFile.write('\n#CN IP\n')
    outputFile.write('ipset -R </jffs/configs/china_ipset.conf\n')
    outputFile.write('iptables -t nat -A SHADOWSOCKS -p tcp -m set --match-set %s dst -j RETURN\n' %china_ipset)

    outputFile.write('\n#Redirect Other IP\n')
    outputFile.write('iptables -t nat -A SHADOWSOCKS -p tcp -j REDIRECT --to-ports %s\n' %localport)
    outputFile.write('\n#Apply\n')
    outputFile.write('iptables -t nat -A PREROUTING -p tcp -j SHADOWSOCKS\n')
    
    outputFile.close()

def outputIPSET(outputFileName='china_ipset_init.sh', ipsetName='china_ipset'):
    outputFile=open(outputFileName,'w')
    outputFile.write('#!/bin/sh\n')
    outputFile.write('ipset -N %s nethash\n' %ipsetName)
    cnCIDR=fetch_cnip_data()
    for ip in cnCIDR:
        outputFile.write('ipset -A %s %s\n' %(ipsetName, ip))
    
    outputFile.write('ipset --save %s >/jffs/configs/china_ipset.conf\n' %ipsetName)
    outputFile.write('ipset --destroy %s\n' %ipsetName)
    outputFile.close
    
def outputDNSMASQ(outputFileName='dnsmasq.conf.add', localdns='114.114.114.114', remotedns='127.0.0.1#1081', chinadns='127.0.0.1#35353' , whiteFile='white.txt', blackFile='black.txt'):
    outputFile=open(outputFileName,'w')
    outputFile.write('no-resolv\n')
    
    black=open(blackFile)
    for line in black:
        outputFile.write('server=/%s/%s\n' %(line.strip(), remotedns))
    
    white=open(whiteFile)
    for line in white:
        outputFile.write('server=/%s/%s\n' %(line.strip(), localdns))
    
    outputFile.write('server=/#/%s\n' %chinadns)
    outputFile.close()


outputIPSET()
outputIPtable(ssip=['your.ip.address.here', 'and.add.another.here'])
outputDNSMASQ()



        
        
        
        