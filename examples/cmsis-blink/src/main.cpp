#include <sam.h>
#include <stdint.h>

#if defined(ADAFRUIT_METRO_M4_EXPRESS)
#define LED_PORT PORT_PA16
const uint32_t CYCLES_PER_SEC = 48000000; // Initial speed of SAMD51 post reset
#else
#define LED_PORT PORT_PA17
const uint32_t CYCLES_PER_SEC = 1000000; // Initial speed of SAMD21 post reset
#endif

void toggleLED() {
  static bool led = false;
  led = !led;

#if defined(REG_PORT_OUT0)
  if (led) {
    REG_PORT_OUT0 &= ~LED_PORT;
  }
  else {
    REG_PORT_OUT0 |= LED_PORT;
  }
#endif
}

void init() {
  SystemInit();

  // Direct register manipulation, because CMSIS does not provide a GPIO abstraction.
#if defined(REG_PORT_OUT0)
  REG_PORT_DIR0 |= LED_PORT;
#endif
}

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
