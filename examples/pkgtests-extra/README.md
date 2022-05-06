# apkg example project: packaging tests with extras

This minimal project demonstrates how to use tests extras:

    distro/pkg/tests/extra

See tests information:

    apkg test --info

See tests information for a specific distro:

    apkg test --info --distro fedora-33

View the control file path and content:

    apkg test --show-control

Run tests:

    apkg test
