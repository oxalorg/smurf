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
for a file in home directory `~/.smurf.css`.

CSS is provided by sakura, a simple css theme: 
[https://github.com/oxalorg/sakura](https://github.com/oxalorg/sakura)

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

# Download a simple css file for pretty webpages [1]
wget "https://raw.githubusercontent.com/oxalorg/sakura/master/css/sakura.css" -O ~/.smurf.css
```

Now if you don't have pandoc installed, you'll have to download
a markdown parser which is as easy as:

```
pip3 install --user markdown2
# make sure Python user bin directory is in your path,
# other wise you can also install like this:
# sudo pip3 install markdown2
```

### Requirements

* Python 3
* Any one of the following markdown parsers
    - Pandoc
    - Markdown2 (`pip3 install --user markdown2`)
