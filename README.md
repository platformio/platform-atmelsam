# Atmel SAM: development platform for [PlatformIO](http://platformio.org)

[![Build Status](https://github.com/platformio/platform-atmelsam/workflows/Examples/badge.svg)](https://github.com/platformio/platform-atmelsam/actions)

Atmel | SMART offers Flash- based ARM products based on the ARM Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB to 2MB of Flash including a rich peripheral and feature mix.

* [Home](https://registry.platformio.org/platforms/platformio/atmelsam) (home page in the PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/platforms/atmelsam.html) (advanced usage, packages, boards, frameworks, etc.)

# Usage

1. [Install PlatformIO](http://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = atmelsam
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/platformio/platform-atmelsam.git
board = ...
...
```

# Configuration

Please navigate to [documentation](https://docs.platformio.org/page/platforms/atmelsam.html).
