#include <sam.h>
#include <stdint.h>

#define LED_PORT PORT_PA17

void toggleLED() {
  static bool led = false;
  led = !led;

  if (led) {
    REG_PORT_OUT0 &= ~LED_PORT;
  }
  else {
    REG_PORT_OUT0 |= LED_PORT;
  }
}

void init() {
  SystemInit();

  // Direct register manipulation, because CMSIS does not provide a GPIO abstraction.
  REG_PORT_DIR0 |= LED_PORT;
}

const uint32_t CYCLES_PER_SEC = 1000000; // Initial speed of SAMD21 post reset
const uint32_t CYCLES_PER_MS = CYCLES_PER_SEC / 1000;
const uint32_t CYCLES_PER_LOOP = 6;
const uint32_t LOOPS_PER_MS = CYCLES_PER_MS / CYCLES_PER_LOOP;
void spinDelay(uint16_t ms) {
  for (uint16_t d = 0; d<ms; ++d) {
    for (uint32_t c = 0; c<LOOPS_PER_MS; ++c) {
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
      static volatile uint32_t ticks = 0; // Volatile so that loop retained by compiler.
#pragma GCC diagnostic pop

      ticks = c;
    }
  }
}

int main() {
  init();

  for( ;; ) {
    toggleLED();

    spinDelay(500);
  }
}
