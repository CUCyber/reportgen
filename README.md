CU Cyber Report Generator
=========================

In this repository is a penetration testing report generation tool.


## Dependencies

* make
* git
* python


### Debian/Ubuntu/Kali

```sh
$ sudo apt install make git
```


### RedHat/CentOS

```sh
$ sudo yum install make git
```


### Fedora

```sh
$ sudo dnf install make git
```


### Arch

```sh
$ sudo pacman -S make git
```


### Gentoo

```sh
$ sudo emerge dev-vcs/git
```


### macOS

Requires [Homebrew](https://brew.sh/). Use `gmake` instead of `make`.

```sh
$ brew install make git
```


## Building

To build all of the reports into PDFs, create a markdown file like the `cyber.md` example and run `make`. The PDFs will be created in the same folder with the same name like `cyber.pdf` in the example.
