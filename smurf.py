#!/usr/bin/env python3
"""
smurf - a simple markdown surfer

Authors:
    Mitesh Shah <mitesh@oxal.org>

Repository:
    https://github.com/oxalorg/smurf
"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus
import shutil
import posixpath
import os
import argparse
import sys
import urllib
import html
import io
import subprocess
from string import Template

BASE_TEMPLATE = Template("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <style>${css}</style>
    <title>${title}</title>
</head>
<body>
    <p>${title}</p>
    <hr>
    ${content}
</body>
</html>
""")


def get_markdown():
    """
    Find and set a valid markdown parser
    Checks for one of these parsers:
        - pandoc
        - markdown2
    """
    markdown = None
    if shutil.which('pandoc'):
        markdown = lambda x: subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html"],
            input=x.encode("utf-8"),
            stdout=subprocess.PIPE).stdout.decode("utf-8")
    else:
        try:
            import markdown2
            _md_extras = [
                "code-friendly",
                "fenced-code-blocks",
                "footnotes",
                "header-ids",
            ]
            markdown = markdown2.Markdown(extras=_md_extras).convert
        except ImportError:
            pass

    if markdown is None:
        print("No markdown parser found. Will serve as plain text.")
    return markdown


def get_css():
    css = ""
    if os.path.isfile("smurf.css"):
        css = open("smurf.css").read()
    elif os.path.isfile(os.path.expanduser("~/.smurf.css")):
        css = open(os.path.expanduser("~/.smurf.css")).read()
    return css


CSS, MARKDOWN = get_css(), get_markdown()

class SmurfRequestHandler(SimpleHTTPRequestHandler):
    md_ext = (".txt", ".md", ".markdown", ".mkd")

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/', parts[3],
                             parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in ["index" + ext for ext in self.md_ext]:
                # if a markdown file named "index" is available in
                # a directory, display that instead of the default
                # directory listing
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        base, ext = posixpath.splitext(path)
        if ext in self.md_ext:
            # replace the contents of the markdown file
            # with HTML before passing it to our http server
            ctype = "text/html"
            content = f.read().decode("utf-8")
            content_html = MARKDOWN(content)
            new_f = io.BytesIO()
            shutil.copyfileobj(f, new_f)
            new_f.seek(0)
            f.close()
            title = 'Current file: %s' % path
            r = BASE_TEMPLATE.substitute(css=CSS, content=content_html, title=title)
            new_f.write(r.encode("utf-8"))
            f = new_f
        else:
            ctype = self.guess_type(path)
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            #fs = os.fstat(f.fileno())
            #self.send_header("Content-Length", str(fs[6]))
            #self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            f.seek(0)
            return f
        except:
            f.close()
            raise

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND,
                            "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())

        try:
            displaypath = urllib.parse.unquote(
                self.path, errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath

        # form the content response i.e. index of the directory
        r = []
        r.append('<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<li><a href="%s">%s</a></li>' % (urllib.parse.quote(
                linkname, errors='surrogatepass'), html.escape(
                    displayname, quote=False)))
        r.append('</ul>')
        r = BASE_TEMPLATE.substitute(content='\n'.join(r), css=CSS, title=title)
        encoded = r.encode(enc, 'surrogateescape')

        # transform the encoded content to a file like object
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f


def cli():
    parser = argparse.ArgumentParser(
        description="a simple markdown surfer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('dir', help="folder to serve", nargs='?', default=os.getcwd())
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(args.dir, " is not a valid directory")
        sys.exit(1)

    os.chdir(args.dir)


def main():
    cli()
    server_address = ('', 3434)
    httpd = HTTPServer(server_address, SmurfRequestHandler)
    print("Starting server at http://localhost:3434")
    try:
        httpd.serve_forever()
    except:
        httpd.shutdown()
        httpd.server_close()


if __name__ == '__main__':
    main()
