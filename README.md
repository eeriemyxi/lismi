# Lismi
A simple typing frontend for your terminal.

# State of the Project
This is in alpha stage. Do not use it.

# Features
- layout emulation
- color highlighting
- text alignment and text wrapping

# Command-Line Arguments
```
usage: lismi [-h] [-w WORD_COUNT] [-s] [-t TARGET_LAYOUT] [-e EMULATE_LAYOUT]
             [-V]

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
  -V, --version         Show program version.
```
