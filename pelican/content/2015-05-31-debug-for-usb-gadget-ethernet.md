Title: PandaBoard ES USB Gadget Ethernet
Date: 2015-05-31 10:00
Category: 
Tags: Pandaboard
Slug: debug-for-usb-gadget-ethernet
Author: Kage Shen
Summary:

> **主要内容:**
> 当你调试的使用如果有网络，是不是很方便呢！但是你想搭建环境的时候却发现各种麻烦，例如需要专门的硬件（路由器），需要一根网线链接，没有路由的话可能要来回插拔网线，很是麻烦。大家电脑USB口都很多，那为什么不用USB来的调试板子呢？如果能像ADB一样，那多方便啊，但是人家是Android啊，我们在调基本的linux的时候没有ADB这样的服务啊，那能不能USB转网口来通信呢？网络一通什么nfs，ssh都能用了，其他的什么的都是浮云了，于是成文共享。
> 

准备工作
=======

1，可以正常使用的开发板一个

2，Linux系统电脑一台

3，> 2G SD卡一张

4，搭建编译环境

根据前面的文章，想必现在板子也是能够启动了，不行的赶紧先看看前面的文章。

配置 Kernel 编译选项
====
其中需要选定的是下面几个选项

```
[*] CONFIG_USB_MUSB_HDRC
[*] MUSB Mode Selection (Dual Role mode)
[*] CONFIG_TWL6030_USB
[*] CONFIG_USB_GADGET
    [*] USB Gadget Drivers (CONFIG_USB_ETH)
```

这里是已经配置好的 **[config](http://7xigc2.com1.z0.glb.clouddn.com/omap2plus_defconfig.txt)**，我的是 linux4.0 版本，不过里面的选项差不多，对比USB部分配置即可。

配置网络
====

使用新编译的boot.img镜像来启动开发板，然后用USB线连接到电脑上（板子的OTG口接到电脑的USB口上），此时电脑会出现一个usb网卡：

```
enp0s20u9i1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether ba:2c:17:c4:83:aa  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 8  bytes 1184 (1.1 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

系统识别信息

```
[ 2304.806598] usbcore: registered new interface driver cdc_subset
[ 2304.806601] cdc_ether: probe of 3-9:1.0 failed with error -16
[ 2304.806616] usbcore: registered new interface driver cdc_ether
[ 2304.807396] cdc_subset 3-9:1.1 enp0s20u9i1: renamed from usb0
```

如果电脑上没有上面的信息，请确认你编译的Kernel的正确性。
首先设置开发板的IP地址以及网关：

```
ifconfig usb0 192.168.0.200 netmask 255.255.255.0 up
route add default gw 192.168.0.201
```

设置电脑上的网络配置：

```
ifconfig enp0s20u13i1 192.168.0.201 netmask 255.255.255.0 up
```
现在就可以ping一下开发板了：
```
ping 192.168.0.200
```

如果你想板子通过电脑的网络来访问外网，那么你可以这样：

```
iptables -A POSTROUTING -t nat -j MASQUERADE -s 192.168.0.0/24
sysctl -w net.ipv4.ip_forward=1
```
现在你就可以在板子上访问外网了，好玩吧！

> 参考资料:
> \[1]: [Openmoko Networking Setup USB Networking](http://wiki.openmoko.org/wiki/USB_Networking) 



