# File System
## Mount using cifs
```bash
sudo apt install cifs-utils 
sudo mount -t cifs -o uid=***,username=***,password=***,iocharset=utf8 nas地址 本地地址
```
当然也可以使用nfs