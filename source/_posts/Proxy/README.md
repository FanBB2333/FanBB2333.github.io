# Where is the WALL?


## Cloud Service Providers
### Oracle Cloud


### Cloudflare
#### DNS
可以让CF协助托管域名，挂CF的CDN

#### CF Workers
- 什么是ProxyIP：是用于workers转发CF托管网站的服务器IP，用于workers访问CF系网站，参考[这里](https://upsangel.com/security/vpn/cloudflare-worker-vless%E7%BF%BB%E7%89%86%E4%BB%A3%E7%90%86%E5%8E%9F%E7%90%86-proxyip%E7%B4%B0%E7%AF%80%E7%A0%94%E7%A9%B6/)
- 什么是CF反代IP：理解为非官方的CF节点，或许可以理解为用户请求经过CF CDN的落地IP？参考[这里](https://blog.tanglu.me/cloudflare_proxy_ip/)


#### Cloudflare Trace API
通过访问`https://xxx/cdn-cgi/trace`可以查看当前访问的CF节点IP
例如访问`https://nodeseek.com/cdn-cgi/trace`, `https://www.cloudflare.com/cdn-cgi/trace`
```markdown
fl：Cloudflare 服务器实例
h：网站域名
ip：当前访问者的IP地址
ts：时间戳，格式为“秒.毫秒”（bash中生成同款时间戳的命令为date +%s.%3N）
visit_scheme：访问者使用的协议
usg：访问者使用的UserAgent信息
colo：被访问的Cloudflare数据中心的所在位置，此处是由IANA定义的机场代码
sliver：请求是否被拆分成多个部分进行处理或传输
http：访问者使用的HTTP协议版本
loc：访问者的所在地（国家）
tls：访问者与服务器建立连接使用的TLS版本
sni：SNI加密或明文传输
warp：访问者是否使用了Warp服务
gateway：访问者是否使用了Cloudflare Gateway服务
rbi：访问者是否使用了Cloudflares Remote Browser Isolation(RBI)服务
kex：TLS密钥交换过程中使用的交换方式
```
参考https://lxnchan.cn/cloudflare-trace.html

## Proxy Tools
### Sing-Box
- [sing-box](https://github.com/SagerNet/sing-box)
- 订阅转换：[sing-box-subscribe](https://github.com/Toperlock/sing-box-subscribe/)


### Hiddify
- [hiddify-next](https://github.com/hiddify/hiddify-next)



## Other Tools
- Search Engine: [shodan](https://www.shodan.io/), [fofa](https://en.fofa.info/), [zoomeye](https://www.zoomeye.hk/)
- IP info: [ipinfo.io](https://ipinfo.io/), [ip-api.com](https://ip-api.com/), [ip.sb](https://ip.sb/), [`[curl] ip.gs`](https://ip.gs/), [ipapi.co](https://ipapi.co/), [ipgeolocation.io](https://ipgeolocation.io/)
- IP Fraud Risk: [scamalytics](https://scamalytics.com/), [whoer](https://whoer.net/)
- FDNS: [bgp.tools](https://bgp.tools/)
- [Public DNS Server List](https://public-dns.info/), [IP/DNS detect](https://ipleak.net/), [WebRTC](https://browserleaks.com/webrtc)

