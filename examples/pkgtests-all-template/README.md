# apkg example project: packaging tests with a single control template

This minimal project demonstrates how to use a single

    distro/tests/extra/all/control

tests extra control template with jinja2 templating based on distro variable
in order to define all distro tests from a single file.

See tests information:

    apkg test --info

View the rendered control template using

    apkg test --show-control

Run tests with

    apkg test
