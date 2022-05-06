# apkg example project: basic packaging tests with inline control

This minimal project demonstrates how to use a single

    distro/tests/control

inline tests control file to define packaging tests.

In this simplest case, distro/tests layout is identical to Debian autopkgtest
usually seen in debian/tests in Debian package sources.

Unless you need to define different tests/dependencies per distro,
this is all you need.

See tests information:

    apkg test --info

View the control file path and content:

    apkg test --show-control

Run tests with

    apkg test
