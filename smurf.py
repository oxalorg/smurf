#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus
import shutil
import posixpath
import os
import sys
import urllib
import html
import io
import subprocess

css = ""

# find a valid markdown parser installed
while 1:
    pandoc = shutil.which('pandoc')
    if pandoc:
        markdown = lambda x: subprocess.run(
                    ["pandoc", "-f", "markdown", "-t", "html"],
                    input=x.encode("utf-8"),
                    stdout=subprocess.PIPE).stdout.decode("utf-8")
        break
    try:
        import mistune
        markdown = mistune.Markdown()
        break
    except ImportError:
        pass

    print("No markdown parser found. Exiting.. ")
    sys.exit(1)


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
            ctype = "text/html"
            content = f.read().decode("utf-8")
            content_html = markdown(content)
            new_f = io.BytesIO()
            shutil.copyfileobj(f, new_f)
            new_f.seek(0)
            f.close()
            r = []
            title = "TODO FIX"
            r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                     '"http://www.w3.org/TR/html4/strict.dtd">')
            r.append('<html>\n<head>')
            r.append('<meta http-equiv="Content-Type" '
                     'content="text/html; charset=utf-8">')
            r.append('<style>%s</style>' % css)
            r.append('<title>%s</title>\n</head>' % title)
            r.append('<body>\n<h1>%s</h1>' % title)
            r.append(content_html)
            r.append('</body></html>')
            new_f.write('\n'.join(r).encode("utf-8"))
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
        r = []
        try:
            displaypath = urllib.parse.unquote(
                self.path, errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<style>%s</style>' % css)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
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
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            os.chdir(path)
        else:
            print(path, " is not a valid directory")
            sys.exit(1)

    global css
    if os.path.isfile("smurf.css"):
        css = open("smurf.css").read()
    elif os.path.isfile(os.path.expanduser("~/.smurf.css")):
        css = open(os.path.expanduser("~/.smurf.css")).read()
    server_address = ('', 3434)
    httpd = HTTPServer(server_address, SmurfRequestHandler)
    print("Starting server http://localhost:3434")
    try:
        httpd.serve_forever()
    except:
        httpd.shutdown()
        httpd.server_close()


if __name__ == '__main__':
    main()
