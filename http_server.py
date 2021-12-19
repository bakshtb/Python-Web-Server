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
CONTENT_LENGTH = "Content-length: "

IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1


def get_file_data(file):
    """ Get data from file """
    with open(file, 'rb') as f:
        return f.read()


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    try:
        http_header = ""  # init
        data = b''  # init

        if resource == '':
            url = DEFAULT_URL
        else:
            url = resource
        url = url.lower()  # to avoid loopholes

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

        http_response = (http_header + CONTENT_LENGTH + str(len(data)) + "\r\n\r\n").encode() + data
        client_socket.send(http_response)
    except Exception as ex:
        http_response = (HTTP_RES_HEADER_500 + CONTENT_LENGTH + "0" + "\r\n\r\n").encode()
        client_socket.send(http_response)
        print("ERROR", ex)


def is_valid_protocol(_str):
    """
    Checks if a string is a valid HTTP protocol.
    For example: HTTP/1.1 is valid and HTTP-1.1 and HTTS/1.1 is not valid.
    """
    http_version_words = _str.split('/')
    if len(http_version_words) == 2:  # (after '/' split)
        if http_version_words[0] == 'HTTP':
            if http_version_words[1].replace('.', '', 1).isdigit():  # if http version is number (include float).
                return True
            else:
                return False


def is_valid_resource(_str):
    """
    The function checks whether the string may be a correct resource.
    In other words - if the string start with '/'
    If the string is correct it will return the resource without the '/'
    """
    if _str.startswith("/"):  # resource string should start at /
        res = _str[1:]  # remove the /
        return True, res
    else:
        return False, None


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    req_lines = request.split('\r\n')
    req_first_row_words = req_lines[0].split(' ')
    try:
        if len(req_first_row_words) == 3:
            method, resource, protocol = req_first_row_words
            if method == 'GET':
                _is_valid_resource, _resource = is_valid_resource(resource)
                if _is_valid_resource:
                    if is_valid_protocol(protocol):
                        return True, _resource

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
