with import <nixpkgs> {};

(callPackage ./. { }).overrideAttrs (attrs: {
  src = ./apkg-ex-template-variables-v{{ version }}.tar.gz;
})
