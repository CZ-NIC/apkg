{ lib, fetchFromGitLab, python3Packages
, gitMinimal, rpm, dpkg, fakeroot
}:

python3Packages.buildPythonApplication rec {
  pname = "apkg";
  version = "{{ version }}";
  format = "pyproject";

  src = fetchFromGitLab {
    domain = "gitlab.nic.cz";
    owner = "packaging";
    repo = pname;
    rev = "v${version}";
    sha256 = "FIXME"; # would be {{ src_hash }} if tarball was used
  };

  propagatedBuildInputs = with python3Packages; [
    # copy&pasted requirements.txt (almost exactly)
    beautifulsoup4   # upstream version detection
    blessed          # terminal colors
    build            # apkg distribution
    cached-property  # for python <= 3.7; but pip complains even with 3.8
    click            # nice CLI framework
    distro           # current distro detection
    jinja2           # templating
    packaging        # version parsing
    pyyaml           # YAML for serialization
    requests         # HTTP for humans™
    setuptools       # required for build
    toml             # config files
  ];

  makeWrapperArgs = [ # deps for `srcpkg` operation for other distros; could be optional
    "--prefix" "PATH" ":" (lib.makeBinPath [ gitMinimal rpm dpkg fakeroot ])
  ];

  nativeCheckInputs = with python3Packages; [ pytest ];
  checkPhase = "py.test"; # inspiration: .gitlab-ci.yml; TODO: do more tests, probably

  meta = with lib; {
    description = "Upstream packaging automation tool";
    homepage = "https://pkg.labs.nic.cz/pages/apkg";
    license = licenses.gpl3Plus;
    maintainers = [ maintainers.vcunat /* close to upstream */ ];
  };
}
