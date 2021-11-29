# Ex 4.4 - HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

import os
import socket

DEFAULT_URL = "index.html"
HTML_HEADER = "Content-Type: text/html; charset=utf-8\r\n"
IMAGE_HEADER = "Content-Type: image/jpeg\r\n"
ICON_HEADER = "Content-Type: image/x-icon\r\n"
JS_HEADER = "Content-Type: text/javascript; charset=UTF-8\r\n"
CSS_HEADER = "Content-Type: text/css\r\n"
HTTP_RES_HEADER_OK = " 200 OK\r\n"
HTTP_RES_HEADER_404 = " 404 NOT FOUND\r\n"
HTTP_RES_HEADER_302 = " 302 FOUND\r\n"
HTTP_RES_HEADER_403 = " 403 FORBIDDEN\r\n"
HTTP_RES_HEADER_500 = " 500 INTERNAL SERVER ERROR\r\n"
FIXED_RESPONSE = "HTTP/1.0"
REDIRECTION_DICTIONARY = {"test.html": "REDIRECTION_DICTIONARY_TEST/test.html", "admin": 'admin/admin_page.html'}
NO_ACCESS = ['admin/admin_page.html']

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1


def get_file_data(file):
    """ Get data from file """
    with open(file, 'rb') as f:
        return f.read()


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    try:
        http_header = ""    # init
        data = b''  # init

        if resource == '':
            url = DEFAULT_URL
        else:
            url = resource
        url = url.lower()   # to avoid loopholes

        if url in REDIRECTION_DICTIONARY:
            # send 302 redirection response
            http_header += HTTP_RES_HEADER_302 + "location: " + REDIRECTION_DICTIONARY[url] + '\r\n'

        elif url in NO_ACCESS:
            # send 403 NO ACCESS response
            http_header += HTTP_RES_HEADER_403

        elif not os.path.isfile(url):
            # send 404 NOT FOUND response
            http_header += HTTP_RES_HEADER_404
        else:
            # extract requested file type from URL (html, jpg etc)
            http_header += HTTP_RES_HEADER_OK
            filename, filetype = os.path.splitext(url)
            if filetype == '.html':
                http_header += HTML_HEADER
            elif filetype == '.jpg':
                http_header += IMAGE_HEADER
            elif filetype == '.ico':
                http_header += ICON_HEADER
            elif filetype == '.js':
                http_header += JS_HEADER
            elif filetype == '.css':
                http_header += CSS_HEADER

            data = get_file_data(url)

        http_response = (http_header + "\r\n").encode() + data
        client_socket.send(http_response)
    except Exception as ex:
        http_response = (HTTP_RES_HEADER_500 + "\r\n").encode()
        client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    # request = str(request)
    req_lines = request.split('\r\n')
    req_first_row_words = req_lines[0].split(' ')
    try:
        if len(req_first_row_words) == 3:
            if req_first_row_words[0] == 'GET':
                if req_first_row_words[1].startswith("/"):  # resource string should start at /
                    req_first_row_words[1] = req_first_row_words[1][1:]  # remove the /
                    http_version_words = req_first_row_words[2].split('/')
                    if len(http_version_words) == 2:
                        if http_version_words[0] == 'HTTP':
                            # if http version is number (include float).
                            if http_version_words[1].replace('.', '', 1).isdigit():
                                return True, req_first_row_words[1]
    except Exception as ex:
        return False, "ERROR: " + str(ex)
    return False, "ERROR"


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    client_socket.send(FIXED_RESPONSE.encode())
    while True:
        # receive client request
        try:
            client_request = client_socket.recv(1024).decode()
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print('Got a valid HTTP request', str(resource))
                handle_client_request(resource, client_socket)
                break
            else:
                print('Error: Not a valid HTTP request')
                break
        except Exception as ex:
            return
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
