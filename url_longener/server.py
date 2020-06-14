import socket
from controllers import *
from utils import write_code
from threading import Thread
HOST, PORT = '', 1008

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
# one connection a time!
listen_socket.listen(10)
print(f'Serving HTTP on port {PORT} ...')


def handle_resp(conn):
    request_data = conn.recv(1024).decode('utf-8').split()
    try:
        # get method, currently only support GET
        method = request_data[0]
        # remove all get params and #
        url = request_data[1].split("?")[0].split("#")[0]
        # default set response to 404
        http_response = write_code(404)

        # /
        if method == 'GET' and url == '/':
            # the func in controllers.py
            http_response = get_index(request_data, client_address)

        # /create_links_api
        if method == 'GET' and url == '/create_links_api':
            # the func in controllers.py
            http_response = create_links(request_data, client_address)

        # /redirect?location=https://google.com
        if method == 'GET' and url == '/redirect':
            # the func in controllers.py
            http_response = redirect(request_data, client_address)

    except Exception as e:
        # if not a http request, throw 500
        http_response = write_code(500)
    # send response
    conn.sendall(http_response.encode('utf-8'))
    conn.close()


while True:
    client_connection, client_address = listen_socket.accept()
    Thread(target=handle_resp, args=(client_connection, )).start()
