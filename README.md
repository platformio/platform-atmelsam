
# Atmel SAM   [![Badge Status]][Status]

*A development platform for **[PlatformIO]**.*

<br>

<div align = center>

---

[![Button PIO Page]][PIO Page]   
[![Button Documentation]][Documentation]

---

</div>

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

2. Create a new project project

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


[Documentation]: https://docs.platformio.org/page/platforms/atmelsam.html 'Advanced usage, packages, boards, frameworks, etc.'
[PlatformIO]: https://platformio.org
[PIO Page]: https://registry.platformio.org/platforms/platformio/atmelsam 'Home page in the PlatformIO Registry'
[Status]: https://github.com/platformio/platform-atmelsam/actions
[Config]: https://docs.platformio.org/page/projectconf.html


<!---------------------------------[ Badges ]---------------------------------->

[Badge Status]: https://github.com/platformio/platform-atmelsam/workflows/Examples/badge.svg


<!--------------------------------[ Buttons ]---------------------------------->

[Button Documentation]: https://img.shields.io/badge/Documentation-3884FF?style=for-the-badge&logoColor=white&logo=GitBook
[Button PIO Page]: https://img.shields.io/badge/PlatformIO-ff7f00?style=for-the-badge&logoColor=white&logo=AzureArtifacts
