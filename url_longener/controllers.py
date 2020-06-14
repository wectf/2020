from utils import make_response
import html
import base64
import urllib.parse

links = {}


def prevent_oom():
    global links
    if len(str(links)) > 100000:
        links = {}


def beautify_arr(arr, server_host):
    content = ""
    for i in arr[::-1]:
        content += "http://%s/redirect?location=%s<br>" % (server_host, html.escape(i))
    return content


@make_response
def get_index(req):
    fingerprint = base64.b64encode(str(req).encode("utf-8"))
    try:
        # get such user's array
        result = links[fingerprint]
    except Exception as e:
        # if no link has been added
        result = []
    # send home page
    return 200, {}, open("index.html").read().replace("{{result}}", beautify_arr(result, req["host"]))


@make_response
def create_links(req):
    prevent_oom()
    # get the GET param: link
    location = req["params"]["link"]
    # no xss :)
    location = html.escape(location)
    # reset params so it could be consistent with following route for fingerprint generation
    req["params"] = []
    # generate fingerprint via req:
    """
    base64({
        "params": dict of get request params (e.g. {'x':1} for /?x=1)
        "authorization": str / user_token
        ...
        "body": not implemented yet
    })
    """
    fingerprint = base64.b64encode(str(req).encode("utf-8"))
    if fingerprint not in links:
        # if no link has been added
        links[fingerprint] = []
    # append link to such user's array
    links[fingerprint].append(location)
    return 302, {"Location": "/"}, "OK"


@make_response
def redirect(req):
    location = req["params"]['location']
    # no xss :)
    location = html.escape(urllib.parse.unquote(location))
    return 302, {"Refresh": "3; url=%s" % location}, "Redirecting you to %s in 3s..." % location

