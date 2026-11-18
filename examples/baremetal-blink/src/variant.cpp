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

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif


#define SCB_VTOR_ADDR 0xE000ED08    // Same for SAM3/4

#define SCB_VTOR *(volatile uint32_t *)SCB_VTOR_ADDR

// These must be defned in linker file
extern unsigned long _etext;
extern unsigned long _srelocate;
extern unsigned long _erelocate;
extern unsigned long _sbss;
extern unsigned long _ebss;
extern unsigned long _estack;

extern int main(void);

typedef void( *const intfunc )( void );

void Reset_Handler(void) __attribute__((__interrupt__));
void Default_Handler(void);

#define NMI_Handler         Default_Handler
#define HardFault_Handler   Default_Handler
#define MemManage_Handler   Default_Handler
#define BusFault_Handler    Default_Handler
#define UsageFault_Handler  Default_Handler
#define MemManage_Handler   Default_Handler
#define SVC_Handler         Default_Handler
#define DebugMon_Handler    Default_Handler
#define PendSV_Handler      Default_Handler
#define SysTick_Handler     Default_Handler


__attribute__ ((section(".vectors")))
void (* const g_pfnVectors[])(void) = {
    (intfunc)((unsigned long)&_estack), /* The stack pointer after relocation */
    Reset_Handler,              /* Reset Handler */
    NMI_Handler,                /* NMI Handler */
    HardFault_Handler,          /* Hard Fault Handler */
    MemManage_Handler,          /* MPU Fault Handler */
    BusFault_Handler,           /* Bus Fault Handler */
    UsageFault_Handler,         /* Usage Fault Handler */
    0,                          /* Reserved */
    0,                          /* Reserved */
    0,                          /* Reserved */
    0,                          /* Reserved */
    SVC_Handler,                /* SVCall Handler */
    DebugMon_Handler,           /* Debug Monitor Handler */
    0,                          /* Reserved */
    PendSV_Handler,             /* PendSV Handler */
    SysTick_Handler             /* SysTick Handler */
};

void Reset_Handler(void)
{
    /* Init Data:
     * - Loads data from addresses defined in linker file into RAM
     * - Zero bss (statically allocated uninitialized variables)
     */
    unsigned long *src, *dst;

    /* copy the data segment into ram */
    src = &_etext;
    dst = &_srelocate;
    if (src != dst)
        while(dst < &_erelocate)
            *(dst++) = *(src++);

    /* zero the bss segment */
    dst = &_sbss;
    while(dst < &_ebss)
        *(dst++) = 0;

    SCB_VTOR = ((uint32_t)g_pfnVectors & (uint32_t)0x1FFFFF80);

    main();
    while(1) {}
}

void Default_Handler(void)
{
    while (1) {}
}

void delay (volatile uint32_t time)
{
  while (time--)
    __asm ("nop");
}


#ifdef __cplusplus
}
#endif