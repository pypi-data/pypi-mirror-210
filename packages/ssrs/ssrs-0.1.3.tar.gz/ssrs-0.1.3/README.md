# Description

This program enables you to run rust source files as scripts, from the command 
line, by prefixing them with a shebang line. It's useful because sometimes you 
just want to write a quick-and-dirty "script", without having to creaate a new 
crate/package.


# Installation

## With `pipx`
```sh
pipx install ssrs
```

## With `makepkg`
```sh
git clone "https://github.com/brunofauth/ssrs"
cd ssrs
makepkg -cris
```

# Usage

## From the Command Line
```sh
ssrs-cli [ssrs-options] -- <script-file> [script-options]
```

## From Script Files
```rust
#! /usr/bin/env ssrs

// your rust code here
fn main() {
    println!("Hello World!");
}
```

