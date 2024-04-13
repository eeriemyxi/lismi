# Lismi

<p align="center">
    <img src="assets/demo.gif"
</p>

A simple typing frontend for your terminal.

# State of the Project
This is in beta stage. The experience is not guaranteed to be stable.

# Features
- layout emulation
- color highlighting
- text alignment and text wrapping

# Installation
### First Method
```bash
git clone --depth 1 --branch main <REPO URL> lismi
pip install ./lismi
```
### Second Method
```bash
pip install git+<REPO URL>@main
```

# Command-Line Arguments
```
usage: __main__.py [-h] [-w WORD_COUNT] [-W WORD_FILE] [-p] [-s] [-S]
                   [-t TARGET_LAYOUT] [-e EMULATE_LAYOUT] [-m MAX_SPACES] [-q]
                   [-V]

Lismi - A simple typing frontend for terminals.

options:
  -h, --help            show this help message and exit
  -w WORD_COUNT, --word-count WORD_COUNT
                        Number of words per test. Default: 20.
  -W WORD_FILE, --word-file WORD_FILE
                        Word file. Defaults (currently) to '/home/myxi/Documents
                        /coding/python/lismi/src/lismi/words/two-hundred.txt'.
  -p, --prepend-script-directory
                        Look for the word file in the script directory's
                        dedicated folder.
  -s, --skip-words      Space skips words.
  -S, --one-shot        Exit after first test.
  -t TARGET_LAYOUT, --target-layout TARGET_LAYOUT
                        Target layout. Default: 'qwerty'. Available: qwerty,
                        colemak.
  -e EMULATE_LAYOUT, --emulate-layout EMULATE_LAYOUT
                        Emulate layout. Default: 'qwerty'. Available: qwerty,
                        colemak.
  -m MAX_SPACES, --max-spaces MAX_SPACES
                        Max spaces per line. Default: 10. Minimum: 2.
  -q, --no-quick-end    Disable quickly ending test by ignoring last space.
                        Default: True.
  -V, --version         Show program version.
```
