#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Dennea MacCallum
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it
# Copyright 2023 Dennea MacCallum

import sys
import socket
# you may use urllib to encode data appropriately
# reference: https://docs.python.org/3/library/urllib.parse.html

from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        end_index = data.find('\r\n\r\n')
        return data[:end_index].strip()

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
            # parse the url
            parsed_url = urlparse(url)
            host = parsed_url.hostname
            path = parsed_url.path if parsed_url.path else '/'
            port = parsed_url.port

            if not port:
                port = 80 if parsed_url.scheme == 'http' else 443

            self.connect(host, port)

            # check for arguments and add them to the path
            if args:
                query = urlencode(args)
                path = f"{path}?{query}"

            # make sure to close the network connection after request is complete
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            self.sendall(request)
            
            recv = self.recvall(self.socket)
            self.close()

            code = self.get_code(recv)
            body = self.get_body(recv)
            print(recv)

            return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #parse the url
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        path = parsed_url.path if parsed_url.path else '/'
        port = parsed_url.port
        data = ''

        if not port:
            port = 80 if parsed_url.scheme == 'http' else 443

        self.connect(host, port)

        # check for arguments
        if args:
            data = urlencode(args)

        request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(data)}\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\n\r\n{data}"
        self.sendall(request)
        
        recv = self.recvall(self.socket)
        self.close()

        code = self.get_code(recv)
        body = self.get_body(recv)
        print(recv)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
