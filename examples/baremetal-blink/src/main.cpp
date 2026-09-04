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
#include "pio.h"
#include "variant.h"


void HardwareInit (void)
{
  // enable peripheral clock
	//  PMC_WPMR  = PMC_WPKEY << 8 | 0;
  PMC_PCER0 = 1 << ID_PIOE;  // PIO Clock on E

  // PIOC
	//  PIOC_WPMR  = PIO_WPKEY << 8 | 0;

  PIOE->PIO_PER = 1 << LED_PIN;
  PIOE->PIO_OER = 1 << LED_PIN;
  PIOE->PIO_OWER = 1 << LED_PIN;
}

static uint32_t* const WDT_MR = (uint32_t*) 0x400E1854;     //  Watchdog Timer Mode Register SAM4: 0x400E1854  SAM3: 0x400E1A54


int main()
{
  // watchdog timer is actived on boot with a default timeout so disable it
  // note: you can only write to WDT_MR once after power on reset
  // Atmel SAM3X8E Datasheet, section 15.4, page 261
  // Atmel SAM4E8E Datasheet, section 16.5.2, page 362
  *WDT_MR |= (1 << 15); // WDDIS (watchdog disable) bit, SAM3 page 265, SAM 4 page 362


  HardwareInit ();

/*
 * Blink
 * Turns on an LED on for one second,
 * then off for one second, repeatedly.
 */

	for (;;)
	{
      PIOE->PIO_SODR = 1 << LED_PIN;
      delay (50000);
      PIOE->PIO_CODR = 1 << LED_PIN;
      delay (50000);  
	}

	return 0 ; 
  
}




