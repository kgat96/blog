---
title: "Pandaboard bootload(uboot) 启动流程探究"
date: 2015-08-15T08:03:48+08:00
lastmod: 2017-08-31T15:43:48+08:00
draft: false
tags: ["Pandaboard", "Linux"]
categories: ["学习"]
author: "KK"

autoCollapseToc: true
contentCopyright: '<a href="https://github.com/" rel="noopener" target="_blank">MIT</a>'

---

## 主要内容:
之前使用的uboot都是直接编译就可以使用了, 但是作为一个愿意折腾的人, 这样的程度显然不够,
于是一如既往的打开了uboot的代码看起来吧!

## 准备工作

1, Linux 64bit 系统电脑一台
2, 熟悉的编译器, 最好有代码引索功能的, 免得找得蛋疼
3, 下载源代码, 及芯片手册

## 引导流程从这里开始

**寻找srart源头:**

折腾过ARM的人必然知道, 系统启动前一定有一段汇编代码, 来设置时钟, 看门狗什么的.
通过前面的文章, 我们了解uboot编译后生成了两个东西是我们需要的, MLO和u-boot.img,
u-boot.img大家都知道, MLO是啥呢? 明显这个是omap4460启动时需要的, 而且是会自动
加载的二进制文件(关于omap4460的自启动过程可以参看手册 <27.1 Initialization Overview>),
那么启动的汇编代码应该就在MLO里了吧, 打开uboot代码的 Makefile (./Makefile), 发现

```bash
./Makefile:1222
spl/u-boot-spl: tools prepare
        $(Q)$(MAKE) obj=spl -f $(srctree)/scripts/Makefile.spl all
```

spl在uboot里表示第二阶段启动代码, 其实就是芯片内部代码启动完后, 就会加载spl了,
那估计就是我们说的MLO了, 继续看, MLO必然和 scripts/Makefile.spl 文件有关, 查看之

```bash
scripts/Makefile.spl:54
libs-$(CONFIG_SPL_FRAMEWORK) += common/spl/
libs-$(CONFIG_SPL_LIBCOMMON_SUPPORT) += common/
libs-$(CONFIG_SPL_LIBDISK_SUPPORT) += disk/
```

这里只发现编译选项和编译内容, 貌似没什么线索了, 换一个想法, 编译的时候没看到, 是不是
在连接的时候能够看到点什么呢, 于是飞快敲入:

```bash
$make V=1 | grep .lds
   ....
   arm-none-linux-gnueabi-ld     -r -o spl/lib/built-in.o spl/lib/hashtable.o spl/lib/errno.o spl/lib/display_options.o spl/lib/crc32.o spl/lib/ctype.o spl/lib/div64.o spl/lib/hang.o spl/lib/linux_compat.o spl/lib/linux_string.o spl/lib/string.o spl/lib/time.o spl/lib/uuid.o spl/lib/vsprintf.o

     arm-linux-gnueabihf-gcc -E -Wp,-MD,spl/.u-boot-spl.lds.d -D__KERNEL__ -D__UBOOT__ -DCONFIG_SYS_TEXT_BASE=0x80800000  -DCONFIG_SPL_BUILD  -D__ARM__ -Wa,-mimplicit-it=always  -mthumb -mthumb-interwork  -mabi=aapcs-linux  -mno-unaligned-access  -ffunction-sections -fdata-sections -fno-common -ffixed-r9  -msoft-float  -pipe  -march=armv7-a   -Iinclude    -I./arch/arm/include -include ./include/linux/kconfig.h  -nostdinc -isystem /mnt/ssd/arm-linux-gnueabihf-5.2/bin/../lib/gcc/arm-linux-gnueabihf/5.2.1/include -include ./include/u-boot/u-boot.lds.h -include ./include/config.h -DCPUDIR=arch/arm/cpu/armv7  -ansi -D__ASSEMBLY__ -x assembler-with-cpp -P -o spl/u-boot-spl.lds arch/arm/cpu/armv7/omap-common/u-boot-spl.lds

  (cd spl && arm-none-linux-gnueabi-ld   -T u-boot-spl.lds  --gc-sections -Bstatic --gc-sections -Ttext 0x40300000 arch/arm/cpu/armv7/start.o --start-group arch/arm/cpu/armv7/built-in.o arch/arm/cpu/built-in.o arch/arm/lib/built-in.o board/ti/panda/built-in.o common/spl/built-in.o common/built-in.o disk/built-in.o drivers/i2c/built-in.o drivers/gpio/built-in.o drivers/mmc/built-in.o drivers/serial/built-in.o fs/built-in.o lib/built-in.o --end-group arch/arm/lib/eabi_compat.o -L /mnt/ssd/arm-2014.05/bin/../lib/gcc/arm-none-linux-gnueabi/4.8.3/thumb2 -lgcc -Map u-boot-spl.map -o u-boot-spl)
   ....
```

编译时gcc使用 arch/arm/cpu/armv7/omap-common/u-boot-spl.lds 文件生成了 spl/u-boot-spl.lds
u-boot-spl.lds文件使用了许多宏来控制, 具体可以看看编译时的输出信息.

```bash
arch/arm/cpu/armv7/omap-common/u-boot-spl.lds:0
MEMORY { .sram : ORIGIN = CONFIG_SPL_TEXT_BASE,\
                LENGTH = CONFIG_SPL_MAX_SIZE }
MEMORY { .sdram : ORIGIN = CONFIG_SPL_BSS_START_ADDR, \
                LENGTH = CONFIG_SPL_BSS_MAX_SIZE }

OUTPUT_FORMAT("elf32-littlearm", "elf32-littlearm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)
SECTIONS
{
        .text      :
        {
                __start = .;
                *(.vectors)
                arch/arm/cpu/armv7/start.o      (.text*)
                *(.text*)
        } >.sram
```

```bash
spl/u-boot-spl.lds:0
MEMORY { .sram : ORIGIN = 0x40300000, LENGTH = (0x4030C000 - 0x40300000) }
MEMORY { .sdram : ORIGIN = 0x80a00000, LENGTH = 0x80000 }
OUTPUT_FORMAT("elf32-littlearm", "elf32-littlearm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)
SECTIONS
{
 .text :
 {
  __start = .;
  *(.vectors)
  arch/arm/cpu/armv7/start.o (.text*)
  *(.text*)
 } >.sram
 . = ALIGN(4);
 .rodata : { *(SORT_BY_ALIGNMENT(.rodata*)) } >.sram
 . = ALIGN(4);
 .data : { *(SORT_BY_ALIGNMENT(.data*)) } >.sram
 . = ALIGN(4);
 .u_boot_list : {
  KEEP(*(SORT(.u_boot_list*_i2c_*)));
 } >.sram
 . = ALIGN(4);
 __image_copy_end = .;
 .end :
 {
  *(.__end)
 }
 .bss :
 {
  . = ALIGN(4);
  __bss_start = .;
  *(.bss*)
  . = ALIGN(4);
  __bss_end = .;
 } >.sdram
}
```

spl里的0x40300000地址是什么呢?
打开手册我们可以看到: L3 OCM_RAM 0x40300000 56KB 32-bit Ex/R/W
看上去是内部扩展的RAM, 估计是专门用来的boot的, 下面是手册说明.

```bash
15.1.6.3 L3 OCM_RAM
The on-chip L3 OCM_RAM contains 56KB of RAM, and partitioning is defined by the L3 firewall logic. The
device-embedded L3 OCM_RAM has the following characteristics:
• Support for single and burst access transactions:
– Operates at full L3 interconnect clock frequency
– Fully pipelined, one 32-bit access per cycle
• Restricted access support
```

上面定义的两个内存段, 分别是sram, sdram. sram是芯片内部的一段存储区, sdram是DDR
初始化完成后才能使用的地址区域.
.text段代码将全部放在sram中, 其中arch/arm/cpu/armv7/start.o里的.text段代码放在sram的
最开始的地方. 那么start.S就是我们要找的东西啦, 打开一看, 果然就是熟悉而又陌生的汇编代码
映满屏幕, 末要慌张, 听我慢慢分析.

**顺流而下, 柳暗花明:**

打开start.S文件, 其实里面有很多注释, 已经足够我们去阅读这里的代码, 这里就会有人说了
"里面的汇编代码我不知道具体的含义啊", 很早之前我也会有这样的问题, 但是我发现, 就算我
当时能够很深入的探究, 当时算是相当明白的, 但是时间一久, 都会有遗忘, 看的时候还是要
重新查, 所以我认为, 在没有很必要的时候我是不会区深入查看这些代码的, 能了解大概在做什么
就好了.
这里也想赞一下国外码农的工程意识, 代码写的很有条理, 注释也非常详细, 值得我们学习.

这里我就列出主要调用流程:

<pre class="prettyprint">
SPL阶段:
/* Allow the board to save important registers */
b       save_boot_params  // 里实际上就是保存一下函数的返回地址
        |- disable interrupts
        |- b cpu_init_cp15  ---> |- Invalidate L1 I/D  // 无效 指令/数据 缓存
        |                        |- disable MMU        // 方便后续的内存访问, 不需要填写TLB
        |
        |- b cpu_init_crit  ---> |- b lowlevel_init --> |- Setup a temporary stack // 设置SP指针, 估计马上要跑C代码了
        |                                               |- b s_init --> |- init_omap_revision // 获取芯片ID
        |                                                               |- watchdog_init // 初始化看门狗
        |                                                               |- force_emif_self_refresh(); // 初始化DDR
        |                                                               |- setup_clocks_for_console // 开时钟等工作
        |- b _main --> |- setup SP // Set up initial C runtime environment
                       |- board_init_f_mem  // uboot设置内存
                       |- board_init_f      // spl board_init_f
                       |- board_init_r      // spl board_init_r
                       |- spl_load_image
                       |- spl_mmc_load_image
                       |- spl_mmc_do_fs_boot    // 这里把uboot.img放到了 0x80800000上
                       |- jump_to_image_no_args // 跳到uboot上 (0x80800000)

uboot阶段和spl阶段类似, 只是后面有些不一样
    ...

        |- b _main --> |- setup SP // Set up initial C runtime environment
                       |- relocate_code     // 代码从定位
                       |- relocate_vectors  // 设置中断向量
                                   |- clear BSS
                                   |- ldr pc, =board_init_r // 正式进入uboot地界

相关文件地址:
arch/arm/cpu/armv7/start.S
arch/arm/cpu/armv7/lowlevel_init.S
arch/arm/cpu/armv7/omap-common/hwinit-common.c
arch/arm/lib/crt0.S
arch/arm/lib/board.c
</pre>

上面展示东西不多, 但是包含的东西确是大大滴多啊, 涉及的基础知识很多, 如计算机理论, 编译连接 等,
是不是瞬间有了 "望尽天涯路" 的感觉.

> 参考资料:
> [1]: [Universal Boot Loader ](http://www.denx.de/wiki/U-Boot)
> [2]: [TI omap4460](http://www.ti.com/product/omap4460)

