with import <nixpkgs> {};

(callPackage ./. { }).overrideAttrs (attrs: {
  src = ./apkg-ex-minimal-no-git-v{{ version }}.tar.gz;
})
