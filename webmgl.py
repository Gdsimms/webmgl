#!/usr/bin/env python3
# A web server to echo back a request's headers and data.
#
# Usage: ./webserver
#        ./webserver 0.0.0.0:5000


# Note for python3 on mister, which is a minimal install
# you will need to execute:
# python -m ensurepip
# python -m pip install <prerequisites>


from asyncore import write
from http.server import HTTPServer, BaseHTTPRequestHandler
from sys import argv
import base64
import socket
import tempfile
import os


# From https://stackoverflow.com/a/28950776
# I used this because when I bound to 'localhost' or '127.0.0.1' I could not
# reach the server from another machine. I think this is likely not the optimal
# solution, and comes from my ignorance of how the HTTPRequestHandler really
# works at the network level. For instance, I do not know if I would be able
# to reach the machine externally via a hostname if it were in DNS.
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

#BIND_HOST = '127.0.0.1'
BIND_HOST = get_ip()
PORT = 8008


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if 'favicon.ico' not in self.path:
            self.write_response(self.path[1:].encode())

    def write_response(self, content):
        self.send_response(200)
        self.end_headers()
        success = False
        try:
            writeme = base64.urlsafe_b64decode(content)
            success = True
        except:
            writeme = "Invalid Base64 encoding.".encode()
        # Display text on requesting client
        self.wfile.write(writeme)

        # Print to local stdout
        print(writeme.decode())
        if success:
            launch(writeme.decode())

def launch(decoded):
    # If the decoded input is an valid filename (e.g. *.mra)
    if os.path.exists(decoded):
        print("Input appears to be a valid file.")
        fname = decoded
    else:
        # Assume the decoded input is the contents of an MGL file
        with tempfile.NamedTemporaryFile(mode='w') as f:
            fname = f.name
            f.write(decoded)
    # os.chdir("/media/fat/_Arcade/")
    os.system('echo "load_core ' + fname + '" > /dev/MiSTer_cmd')
    
if len(argv) > 1:
    arg = argv[1].split(':')
    BIND_HOST = arg[0]
    PORT = int(arg[1])

print(f'Listening on http://{BIND_HOST}:{PORT}\n')

httpd = HTTPServer((BIND_HOST, PORT), SimpleHTTPRequestHandler)
httpd.serve_forever()
