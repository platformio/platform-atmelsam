/* ========================================================================== */
/*                                                                            */
/*   startup.c  main.c                                                        */
/*   (c) 2017 Bob Cousins                                                     */
/*                                                                            */
/*   2023 Axel Sepulveda gh@chepo92                                           */
/*   Description                                                              */
/*                                                                            */
/*   Minimal blink for SAM4E in platformio using no framework (baremetal)     */
/* ========================================================================== */

#ifndef _VARIANT_SAM4E8E_BAREMETAL // SAM4E8E ( 48 pin  )
#define _VARIANT_SAM4E8E_BAREMETAL

#ifdef __cplusplus
extern "C"{
#endif // __cplusplus

// Output on PE0 (Duet)
#define LED_PIN 0  // We'll blink pin4 PE0 E2_STOP on Duet Board (refer to Duet schematic https://github.com/Duet3D/Duet-2-Hardware/blob/master/Duet2/Duet2v1.04/Duet2_1.04c_Schematic.pdf)

// PMC definitions
#define PMC_PCER0 *(volatile uint32_t *)0x400E0410    // PMC Peripheral Clock Enable Register 0; Address SAM3: 0x400E0610 SAM4E: 0x400E0410

// Peripheral Identifiers SAM4E
#define ID_PIOA 9
#define ID_PIOB 10
#define ID_PIOC 11
#define ID_PIOD 12
#define ID_PIOE 13

#define PMC_WPMR *(volatile uint32_t *)0x400E06E4 // SAM3: 0x400E06E4 SAM4: 0x400E04E4

#define PMC_WPKEY 0x504D43  // 0/1 = Disables/Enables the Write Protect if WPKEY corresponds to 0x504D43 (“PMC” in ASCII)

#define PIOA ((struct gpio *)0x400E0E00)
#define PIOB ((struct gpio *)0x400E1000)
#define PIOC ((struct gpio *)0x400E1200)
#define PIOD ((struct gpio *)0x400E1400)
#define PIOE ((struct gpio *)0x400E1600)
// #define PIOF ((struct gpio *)0x400E1800)  // SAM4 has no PIOF

#define PIOA_WPMR *(volatile uint32_t *)0x400E0EE4
#define PIOB_WPMR *(volatile uint32_t *)0x400E10E4
#define PIOC_WPMR *(volatile uint32_t *)0x400E12E4
#define PIOD_WPMR *(volatile uint32_t *)0x400E14E4
#define PIOE_WPMR *(volatile uint32_t *)0x400E16E4
// #define PIOE_WPMR *(volatile uint32_t *)0x400E18E4  // SAM4 has no PIOF, SAM3 was missing

#define PIO_WPKEY 0x50494F // 0/1: Disables/Enables the Write Protect if WPKEY corresponds to 0x50494F (“PIO” in ASCII).

extern void delay( uint32_t dwMs ) ; // From arduino wiring

#ifdef __cplusplus
} // extern "C"

#endif // __cplusplus

#endif /* _VARIANT_SAM4E8E_BAREMETAL */
