{ lib, stdenv, fetchurl }:
stdenv.mkDerivation rec {
  pname = "apkg-ex-minimal-no-git";
  version = "{{ version }}";

  src = fetchurl { # or e.g. fetchFromGitHub, but that wouldn't give us src_hash
    url = "https://example.org/tarballs/${pname}-${version}.tar.gz";
    sha256 = "{{ src_hash }}";
  };

  installPhase = ''
    install -D -t "$out/bin" -m 775 ${pname}
  '';

  meta = with lib; { # it's all optional
    description = "Testing package containing a single script";
    homepage = "https://example.org";
    license = licenses.gpl3;
    platforms = platforms.all;
  };
}
