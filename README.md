[![Release Notes](https://img.shields.io/github/release/iloveitaly/ipython-copy)](https://github.com/iloveitaly/ipython-copy/releases)
[![Downloads](https://static.pepy.tech/badge/ipython-copy/month)](https://pepy.tech/project/ipython-copy)
![GitHub CI Status](https://github.com/iloveitaly/ipython-copy/actions/workflows/build_and_publish.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Copy Text, Variables, and History to Clipboard from IPython

I built this to solve a constant point of friction: getting data out of a remote or local REPL and into my system clipboard. This is a cross-platform IPython plugin that adds smart `%clip` and `%pickle` magic commands. It seamlessly handles both local GUI clipboards and headless remote SSH sessions.

## Installation

```bash
uv add ipython-copy
```

Once installed, load it in your IPython session:

```python
%load_ext ipython_copy
```

To load it automatically every time you start IPython, you can add it to your `ipython_config.py` in the `c.InteractiveShellApp.extensions` list.

## Usage

The plugin exposes a `%clip` magic command that tries to be smart about what you want to copy. It handles standard string inputs, looks up variables in your namespace, and can even reference your output history.

```python
# Copy the last output
%clip

# Copy the output from a specific history line
%clip 7

# Copy the string representation of a specific variable
%clip my_var

# Copy a literal string
%clip hello world
```

You can also use it as a cell magic to easily copy multi-line blocks of text:

```python
%%clip
Even multi
lines
work!
```

If you are dealing with complex data structures, use the `%pickle` magic to serialize Python objects directly to your clipboard and unpickle them later.

## Features

* Smart line magic (`%clip`) for copying the last output, history lines, or specific variables.
* Cell magic (`%%clip`) for cleanly copying multi-line blocks.
* `%pickle` magic to serialize and copy complex Python objects directly to the clipboard.
* Fully cross-platform using `pyperclip`.
* Automatic headless and remote server support via OSC 52 sequence fallbacks.

## Remote Environments and OSC 52

I frequently work in tmux on remote servers, which used to make clipboard access a nightmare. This plugin relies on `pyperclip`, which handles remote clipboard access automatically without you needing to configure anything. 

Here is how it works under the hood:

1. **Automatic Fallback:** By default, `pyperclip` uses `determine_clipboard()` to find a working backend. If it cannot find a local GUI clipboard (like `xclip`, `wl-clipboard`, or `pbcopy`) and it detects that it is running inside a terminal (by checking if the `TERM` environment variable is set and `sys.stdout` or `sys.stderr` is a TTY), it will automatically fall back to the new OSC 52 backend.
2. **Explicit Selection (Optional):** If you want to bypass GUI clipboards and force the use of OSC 52, you can explicitly set it in your Python code:
   ```python
   import pyperclip
   pyperclip.set_clipboard("osc52")
   ```

**The only external requirement:** While the library requires no configuration, your terminal emulator (e.g., iTerm2, Alacritty, Windows Terminal, Kitty) must support the OSC 52 escape sequence.
* Most modern terminals support it out of the box.
* Some terminals might have security settings that disable OSC 52 by default or prompt the user for permission the first time a script tries to write to the clipboard.

## Alternatives

* [IPythonClipboard](https://github.com/CarlosGTrejo/ipython_extensions/blob/master/ipython_clipboard/ipython_clipboard/__init__.py) - cannot copy a variable to the clipboard, only line numbers.
* [bwagner/clip.py](https://gist.github.com/bwagner/270da7c7d31af7ffaca32674557fc172) - can copy variables to clipboard, but relies on AppKit.
* [nova77/clip.py](https://gist.github.com/nova77/5403446) - the original script that this project iterated upon.

## [MIT License](LICENSE.md)

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*
