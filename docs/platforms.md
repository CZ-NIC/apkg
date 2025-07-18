# apkg platform support

## Python support

apkg is tested to **run** on following **Python** versions:

| Python | support   |
| ------ | --------- |
| 3.13   | ✅        |
| 3.12   | ✅        |
| 3.11   | ✅        |
| 3.10   | ✅        |
| 3.9    | ✅        |
| 3.8    | ⚠️ EOL    |
| 3.7    | ⚠️ EOL    |
| 3.6    | ⚠️ EOL    |

*[EOL]: Python version reached End Of Life, but apkg still supports it for old distros.

All currently active Python releases are supported.

Additionally, older EOL Python releases are supported on best effort basis in
**legacy** mode in order to support older distros.


## distro support

apkg is able to **create packages** for/on following **distros**:

| distro | support | CI | pkgstyle | Python |
| ------ | ------- | -- | -------- | ------ |
| Debian Sid | ✅ | ❌ | [deb] | 3.13 |
| Debian 13 | ✅ | ✅ | [deb] | 3.13 |
| Debian 12 | ✅ | ✅ | [deb] | 3.11 |
| Debian 11 | ✅ | ✅ | [deb] | 3.9  |
| Debian 10 | ⚠️ legacy | ✅ | [deb] | 3.7 ⚠️ EOL |
| Debian 9 | ⚠️ legacy | ❌ | [deb] | 3.6 ⚠️ EOL |
| Ubuntu 25.04 | ✅ | ✅ | [deb] | 3.13 |
| Ubuntu 24.10 | ✅ | ✅ | [deb] | 3.12 |
| Ubuntu 24.04 | ✅ | ✅ | [deb] | 3.12 |
| Ubuntu 22.04 | ✅ | ✅ | [deb] | 3.10 |
| Ubuntu 20.04 | ⚠️ legacy | ✅ | [deb] | 3.8 ⚠️ EOL |
| Ubuntu 18.04 | ⚠️ legacy | ❌ | [deb] | 3.6 ⚠️ EOL |
| Linux Mint | ⚠️ untested | ❌ | [deb] |  |
| Pop!_OS | ⚠️ untested | ❌ | [deb] |  |
| Fedora Rawhide | ✅ | ❌ | [rpm] | 3.13 |
| Fedora 42 | ✅ | ✅ | [rpm] | 3.13 |
| Fedora 41 | ✅ | ✅ | [rpm] | 3.13 |
| Enterprise Linux 10 | ✅ | ✅ | [rpm] | 3.12 |
| Enterprise Linux 9 | ✅ | ✅ | [rpm] | 3.9 |
| Enterprise Linux 8 | ⚠️ legacy | ✅ | [rpm] | 3.6 ⚠️ EOL |
| Enterprise Linux 7 | ⚠️ legacy | ❌ | [rpm] | 3.6 ⚠️ EOL |
| openSUSE Tumbleweed | ✅ | ✅ | [rpm] | 3.11 |
| openSUSE Leap 15 | ⚠️ legacy | ✅ | [rpm] | 3.6 ⚠️ EOL, 3.11 available |
| Arch | ✅ | ✅ | [arch] | 3.13 |
| Manjaro | ⚠️ untested | ❌ | [arch] | 3.13 |
| NixOS | ✅ | ✅ | [nix] | 3.13 |

*[legacy]: Distro is old, possibly EOL, or shipping EOL Python version, but apkg still supports in on best effort basis.

*[untested]: Distro is recognized and supported by apkg in theory, but nothing actively ensures correct function - the distro isn't periodically tested in CI and there are no known apkg users. Help by using it :)

**CI** column denotes whether the distro is tested in apkg CI. Distros included
in apkg CI are very likely to work with stable and development versions of
apkg.


[deb]: pkgstyles.md#deb
[rpm]: pkgstyles.md#rpm
[arch]: pkgstyles.md#arch
[nix]: pkgstyles.md#nix


*[Enterprise Linux]: RHEL and its clones: CentOS, Alma, Rocky, Oracle
