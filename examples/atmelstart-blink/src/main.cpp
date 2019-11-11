#include <atmel_start.h>

int main(void)
{
	atmel_start_init(); // Initializes MCU, drivers and middleware

  gpio_set_pin_direction(LED_PIN, GPIO_DIRECTION_OUT);
  gpio_set_pin_pull_mode(LED_PIN, GPIO_PULL_OFF);
	gpio_set_pin_level(LED_PIN, false);

  for( ;; ) {
  	gpio_toggle_pin_level(LED_PIN);
    delay_ms(500);
  }
}
