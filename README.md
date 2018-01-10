# Atmel SAM: development platform for [PlatformIO](http://platformio.org)
[![Build Status](https://travis-ci.org/platformio/platform-atmelsam.svg?branch=develop)](https://travis-ci.org/platformio/platform-atmelsam)
[![Build status](https://ci.appveyor.com/api/projects/status/dj1c3b2d6fyxkoxq/branch/develop?svg=true)](https://ci.appveyor.com/project/ivankravets/platform-atmelsam/branch/develop)

Atmel | SMART offers Flash- based ARM products based on the ARM Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB to 2MB of Flash including a rich peripheral and feature mix.

* [Home](http://platformio.org/platforms/atmelsam) (home page in PlatformIO Platform Registry)
* [Documentation](http://docs.platformio.org/page/platforms/atmelsam.html) (advanced usage, packages, boards, frameworks, etc.)

# Usage

1. [Install PlatformIO](http://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](http://docs.platformio.org/page/projectconf.html) file:

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

Please navigate to [documentation](http://docs.platformio.org/page/platforms/atmelsam.html).
