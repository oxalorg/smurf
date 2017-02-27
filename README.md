# smurf - a simple markdown surfer

Preview any folder on your pc using a website.

*Quick Demo*:

```
$ cd ~/project/smurf
$ smurf
Starting server http://localhost:3434
...
```

Now simply open `http://localhost:3434` in your web browser and
you can see a directory listing. You can open any files ending in 
`.md, .mkd, .markown, .txt` and they will be converted to html on-the-fly.

![smurf demo](https://raw.githubusercontent.com/oxalorg/smurf/master/demo.png)

Supports custom css, first it checks for a file named
`smurf.css` in the directory to be served. Then it checks
for a file in home directory `~/.smurf.css` (PS: note that the
file in the home directory starts with a dot)

## Usage:

```
smurf [PATH to Directory]
```

PS: Path to directory can be ommited to serve current
directory.

## Install

```
# Download the smurf script into your local bin folder
sudo wget "https://raw.githubusercontent.com/oxalorg/smurf/master/smurf.py" -O /usr/local/bin/smurf
# Make the script executable
sudo chmod a+x /usr/local/bin/smurf
# Download a simple css file for pretty webpages
wget "https://raw.githubusercontent.com/oxalorg/sakura/master/css/sakura.css" -O ~/.smurf.css
```

PS: `sakura.css` is another one of my projects, feel free to
check it out:
[https://github.com/oxalorg/sakura](https://github.com/oxalorg/sakura)

### Requirements

* Python 3
* Any one of the following markdown parsers
    - Pandoc
    - Markdown2 (`pip3 install --user markdown2`)
