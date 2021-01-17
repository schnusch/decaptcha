{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  nativeBuildInputs = (with pkgs; [
    electron
    gnumake
    nodejs
    openssl
  ]) ++ (with pkgs.nodePackages; [
    npm
  ]);
}
