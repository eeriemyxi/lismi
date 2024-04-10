# Lismi
A simple typing frontend for your terminal.

# State of the Project
This is in alpha stage. Do not use it.

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
usage: lismi [-h] [-w WORD_COUNT] [-s] [-t TARGET_LAYOUT] [-e EMULATE_LAYOUT]
             [-m MAX_SPACES] [-V]

Lismi - A simple typing frontend for terminals.

options:
  -h, --help            show this help message and exit
  -w WORD_COUNT, --word-count WORD_COUNT
                        Number of words per test. Default: 20.
  -s, --skip-words      Space skips words.
  -t TARGET_LAYOUT, --target-layout TARGET_LAYOUT
                        Target layout. Default: 'qwerty'. Available: qwerty,
                        colemak.
  -e EMULATE_LAYOUT, --emulate-layout EMULATE_LAYOUT
                        Emulate layout. Default: 'qwerty'. Available: qwerty,
                        colemak.
  -m MAX_SPACES, --max-spaces MAX_SPACES
                        Max spaces per line. Default: 10. Minimum: 2.
  -V, --version         Show program version.
```
