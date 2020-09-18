---
title: "Pandaboard 配置gpio功能 (uboot 2016.1)"
date: 2016-01-31T08:03:48+08:00
lastmod: 2017-08-31T15:43:48+08:00
draft: false
tags: ["Pandaboard", "Linux"]
categories: ["学习"]
author: "KK"

autoCollapseToc: true
contentCopyright: '<a href="https://github.com/" rel="noopener" target="_blank">MIT</a>'

---

## 主要内容: 
 
很久没有更新博客了, 最近买了域名, 于是乎心血来潮, 决定更新一篇小文.  
其实最近在用这个板子来配置一个外设但是什么都配置不好, 比如连设置一个IO口都不行.  
于是乎做了一堆对比, 希望能给你们节省一些调试时间.  

## 问题发现

我先在使用的是linux4.0+uboot12.1, 按照网上[Toggling_an_LED_on_Pandaboard_using_GPIO](omappedia.org/wiki/Toggling_an_LED_on_Pandaboard_using_GPIO)介绍操作, 发现功能不能用,  

## 查找问题

因为pandaboard这个板子已经比较老了, 估计是现在的新代码支持不好, 准备用较老的软件来试试点灯,  
功夫不负有心人, [在Gentoo的Arm项目上找到了pandaboard的支持](https://wiki.gentoo.org/wiki/Pandaboard), 于是下载对应编译好的工程, 惊奇发现, 上面的实验可以了! 于是剩下的工作就是找到他们的不同处了, 通过uboot的打印发现, 他的版本号是 2011.12, 于是主要查看了,  
2011.12~2016.1之间关于omap的提交, 于是发现下面两位大牛的提交:  

[ARM: OMAP4/5: Do not configure non essential pads, clocks, dplls.](https://github.com/trini/u-boot/commit/f3f98bb0b8cc520e08ea2bdfc3f9cbe4e4ac29f5)  
```
ARM: OMAP4/5: Do not configure non essential pads, clocks, dplls.

Currently on OMAP4/5 platforms, many kernel drivers are dependent
upon the bootloaders for mux, dpll and clock configurations.
This should not be the case and bootloaders should set only the
minimum required for the uboot functionality and kernel boot.

Note that this is going to break the kernel drivers. But this
is the only way to get things fixed in the kernel.

Signed-off-by: R Sricharan <r.sricharan@ti.com>
```
[ARM: OMAP4/5: Remove dead code against CONFIG_SYS_ENABLE_PADS_ALL](https://github.com/trini/u-boot/commit/e81f63f0d2acb130df68da52e711f9178592a012)  
```
ARM: OMAP4/5: Remove dead code against CONFIG_SYS_ENABLE_PADS_ALL

The commit
f3f98bb : "ARM: OMAP4/5: Do not configure non essential pads, clocks, dplls"
removed the config option aimed towards moving that stuff into kernel, which
renders some code unreachable. Remove that code.

Signed-off-by: Jassi Brar <jaswinder.singh@linaro.org>
```
**哇... 原来是他们把"不需要的" 引脚, 时钟, 等等外设都给关闭了, 有没有想过, 我们初学者的感呢 ?  
他们这样一提交, 给我们造成巨大的时间损失啊!**  

## 解决问题

好吧, 既然问题已经找到, 我们就把对应的补丁放上去就可以了,  
```diff
diff --git a/arch/arm/cpu/armv7/omap-common/hwinit-common.c b/arch/arm/cpu/armv7/omap-common/hwinit-common.c
index 80794f9..ee43320 100644
--- a/arch/arm/cpu/armv7/omap-common/hwinit-common.c
+++ b/arch/arm/cpu/armv7/omap-common/hwinit-common.c
@@ -38,6 +38,7 @@ static void set_mux_conf_regs(void)
 		set_muxconf_regs_essential();
 		break;
 	case OMAP_INIT_CONTEXT_UBOOT_AFTER_SPL:
+	    set_muxconf_regs_non_essential();
 		break;
 	case OMAP_INIT_CONTEXT_UBOOT_FROM_NOR:
 	case OMAP_INIT_CONTEXT_UBOOT_AFTER_CH:
diff --git a/arch/arm/include/asm/arch-omap4/sys_proto.h b/arch/arm/include/asm/arch-omap4/sys_proto.h
index f30f865..a110613 100644
--- a/arch/arm/include/asm/arch-omap4/sys_proto.h
+++ b/arch/arm/include/asm/arch-omap4/sys_proto.h
@@ -35,6 +35,7 @@ void watchdog_init(void);
 u32 get_device_type(void);
 void do_set_mux(u32 base, struct pad_conf_entry const *array, int size);
 void set_muxconf_regs_essential(void);
+void set_muxconf_regs_non_essential(void);
 u32 wait_on_value(u32, u32, void *, u32);
 void sdelay(unsigned long);
 void setup_clocks_for_console(void);
diff --git a/board/ti/panda/panda.c b/board/ti/panda/panda.c
index eb9ce63..b5021c5 100644
--- a/board/ti/panda/panda.c
+++ b/board/ti/panda/panda.c
@@ -286,6 +286,25 @@ void set_muxconf_regs_essential(void)
 			   sizeof(struct pad_conf_entry));
 }
 
+void set_muxconf_regs_non_essential(void)
+{
+    do_set_mux((*ctrl)->control_padconf_core_base,
+            core_padconf_array_non_essential,
+            sizeof(core_padconf_array_non_essential)
+                    / sizeof(struct pad_conf_entry));
+
+    do_set_mux((*ctrl)->control_padconf_core_base,
+            core_padconf_array_non_essential_4460,
+            sizeof(core_padconf_array_non_essential_4460)
+                    / sizeof(struct pad_conf_entry));
+
+    do_set_mux((*ctrl)->control_padconf_wkup_base,
+            wkup_padconf_array_non_essential,
+            sizeof(wkup_padconf_array_non_essential)
+                    / sizeof(struct pad_conf_entry));
+
+}
+
 #if !defined(CONFIG_SPL_BUILD) && defined(CONFIG_GENERIC_MMC)
 int board_mmc_init(bd_t *bis)
 {
diff --git a/board/ti/panda/panda_mux_data.h b/board/ti/panda/panda_mux_data.h
index 53c7080..11fcd32 100644
--- a/board/ti/panda/panda_mux_data.h
+++ b/board/ti/panda/panda_mux_data.h
@@ -78,10 +78,215 @@ const struct pad_conf_entry wkup_padconf_array_essential[] = {
 
 };
 
+//const struct pad_conf_entry wkup_padconf_array_essential_4460[] = {
+//
+//{PAD1_FREF_CLK4_REQ, (M3)}, /* gpio_wk7 for TPS: Mode 3 */
+//
+//};
+
 const struct pad_conf_entry wkup_padconf_array_essential_4460[] = {
 
-{PAD1_FREF_CLK4_REQ, (M3)}, /* gpio_wk7 for TPS: Mode 3 */
+{PAD1_FREF_CLK4_REQ, (PTU | M7)}, /* gpio_wk7 for TPS: safe mode + pull up */
+
+};
+
+const struct pad_conf_entry core_padconf_array_non_essential[] = {
+    {GPMC_AD8, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M3)},    /* gpio_32 */
+    {GPMC_AD9, (PTU | IEN | M3)},                   /* gpio_33 */
+    {GPMC_AD10, (PTU | IEN | M3)},                  /* gpio_34 */
+    {GPMC_AD11, (PTU | IEN | M3)},                  /* gpio_35 */
+    {GPMC_AD12, (PTU | IEN | M3)},                  /* gpio_36 */
+    {GPMC_AD13, (PTD | OFF_EN | OFF_PD | OFF_OUT_PTD | M3)},    /* gpio_37 */
+    {GPMC_AD14, (PTD | OFF_EN | OFF_PD | OFF_OUT_PTD | M3)},    /* gpio_38 */
+    {GPMC_AD15, (PTD | OFF_EN | OFF_PD | OFF_OUT_PTD | M3)},    /* gpio_39 */
+    {GPMC_A16, (M3)},                       /* gpio_40 */
+    {GPMC_A17, (PTD | M3)},                     /* gpio_41 */
+    {GPMC_A18, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},    /* kpd_row6 */
+    {GPMC_A19, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},    /* kpd_row7 */
+    {GPMC_A20, (IEN | M3)},                     /* gpio_44 */
+    {GPMC_A21, (M3)},                       /* gpio_45 */
+    {GPMC_A22, (M3)},                       /* gpio_46 */
+    {GPMC_A23, (OFF_EN | OFF_PD | OFF_IN | M1)},            /* kpd_col7 */
+    {GPMC_A24, (PTD | M3)},                     /* gpio_48 */
+    {GPMC_A25, (PTD | M3)},                     /* gpio_49 */
+    {GPMC_NCS0, (M3)},                      /* gpio_50 */
+    {GPMC_NCS1, (IEN | M3)},                    /* gpio_51 */
+    {GPMC_NCS2, (IEN | M3)},                    /* gpio_52 */
+    {GPMC_NCS3, (IEN | M3)},                    /* gpio_53 */
+    {GPMC_NWP, (M3)},                       /* gpio_54 */
+    {GPMC_CLK, (PTD | M3)},                     /* gpio_55 */
+    {GPMC_NADV_ALE, (M3)},                      /* gpio_56 */
+    {GPMC_NBE0_CLE, (M3)},                      /* gpio_59 */
+    {GPMC_NBE1, (PTD | M3)},                    /* gpio_60 */
+    {GPMC_WAIT0, (PTU | IEN | M3)},                 /* gpio_61 */
+    {GPMC_WAIT1,  (PTD | OFF_EN | OFF_PD | OFF_OUT_PTD | M3)},  /* gpio_62 */
+    {C2C_DATA11, (PTD | M3)},                   /* gpio_100 */
+    {C2C_DATA12, (PTU | IEN | M3)},                 /* gpio_101 */
+    {C2C_DATA13, (PTD | M3)},                   /* gpio_102 */
+    {C2C_DATA14, (M1)},                     /* dsi2_te0 */
+    {C2C_DATA15, (PTD | M3)},                   /* gpio_104 */
+    {HDMI_HPD, (M0)},                       /* hdmi_hpd */
+    {HDMI_CEC, (M0)},                       /* hdmi_cec */
+    {HDMI_DDC_SCL, (PTU | M0)},                 /* hdmi_ddc_scl */
+    {HDMI_DDC_SDA, (PTU | IEN | M0)},               /* hdmi_ddc_sda */
+    {CSI21_DX0, (IEN | M0)},                    /* csi21_dx0 */
+    {CSI21_DY0, (IEN | M0)},                    /* csi21_dy0 */
+    {CSI21_DX1, (IEN | M0)},                    /* csi21_dx1 */
+    {CSI21_DY1, (IEN | M0)},                    /* csi21_dy1 */
+    {CSI21_DX2, (IEN | M0)},                    /* csi21_dx2 */
+    {CSI21_DY2, (IEN | M0)},                    /* csi21_dy2 */
+    {CSI21_DX3, (PTD | M7)},                    /* csi21_dx3 */
+    {CSI21_DY3, (PTD | M7)},                    /* csi21_dy3 */
+    {CSI21_DX4, (PTD | OFF_EN | OFF_PD | OFF_IN | M7)},     /* csi21_dx4 */
+    {CSI21_DY4, (PTD | OFF_EN | OFF_PD | OFF_IN | M7)},     /* csi21_dy4 */
+    {CSI22_DX0, (IEN | M0)},                    /* csi22_dx0 */
+    {CSI22_DY0, (IEN | M0)},                    /* csi22_dy0 */
+    {CSI22_DX1, (IEN | M0)},                    /* csi22_dx1 */
+    {CSI22_DY1, (IEN | M0)},                    /* csi22_dy1 */
+    {CAM_SHUTTER, (OFF_EN | OFF_PD | OFF_OUT_PTD | M0)},        /* cam_shutter */
+    {CAM_STROBE, (OFF_EN | OFF_PD | OFF_OUT_PTD | M0)},     /* cam_strobe */
+    {CAM_GLOBALRESET, (PTD | OFF_EN | OFF_PD | OFF_OUT_PTD | M3)},  /* gpio_83 */
+    {USBB1_ULPITLL_CLK, (IEN | OFF_EN | OFF_IN | M1)},      /* hsi1_cawake */
+    {USBB1_ULPITLL_STP, (IEN | OFF_EN | OFF_IN | M1)},      /* hsi1_cadata */
+    {USBB1_ULPITLL_DIR, (IEN | OFF_EN | OFF_IN | M1)},      /* hsi1_caflag */
+    {USBB1_ULPITLL_NXT, (OFF_EN | M1)},             /* hsi1_acready */
+    {USBB1_ULPITLL_DAT0, (OFF_EN | M1)},                /* hsi1_acwake */
+    {USBB1_ULPITLL_DAT1, (OFF_EN | M1)},                /* hsi1_acdata */
+    {USBB1_ULPITLL_DAT2, (OFF_EN | M1)},                /* hsi1_acflag */
+    {USBB1_ULPITLL_DAT3, (IEN | OFF_EN | OFF_IN | M1)},     /* hsi1_caready */
+    {USBB1_ULPITLL_DAT4, (IEN | OFF_EN | OFF_PD | OFF_IN | M4)},    /* usbb1_ulpiphy_dat4 */
+    {USBB1_ULPITLL_DAT5, (IEN | OFF_EN | OFF_PD | OFF_IN | M4)},    /* usbb1_ulpiphy_dat5 */
+    {USBB1_ULPITLL_DAT6, (IEN | OFF_EN | OFF_PD | OFF_IN | M4)},    /* usbb1_ulpiphy_dat6 */
+    {USBB1_ULPITLL_DAT7, (IEN | OFF_EN | OFF_PD | OFF_IN | M4)},    /* usbb1_ulpiphy_dat7 */
+    {USBB1_HSIC_DATA, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},   /* usbb1_hsic_data */
+    {USBB1_HSIC_STROBE, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* usbb1_hsic_strobe */
+    {USBC1_ICUSB_DP, (IEN | M0)},                   /* usbc1_icusb_dp */
+    {USBC1_ICUSB_DM, (IEN | M0)},                   /* usbc1_icusb_dm */
+    {ABE_MCBSP2_DR, (IEN | OFF_EN | OFF_OUT_PTD | M0)},     /* abe_mcbsp2_dr */
+    {ABE_MCBSP2_DX, (OFF_EN | OFF_OUT_PTD | M0)},           /* abe_mcbsp2_dx */
+    {ABE_MCBSP2_FSX, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},    /* abe_mcbsp2_fsx */
+    {ABE_MCBSP1_CLKX, (IEN | M0)},                  /* abe_mcbsp1_clkx */
+    {ABE_MCBSP1_DR, (IEN | M0)},                    /* abe_mcbsp1_dr */
+    {ABE_MCBSP1_DX, (OFF_EN | OFF_OUT_PTD | M0)},           /* abe_mcbsp1_dx */
+    {ABE_MCBSP1_FSX, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},    /* abe_mcbsp1_fsx */
+    {ABE_PDM_UL_DATA, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* abe_pdm_ul_data */
+    {ABE_PDM_DL_DATA, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* abe_pdm_dl_data */
+    {ABE_PDM_FRAME, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M0)},   /* abe_pdm_frame */
+    {ABE_PDM_LB_CLK, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M0)},  /* abe_pdm_lb_clk */
+    {ABE_CLKS, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M0)},    /* abe_clks */
+    {ABE_DMIC_CLK1, (M0)},                      /* abe_dmic_clk1 */
+    {ABE_DMIC_DIN1, (IEN | M0)},                    /* abe_dmic_din1 */
+    {ABE_DMIC_DIN2, (PTU | IEN | M3)},              /* gpio_121 */
+    {ABE_DMIC_DIN3, (IEN | M0)},                    /* abe_dmic_din3 */
+    {UART2_CTS, (PTU | IEN | M0)},                  /* uart2_cts */
+    {UART2_RTS, (M0)},                      /* uart2_rts */
+    {UART2_RX, (PTU | IEN | M0)},                   /* uart2_rx */
+    {UART2_TX, (M0)},                       /* uart2_tx */
+    {HDQ_SIO, (M3)},                        /* gpio_127 */
+    {MCSPI1_CLK, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},        /* mcspi1_clk */
+    {MCSPI1_SOMI, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},       /* mcspi1_somi */
+    {MCSPI1_SIMO, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},       /* mcspi1_simo */
+    {MCSPI1_CS0, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M0)},  /* mcspi1_cs0 */
+    {MCSPI1_CS1, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M3)},  /* mcspi1_cs1 */
+    {MCSPI1_CS2, (PTU | OFF_EN | OFF_OUT_PTU | M3)},        /* gpio_139 */
+    {MCSPI1_CS3, (PTU | IEN | M3)},                 /* gpio_140 */
+    {SDMMC5_CLK, (PTU | IEN | OFF_EN | OFF_OUT_PTD | M0)},      /* sdmmc5_clk */
+    {SDMMC5_CMD, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M0)},  /* sdmmc5_cmd */
+    {SDMMC5_DAT0, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* sdmmc5_dat0 */
+    {SDMMC5_DAT1, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* sdmmc5_dat1 */
+    {SDMMC5_DAT2, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* sdmmc5_dat2 */
+    {SDMMC5_DAT3, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M0)}, /* sdmmc5_dat3 */
+    {MCSPI4_CLK, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},        /* mcspi4_clk */
+    {MCSPI4_SIMO, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},       /* mcspi4_simo */
+    {MCSPI4_SOMI, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},       /* mcspi4_somi */
+    {MCSPI4_CS0, (PTD | IEN | OFF_EN | OFF_PD | OFF_IN | M0)},  /* mcspi4_cs0 */
+    {UART4_RX, (IEN | M0)},                     /* uart4_rx */
+    {UART4_TX, (M0)},                       /* uart4_tx */
+    {USBB2_ULPITLL_CLK, (IEN | M3)},                /* gpio_157 */
+    {USBB2_ULPITLL_STP, (IEN | M5)},                /* dispc2_data23 */
+    {USBB2_ULPITLL_DIR, (IEN | M5)},                /* dispc2_data22 */
+    {USBB2_ULPITLL_NXT, (IEN | M5)},                /* dispc2_data21 */
+    {USBB2_ULPITLL_DAT0, (IEN | M5)},               /* dispc2_data20 */
+    {USBB2_ULPITLL_DAT1, (IEN | M5)},               /* dispc2_data19 */
+    {USBB2_ULPITLL_DAT2, (IEN | M5)},               /* dispc2_data18 */
+    {USBB2_ULPITLL_DAT3, (IEN | M5)},               /* dispc2_data15 */
+    {USBB2_ULPITLL_DAT4, (IEN | M5)},               /* dispc2_data14 */
+    {USBB2_ULPITLL_DAT5, (IEN | M5)},               /* dispc2_data13 */
+    {USBB2_ULPITLL_DAT6, (IEN | M5)},               /* dispc2_data12 */
+    {USBB2_ULPITLL_DAT7, (IEN | M5)},               /* dispc2_data11 */
+    {USBB2_HSIC_DATA, (PTD | OFF_EN | OFF_OUT_PTU | M3)},       /* gpio_169 */
+    {USBB2_HSIC_STROBE, (PTD | OFF_EN | OFF_OUT_PTU | M3)},     /* gpio_170 */
+    {UNIPRO_TX0, (PTD | IEN | M3)},                 /* gpio_171 */
+    {UNIPRO_TY0, (OFF_EN | OFF_PD | OFF_IN | M1)},          /* kpd_col1 */
+    {UNIPRO_TX1, (OFF_EN | OFF_PD | OFF_IN | M1)},          /* kpd_col2 */
+    {UNIPRO_TY1, (OFF_EN | OFF_PD | OFF_IN | M1)},          /* kpd_col3 */
+    {UNIPRO_TX2, (PTU | IEN | M3)},                 /* gpio_0 */
+    {UNIPRO_TY2, (PTU | IEN | M3)},                 /* gpio_1 */
+    {UNIPRO_RX0, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},  /* kpd_row0 */
+    {UNIPRO_RY0, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},  /* kpd_row1 */
+    {UNIPRO_RX1, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},  /* kpd_row2 */
+    {UNIPRO_RY1, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},  /* kpd_row3 */
+    {UNIPRO_RX2, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},  /* kpd_row4 */
+    {UNIPRO_RY2, (PTU | IEN | OFF_EN | OFF_PD | OFF_IN | M1)},  /* kpd_row5 */
+    {USBA0_OTG_CE, (PTD | OFF_EN | OFF_PD | OFF_OUT_PTD | M0)}, /* usba0_otg_ce */
+    {USBA0_OTG_DP, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},      /* usba0_otg_dp */
+    {USBA0_OTG_DM, (IEN | OFF_EN | OFF_PD | OFF_IN | M0)},      /* usba0_otg_dm */
+    {FREF_CLK1_OUT, (M0)},                      /* fref_clk1_out */
+    {FREF_CLK2_OUT, (PTU | IEN | M3)},              /* gpio_182 */
+    {SYS_NIRQ1, (PTU | IEN | M0)},                  /* sys_nirq1 */
+    {SYS_NIRQ2, (PTU | IEN | M0)},                  /* sys_nirq2 */
+    {SYS_BOOT0, (PTU | IEN | M3)},                  /* gpio_184 */
+    {SYS_BOOT1, (M3)},                      /* gpio_185 */
+    {SYS_BOOT2, (PTD | IEN | M3)},                  /* gpio_186 */
+    {SYS_BOOT3, (M3)},                      /* gpio_187 */
+    {SYS_BOOT4, (M3)},                      /* gpio_188 */
+    {SYS_BOOT5, (PTD | IEN | M3)},                  /* gpio_189 */
+    {DPM_EMU0, (IEN | M0)},                     /* dpm_emu0 */
+    {DPM_EMU1, (IEN | M0)},                     /* dpm_emu1 */
+    {DPM_EMU2, (IEN | M0)},                     /* dpm_emu2 */
+    {DPM_EMU3, (IEN | M5)},                     /* dispc2_data10 */
+    {DPM_EMU4, (IEN | M5)},                     /* dispc2_data9 */
+    {DPM_EMU5, (IEN | M5)},                     /* dispc2_data16 */
+    {DPM_EMU6, (IEN | M5)},                     /* dispc2_data17 */
+    {DPM_EMU7, (IEN | M5)},                     /* dispc2_hsync */
+    {DPM_EMU8, (IEN | M5)},                     /* dispc2_pclk */
+    {DPM_EMU9, (IEN | M5)},                     /* dispc2_vsync */
+    {DPM_EMU10, (IEN | M5)},                    /* dispc2_de */
+    {DPM_EMU11, (IEN | M5)},                    /* dispc2_data8 */
+    {DPM_EMU12, (IEN | M5)},                    /* dispc2_data7 */
+    {DPM_EMU13, (IEN | M5)},                    /* dispc2_data6 */
+    {DPM_EMU14, (IEN | M5)},                    /* dispc2_data5 */
+    {DPM_EMU15, (IEN | M5)},                    /* dispc2_data4 */
+    {DPM_EMU16, (M3)},                      /* gpio_27 */
+    {DPM_EMU17, (IEN | M5)},                    /* dispc2_data2 */
+    {DPM_EMU18, (IEN | M5)},                    /* dispc2_data1 */
+    {DPM_EMU19, (IEN | M5)},                    /* dispc2_data0 */
+};
+
+const struct pad_conf_entry core_padconf_array_non_essential_4460[] = {
+    {ABE_MCBSP2_CLKX, (PTU | OFF_EN | OFF_OUT_PTU | M3)},       /* led status_1 */
+};
 
+const struct pad_conf_entry wkup_padconf_array_non_essential[] = {
+    {PAD0_SIM_IO, (IEN | M0)},      /* sim_io */
+    {PAD1_SIM_CLK, (M0)},           /* sim_clk */
+    {PAD0_SIM_RESET, (M0)},         /* sim_reset */
+    {PAD1_SIM_CD, (PTU | IEN | M0)},    /* sim_cd */
+    {PAD0_SIM_PWRCTRL, (M0)},       /* sim_pwrctrl */
+    {PAD1_FREF_XTAL_IN, (M0)},      /* # */
+    {PAD0_FREF_SLICER_IN, (M0)},        /* fref_slicer_in */
+    {PAD1_FREF_CLK_IOREQ, (M0)},        /* fref_clk_ioreq */
+    {PAD0_FREF_CLK0_OUT, (M2)},     /* sys_drm_msecure */
+    {PAD1_FREF_CLK3_REQ, M7},       /* safe mode */
+    {PAD0_FREF_CLK3_OUT, (M0)},     /* fref_clk3_out */
+    {PAD0_FREF_CLK4_OUT, (PTU | M3)},   /* led status_2 */
+    {PAD0_SYS_NRESPWRON, (M0)},     /* sys_nrespwron */
+    {PAD1_SYS_NRESWARM, (M0)},      /* sys_nreswarm */
+    {PAD0_SYS_PWR_REQ, (PTU | M0)},     /* sys_pwr_req */
+    {PAD1_SYS_PWRON_RESET, (M3)},       /* gpio_wk29 */
+    {PAD0_SYS_BOOT6, (IEN | M3)},       /* gpio_wk9 */
+    {PAD1_SYS_BOOT7, (IEN | M3)},       /* gpio_wk10 */
 };
 
+
 #endif /* _PANDA_MUX_DATA_H_ */
```

大功告成, 再配置一下gpio, 问题解决!  



