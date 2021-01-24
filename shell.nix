{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  nativeBuildInputs = (with pkgs; [
    gobject-introspection
    webkitgtk
    youtube-dl
  ]) ++ (with pkgs.python3Packages; [
    jsonschema
    mypy
    pygobject3
  ]);
  shellHooks = ''
    export GIO_EXTRA_MODULES=${pkgs.glib-networking}/lib/gio/modules
  '';
}
