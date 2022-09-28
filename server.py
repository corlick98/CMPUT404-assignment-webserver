#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Christopher Orlick
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
def get_request_line(request_string):
    return request_string.split()[0:3]

def path_is_legal(parent_path, child_path):
    # Credit to https://stackoverflow.com/a/37095733
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    # Compare the common path of the parent and child path with the common path of just the parent path. 
    # Using the commonpath method on just the parent path will regularise the path name in the same way 
    # as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def result_405():
    return """HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\nConnection: Closed\r\n
<html>
    <head>
        <title>405 Method Not Allowed</title>
    </head>
    <body>
        <h1>Method Not Allowed</h1>
    </body>
</html>"""

def result_404():
    return """HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nConnection: Closed\r\n
<html>
    <head>
        <title>404 Not Found</title>
    </head>
    <body>
        <h1>Not Found</h1>
    </body>
</html>"""

def result_301(new_loc):
    return """HTTP/1.1 301 Moved Permanently\r\nContent-Type: text/html\r\nConnection: Closed\r\nLocation: {new_loc}\r\n
<html>
    <head>
        <title>301 Moved Permanently</title>
    </head>
    <body>
        <h1>Moved Permanently<h1>
        The document has moved <a href="{new_loc}">here</a>.
    </body>
</html>
""".format(new_loc=new_loc)

def result_200(path):
    file_type = path.split('.')[-1].split('/')[0]
    file_size = os.path.getsize(path)
    with open(path, 'r') as f:
        header = "HTTP/1.1 200 OK\r\nContent-Type: text/{}\r\nContent-Size: {}\r\nConnection: Closed\r\n\n".format(file_type, file_size)
        return header + f.read()



def _handler(method, path):
    if method != 'GET':
        return result_405()
    current_location = os.path.dirname(os.path.abspath(__file__))+'/www'
    full_path = current_location + path
    if not path_is_legal(current_location, full_path):
        return result_404()
    if os.path.isfile(full_path):
        return result_200(full_path)
    elif os.path.isdir(full_path):
        if full_path[-1] == "/": #return index.html
            return result_200(full_path+"index.html")
        else:
            return result_301(path+"/")
    return result_404()

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        data_string = self.data.decode()
        method, path, version = get_request_line(data_string)
        response = _handler(method, path)
        self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
