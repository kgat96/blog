Title: archlinux setup Quartus II 15.0
Date: 2015-05-31 10:00
Category:
Tags: fpga linux
Slug: archlinux-setup-quartus-15
Author: Kage Shen
Summary:

> **主要内容:**
> 因为工作需要使用到 Quartus II, 于是乎就整了个XP电脑, 装了软件, 只是用习惯了Linux
> 突然又要我用XP, 只能是让我无力吐槽啊, 发现Quartus有linux版本的, 果断安装之, 装完
> 后面X解的事情就交给你们自己了, 我就不说了 ...
>

准备工作
=======

1, Linux 64bit 系统电脑一台

下载 Quartus II 15.0 软件
====

送上下载地址, 请叫我雷锋!
http://download.altera.com/akdlm/software/acdsinst/15.0/145/ib_installers/QuartusSetup-15.0.0.145-linux.run
这个版本是自带 Cyclone IV 库的 (安装的时候可以选择安装)

安装配置
====

1, 加上执行权限把

```
chmod +x QuartusSetup-15.0.0.145-linux.run
```

2, 安装

这里你就直接运行它就可以了, 中间需要你选择安装路径什么的, 相信你都会把 :)

安装好后 就可以直接运行了:

```
./altera/15.0/quartus/bin/quartus --64bit
```

不过你会发现它启动不了, 好吧, 再终端命令行里执行一下, 发现如下错误:

```
libpng12.so.0: cannot open shared object file
```

一番谷歌后了解到, 这个库现在已经不用了, 所以很多机器没用这个库了,
那么就需要我们自己安装一个这样的库咯, 我用的是 archlinux, 其它的发行版应该类似.

```
wget https://aur.archlinux.org/packages/li/libpng12/PKGBUILD
makepkg ./PKGBUILD
makepkg -i./PKGBUILD
```

实际上它就是下载了一个libpng, 编译安装的, 所以这个方法也可以试试.
http://sourceforge.net/projects/libpng/files/libpng-12.tar.xz

到了这个, 这个软件基本就能用了, 那么我可以还需要使用到 USB Blaster, 需要配置一下
USB设备的权限, 如下:

```
touch /etc/udev/rules.d/51-altera-usb-blaster.rules
```

加入一下内容:

```
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6001", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6002", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6003", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6010", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6810", MODE="0666"
```

重启一下电脑, 打开软件, 就能识别你的usb硬件了.

最后, 有图有真相嘛:

![picture](http://7xigc2.com1.z0.glb.clouddn.com/archlinux-setup-quartus-15-p1.png)

> 参考资料:
> \[1]: [Altera Design Software](https://wiki.archlinux.org/index.php/Altera_Design_Software)
> \[2]: [X解](http://bbs.eetop.cn/viewthread.php?tid=485257)

