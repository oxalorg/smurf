# smurf - a simple markdown surfer

Preview any folder on your pc using a website.

Converts any files ending in `.md, .mkd, .markown, .txt` into
html.

Supports custom css, first it checks for a file named
`smurf.css` in the directory to be served. Then it checks
for a file in home directory `~/.smurf.css` (PS: note that the
file in the home directory starts with a dot)

## Install

```
sudo wget https://github.com/oxalorg/smurf/blob/master/smurf.py -o /usr/local/bin/smurf
chmod a+x /usr/local/bin/smurf
```

## Usage:

```
smurf [PATH to Directory]
```

PS: Path to directory can be ommited to serve current directory.

## Requirements

* Python 3
* Any one of the following markdown parsers
    - Pandoc
    - Mistune (`pip3 install --user mistune`)
