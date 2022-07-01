
# Atmel SAM   [![Badge Status]][Status]

*A development platform for **[PlatformIO]**.*

<br>

* [Home](https://registry.platformio.org/platforms/platformio/atmelsam) (home page in the PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/platforms/atmelsam.html) (advanced usage, packages, boards, frameworks, etc.)

<br>
<br>

## Supported Architectures

Offers a rich selection of peripherals and features to:

- Flash based products

- ARM based products

    `8KB → 2MB` of flash 

    - `Cortex-M0+`
    
    - `Cortex-M3`
    
    - `Cortex-M4`
    
<br>
<br>

## Usage

1. Install **[PlatformIO]**

2. Create PlatformIO project

3. Configure a platform option in [`/platformio.ini`][Config]

    #### Stable

    ```ini
    [env:stable]
    platform = atmelsam
    board = ...
    ...
    ```

    #### Development

    ```ini
    [env:development]
    platform = https://github.com/platformio/platform-atmelsam.git
    board = ...
    ...
    ```
<br>


<!----------------------------------------------------------------------------->

[Badge Status]: https://github.com/platformio/platform-atmelsam/workflows/Examples/badge.svg

[PlatformIO]: https://platformio.org
[Status]: https://github.com/platformio/platform-atmelsam/actions
[Config]: https://docs.platformio.org/page/projectconf.html

