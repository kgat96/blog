Title: PandaBoard ES 下 Kernel 4.0.0 的移植
Date: 2015-05-01 10:00
Tags: Pandaboard
Slug: build-new-kernel-on-pandaboard
Author: Kage Shen

> ###主要内容:
> 实际上 **Kernel 4.0.0** 已经支持 [PandaBoard](http://pandaboard.org) 的，应该是 **Kernel** 主分支都是支持这块板子的，只是在实际让最新 Kernel 跑起来的过程中还是有一些问题的，所以本文就是告诉你一步步让它跑起来的。
>

###准备工作  

1，可以正常使用的开发板一个

2，Linux系统电脑一台

3，> 2G SD卡一张

4，搭建编译环境

 - **下载 arm-gcc 编译器**


```bash
arm-2014.05-29-arm-none-linux-gnueabi-i686-pc-linux-gnu.tar.bz2
#arm-none-linux-gnueabi-gcc -v
gcc version 4.8.3 20140320 (prerelease) (Sourcery CodeBench Lite 2014.05-29)
```

 - **同步库 linux-omap (Kernel)**

```bash
#git clone git://git.kernel.org/pub/scm/linux/kernel/git/tmlind/linux-omap.git
```

 - **同步库 uboot (bootloader)**

 > 原生库在  [www.denx.de](http://www.denx.de) 非常慢

```bash
#git clone https://github.com/RobertCNelson/u-boot.git
```

 - **下载根文件系统 (ubuntu-14.04.2)**

```bash
#wget -c https://rcn-ee.com/rootfs/eewiki/minfs/ubuntu-14.04.2-minimal-armhf-2015-04-27.tar.xz
```

###让它板子飞起来


 **1，格式化&制作启动分区**

```bash
#fdisk -l
Disk /dev/sdc: 1.9 GiB, 2014838784 bytes, 3935232 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xfb04e098

Device     Boot  Start     End Sectors  Size Id Type
/dev/sdc1  *      2048  264191  262144  128M  c W95 FAT32 (LBA)
/dev/sdc2       264192 3935231 3671040  1.8G 83 Linux
```

***这里有两点要注意：***

 - 第一个分区一定是 W95 FAT32 (LBA) 格式
 - 第一个分区一定是可以引导的，既有 Boot *

**2，编译 Uboot**

最新的Uboot整的和Kernel的一样的图形化的配置界面了，略屌.

![uboot menuconfig](http://7xigc2.com1.z0.glb.clouddn.com/build-new-kernel-on-pandaboard-p1.png)

那么编译自然也和Kernel一样啦，这里先不对Uboot做修改，免得大家看不懂哈

```bash
#export ARCH=arm
#export CROSS_COMPILE=arm-none-linux-gnueabi-
#make omap4_panda_defconfig
#make -j8
  ...
  OBJCOPY u-boot.bin
  MKIMAGE u-boot.img
  OBJCOPY u-boot.srec
  CC      spl/common/spl/spl.o
  LD      spl/common/spl/built-in.o
  CC      spl/lib/display_options.o
  LD      spl/lib/built-in.o
  LD      spl/u-boot-spl
  OBJCOPY spl/u-boot-spl.bin
  MKIMAGE MLO
```

这里生成了几个比较重要的文件  **MLO、u-boot.img**

 - **MLO：** TI x-loader 第二引导阶段的执行文件，omap启动的时候会读取这个文件，并load进内存
 - **u-boot.img：** 这个不解释了

**2，编译 Kernel**

编译之前我们需要做件事情，开启启动时候的打印 (**EARLY_PRINTK**)

```bash
patch to omap2plus_defconfig:
+CONFIG_DEBUG_LL=y
+CONFIG_DEBUG_OMAP4UART3=y
+CONFIG_DEBUG_OMAP2PLUS_UART=y
+CONFIG_DEBUG_LL_INCLUDE="debug/omap2plus.S"
+CONFIG_EARLY_PRINTK=y
```

```bash
export ARCH=arm
export CROSS_COMPILE=arm-none-linux-gnueabi-
make omap2plus_defconfig
make zImage -j8  // 这里就使用zImage就可以了
make dtbs
cat arch/arm/boot/zImage arch/arm/boot/dts/omap4-panda-es.dtb > /tmp/appended
mkimage -A arm -O linux -T kernel -C none -a 0x80008000 -e 0x80008000 \
         -n "Linux" -d /tmp/appended /tmp/uImage
```

这里最后生成了uImage，那为什么不用 **make uImage** 来一步生成呢，当然你可以先测试一下看看。
实际上从 linux 3.10 后，代码库就开始使用 dtbs 文件来描述板机配置，问什么，大家自己了解吧。

**3，制作启动SD卡**

拷贝刚才生成的 **uImage MLO u-boot.img** 到第一个分区，将下载的 **ubuntu-14.04.2-minimal-armhf-2015-04-27.tar.xz** 解压到第二个分区。

好了终于可以看到他启动了 : )

![boot log](http://7xigc2.com1.z0.glb.clouddn.com/build-new-kernel-on-pandaboard-p2.png)

> **Note:**
> 这里 omap4-panda-es.dtb 就是板级配置文件了，上面是将他和 zImage 和到了一起，实际上还有一种
> 更加灵活的方法，就是动态加载 dtb 文件，并加载相同的 zImage，下面提供 Uboot 动态加载命令：

<pre class="prettyprint">
> Panda # load mmc 0 zImage 0x81000000
> Panda # load mmc 0 omap4-panda-es.dtb x81f00000
> Panda # bootz 0x81000000 - 0x81f00000
</pre>


