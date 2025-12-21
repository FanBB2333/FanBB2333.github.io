---
title: Custom profile
type: post
description: Linux 系统配置笔记，包括 CIFS/NFS/NTFS 挂载、Zsh 美化、Docker 代理设置等常用配置。
---
# File System configuration
## Mount using cifs
```bash
sudo apt install cifs-utils 
sudo mount -t cifs -o uid=***,username=***,password=***,iocharset=utf8 //nas/folder /mnt/nas
```
当然也可以使用nfs

## Mount NTFS in Ubuntu
```bash
sudo apt install nfs-kernel-server fuse
sudo blkid | grep ntfs
sudo mkdir /mnt/8t
sudo mount -t ntfs-3g /dev/sda1 /mnt/8t/sda1
sudo mount -t ntfs-3g /dev/sda2 /mnt/8t/sda2
sudo nano /etc/fstab

UUID=2E2EC83F580E31B4 /mnt/8t/sda1 ntfs-3g defaults,nofail 0 0
UUID=FC28DE4526ACCAE3 /mnt/8t/sda2 ntfs-3g defaults,nofail 0 0

sudo umount /mnt/8t/sda1
sudo umount /mnt/8t/sda2
```


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