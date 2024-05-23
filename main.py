import socket
import ssl

import re


def url_parts(url: str) -> (str, str):
    """
    Returns tuple of hostname and relative path.
    """

    pattern = re.compile(r"(http://)|(https://)([^/\s]+)(/[^\s]*)?")
    result = pattern.findall(url)

    hostname = result[0][2]
    relative_path = result[0][3]

    if relative_path == "":
        relative_path = "/"

    return (hostname, relative_path)


def extract_response(response: bytes) -> (bytes, bytes):
    """
    Returns tuple of header and response body.
    """

    # In HTTP request header is terminated by double CRLF line breaks.
    headers, body = response.split(b"\r\n\r\n", 2)
    return (headers, body)


def fetch(url: str, method: str) -> (bytes, bytes):
    """
    Makes network request and returns http header and body.
    """

    if method != "GET":
        raise NotImplementedError(f"The request method {method} is not implemented yet.")

    hostname, relative_path = url_parts(url)

    # Creates ssl context
    ssl_context = ssl.create_default_context()
    sock = socket.create_connection((hostname, 443))

    ssl_sock = ssl_context.wrap_socket(sock, server_hostname=hostname)

    # Request headers
    # Each header line ends with CRLF line break.
    # Http version 1.0
    request_header = f"{method} {relative_path} HTTP/1.0\r\n".encode()
    request_header += f"Origin: {hostname}\r\n".encode()
    request_header += f"Host: {hostname}\r\n".encode()
    request_header += b"\r\n\r\n"  # Request header ends

    # Writes request to the socket
    ssl_sock.write(request_header)

    response = b""

    while True:
        # Read 1024 bytes if possible
        chunk = ssl_sock.recv(1024)
        if len(chunk) == 0:
            # In http 1.0 server terminates connection when all request body is received.
            break

        response += chunk

    ssl_sock.close()
    sock.close()
    return extract_response(response)


# Test image download
test_url = "https://play-lh.googleusercontent.com/2gk4MOJoUf_yqndIXUxiVuVSFhecQBReW1jbZyEvKVU3nslC66_0l1iBFggqPjbkiA"

_, response = fetch(test_url, "GET")
with open("icon.png", "wb") as file:
    file.write(response)

print("Image saved.")
