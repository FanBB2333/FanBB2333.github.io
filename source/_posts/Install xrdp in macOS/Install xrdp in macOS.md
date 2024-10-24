# Install xrdp in macOS
## Prerequisites


## Install
### Build
implicit declaration error while building
![](imgs/2023-12-22-09-47-26.png)
查了下可以指定`-std=c89`，不过试了试发现没有效果
于是直接去看源代码，报错的这行看起来是用来记录LOG的，全局搜索发现别的地方也有记录log的逻辑，复制过来，仍然报错，查找后发现是因为没有`stdio.h`头函数的原因，引入之后终于编译成功
![](imgs/2023-12-22-10-08-52.png)

编译好了xrdp，又要变异xorgxrdp
解决了文档中提到的X11的include问题，又遇到了新的问题
![](imgs/2023-12-22-10-34-00.png)
参考[这里](https://forums.opensuse.org/t/leap-15-4-xorgxrdp-problem-with-make/152223)的解决方案换成老版本的xorgxrdp稳定版，但是还是报错

## Tips
Unofficial guide: [[WIP] xrdp on macOS (with ulalaca)](https://github.com/neutrinolabs/xrdp/wiki/%5BWIP%5D-xrdp-on-macOS-(with-ulalaca)), [Building on OSX (not official)](https://github.com/neutrinolabs/xrdp/wiki/Building-on-OSX-(not-official))