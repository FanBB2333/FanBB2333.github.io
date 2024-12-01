---
title: File System configuration
type: post
---

## Mount using cifs
```bash
sudo apt install cifs-utils 
sudo mount -t cifs -o uid=***,username=***,password=***,iocharset=utf8 //nas/folder /mnt/nas
```
当然也可以使用nfs

## Acknowledgements
