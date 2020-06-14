from collections import defaultdict
import time
import jwt
import uuid
import os
server_secret_key = str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4())
"""
decorator that changes request payload in dict:
{
    "params": dict of get request params (e.g. {'x':1} for /?x=1)
    "authorization": str / user_token
    ...
    "body": not implemented yet
}
and parse code, headers, content returned by func to raw http response
"""
def make_response(func):
    def wrapper(req, client_addr):
        result = ''
        parse_request = parse_req(req, client_addr)
        if not parse_request:
            result += write_code(500)
            return result
        try:
            if parse_request["token"] == '' or parse_request["token"] == 'WRONG_TOKEN':
                parse_request["token"] = str(uuid.uuid4())
            code, headers, content = func(parse_request)
            result += write_code(code)
            headers["Set-Cookie"] = "url_longener_auth=%s" % generate_new_authorization(parse_request).decode("utf-8")
            result += write_header(headers)
            result += '\r\n' + content
        except Exception as e:
            print(e)
            result += write_code(500)
            result += write_header({})
            result += '\r\n'
        return result
    return wrapper


def get_authorization(req):
    try:
        cookies = req[req.index("Cookie:") + 1:]
        for i in cookies:
            if "url_longener_auth" in i:
                return jwt.decode(i.split("=")[1], server_secret_key, algorithms=['HS256'])['token']
        return ""
    except Exception as e:
        print(e)
        return "WRONG_TOKEN"

def get_host(req):
    try:
        return req[req.index("Host:") + 1]
    except Exception as e:
        print(e)
        return ""

def get_first_ua(req):
    try:
        # only take the first section of ua
        return req[req.index("User-Agent:") + 1]
    except Exception as e:
        print(e)
        return ""

# https://totaluptime.com/kb/how-can-i-obtain-the-original-client-ip-address-all-connections-from-the-cloud-load-balancer-seem-to-come-from-the-same-few-ip-addresses/
def get_ip(req, client_addr):
    try:
        # get actual ip of user when behind nginx
        return req[req.index("X-Forwarded-For:") + 1]
    except Exception as e:
        return client_addr[0]


def get_params(req):
    if len(req[1].split("?")) <= 1:
        return []
    content_after_question_mark = req[1].split("?")[1]
    params = defaultdict(str)
    for x in content_after_question_mark.split("&"):
        try:
            (k,v) = x.split("=")
            params[k] = v
        except Exception as e:
            print(e)
    return params


def parse_req(req, client_addr):
    if len(req) < 3:
        return None
    return {
        "params": get_params(req),
        "token": get_authorization(req),
        "ip": get_ip(req, client_addr),
        "ua": get_first_ua(req),
        "host": get_host(req)
    }


def write_code(code):
    if code == 200:
        return "HTTP/1.1 200 OK\r\n"
    if code == 404:
        return "HTTP/1.1 404 NOT FOUND\r\n"
    if code == 403:
        return "HTTP/1.1 403 FORBIDDEN\r\n"
    if code == 500:
        return "HTTP/1.1 500 INTERNAL SERVER ERROR\r\n"
    if code == 302:
        return "HTTP/1.1 302 FOUND\r\n"
    return "HTTP/1.1 204 NO CONTENT\r\n"


COMMON_HEADERS = {
    "Server": "Shou's little python server"
}


def write_header(headers):
    result = ""
    all_headers = {**COMMON_HEADERS, **headers}
    for k in all_headers:
        result += "%s: %s\r\n" % (k, all_headers[k].replace("\\r", "\r").replace("\\n", "\n"))
    return result


def generate_new_authorization(req):
    return jwt.encode({'time': int(time.time()), 'token': req["token"]}, server_secret_key, algorithm='HS256')

