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

#ifdef __cplusplus
extern "C" {
#endif

// PIO definitions
// Parallel Input/Output Controller (PIO) User Interface
// You can see that consecutive 32 bit registers are mapped at 4 bytes increments. 
// 0x0004 bytes = 4*8 = 32 bit

// typedef  struct { } gpio  alternative as in \system\CMSIS\Device\ATMEL\sam4e\include\component\pio.h
// extern struct gpio {
struct gpio {
  // + 0x00
  volatile uint32_t PIO_PER;      // PIO Enable Register
  volatile uint32_t PIO_PDR;      // PIO Disable Register
  volatile uint32_t PIO_PSR;      // PIO Status Register 
  volatile uint32_t res1;
  // + 0x10
  volatile uint32_t PIO_OER;
  volatile uint32_t PIO_ODR;
  volatile uint32_t PIO_OSR;
  volatile uint32_t res2;
  // + 0x20
  volatile uint32_t PIO_IFER;
  volatile uint32_t PIO_IFDR;
  volatile uint32_t PIO_IFSR;
  volatile uint32_t res3;
  // + 0x30
  volatile uint32_t PIO_SODR;
  volatile uint32_t PIO_CODR;
  volatile uint32_t PIO_ODSR;
  volatile uint32_t PIO_PDSR;
  // + 0x40
  volatile uint32_t PIO_IER;
  volatile uint32_t PIO_IDR;
  volatile uint32_t PIO_IMR;
  volatile uint32_t PIO_ISR;
  // + 0x50
  volatile uint32_t PIO_MDER;
  volatile uint32_t PIO_MDDR;
  volatile uint32_t PIO_MDSR;
  volatile uint32_t res4;
  // + 0x60
  volatile uint32_t PIO_PUDR;
  volatile uint32_t PIO_PUER;
  volatile uint32_t PIO_PUSR;
  volatile uint32_t res5;
  // + 0x70
  volatile uint32_t PIO_ABCDSR1;    // SAM4E Table 33-5. Register Mapping (Continued), SAM3: PIO_ABSR
  volatile uint32_t PIO_ABCDSR2;    // SAM4E Table 33-5. Register Mapping (Continued), SAM3: reserved
  volatile uint32_t res6[2];
  // + 0x80
  volatile uint32_t PIO_SCIFSR;
  volatile uint32_t PIO_DIFSR;
  volatile uint32_t PIO_IFDGSR;
  volatile uint32_t PIO_SCDR;
  // + 0x90
  volatile uint32_t res7[4];
  // + 0xA0
  volatile uint32_t PIO_OWER;
  volatile uint32_t PIO_OWDR;
  volatile uint32_t PIO_OWSR;
  volatile uint32_t res8;
  // ...
} ;


#ifdef __cplusplus
}
#endif