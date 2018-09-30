CU Cyber Report Generator
=========================

In this repository is a penetration testing report generation tool.


## Dependencies

* make
* git
* python
* texlive-latexextra
* latexmk


### Debian/Ubuntu/Kali

```sh
$ sudo apt install make git texlive-latex-extra latexmk
```


### RedHat/CentOS

```sh
$ sudo yum install epel-release
$ sudo yum install make git texlive-collection-latexextra latexmk
```


### Fedora

```sh
$ sudo dnf install make git texlive-collection-latexextra latexmk
```


### Arch

```sh
$ sudo pacman -S make git texlive-latexextra latex-mk
```


### Gentoo

```sh
$ sudo emerge dev-vcs/git dev-texlive/texlive-latexextra dev-tex/latexmk
```


### macOS

Requires [Homebrew](https://brew.sh/). Use `gmake` instead of `make`.

```sh
$ brew install make git
$ brew cask install mactex
```


## Building

To build all of the reports into PDFs, create a markdown file like the `cyber.md` example and run `make`. The PDFs will be created in the same folder with the same name like `cyber.pdf` in the example.
