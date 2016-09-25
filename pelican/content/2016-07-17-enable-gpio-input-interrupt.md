Title: Pandaboard 中断流程和中断服务函数

Date: 2016-07-17 12:00
Tags: arm, pandaboard
Slug: enable-gpio-input-interrupt
Author: Kage Shen

> ###主要内容:  
> armV7 使用GIC来管理中断, 功能许多, 但是如何开启一个普通的中断却让我花费了不少时间,  
> 因为中间的信息量太大了, 不能很快的抽取出想要的流程.  
> 所以这里也是跟着流程一点点的看看.   

###问题发现
探索中断流程, 以按键中断为例子

###解决问题
更具原理图(panda-es-b-schematic.pdf)可以看到, 按键S2是GPIO-113.

这样的话, 我们就按照下面的配置流程一一向下走:

1, Control Module: gpio 模式/双向/上拉 (Pad Configuration Register Functionality)   
   Pad Configuration Register Functionality  
   这里设置为gpio模式: PTU | IEN | M3  

2, General-Purpose Interface: 设置为输入, 边缘触发, 使能cpu0中断信号  
   GPIO_OE 设置为输入模式   
   FALLINGDETECT 设置为 Falling edge detection enabled  
   GPIO_IRQSTATUS_RAW_0 / GPIO_IRQSTATUS_0  
   
3, Vector Base Address Register (VBAT) 设置中断向量起始地址  
   这里需要说明的是, ddr初始话的时候, 内存起始地址会设置到0x80000000(uboot) 上, 那么  
   默认的VBAT[0]肯定是不能用的, 那么就需要我们改写这个地址.  
   读写指令:  
   read: "MRC p15, 0, r2, c12, c0, 0" @  
   wirte: "mcr p15, 0, r0, c12, c0, 0"  @Set VBAR  
   
4, ARM Generic Interrupt Controller  
   GICD_CTLR: Enables the forwarding of pending interrupts from the Distributor to the CPU interfaces.  
   GICD_TYPER: TYPER[4:0] contains an encoded number of available interrupts  
   GICD_IGROUPRn: The GICD_IGROUPR registers provide a status bit for each interrupt supported by the GIC.  
   GICD_ITARGETSRn: Interrupt Processor Targets Registers
   GICD_ISENABLERn: Interrupt Set-Enable Registers
   GICC_PMR: Interrupt Priority Mask Register
   GICC_CTLR; CPU Interface Control Register

> 参考资料:  
> [1]: [panda-es-b-schematic.pdf](http://pandaboard.org/sites/default/files/board_reference/pandaboard-es-b/panda-es-b-schematic.pdf)  
> [2]: [TI omap4460](http://www.ti.com/product/omap4460)  
> [3]: [ARM Architecture Reference Manual (ARMv7-A and ARMv7-R edition)](http://download.csdn.net/detail/heyuanxianzi/7568191)  


