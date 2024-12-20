---
title: Custom profile
type: post
---
# File System configuration
## Mount using cifs
```bash
sudo apt install cifs-utils 
sudo mount -t cifs -o uid=***,username=***,password=***,iocharset=utf8 //nas/folder /mnt/nas
```
当然也可以使用nfs

## Acknowledgements

# How About zsh?
## Beautify my terminal with Zsh

### Plugins

### Install zsh with non-root user

#### Acknowledgements
- https://www.cnblogs.com/XiiX/p/14618799.html
- https://iscottmark.github.io/2021/zsh/

### Misc
- Fix auto-suggestions not working: https://www.mojidong.com/post/2017-05-14-zsh-autosuggestions/


# Docker
## Proxy in docker
```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
```
 
```bash
vim /etc/systemd/system/docker.service.d/http-proxy.conf
```

```bash
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:20171"
Environment="HTTPS_PROXY=http://127.0.0.1:20171"
Environment="NO_PROXY=localhost,127.0.0.1"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```