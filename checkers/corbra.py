from requests import *


def demo_search(host):
    result = get(f"http://corbra.{host}/?needle=we&_action=search_html").content
    if b"<strong>we</strong>" not in result:
        return 0, "Cannot search 'we' for demo"
    result = get(f"http://corbra.{host}/?needle=we&_action=search_json").json()
    if result["result"][0] != "<strong>we</strong>{demoflag}<br>":
        return 0, "Wrong JSON result for 'we' in demo"
    result = get(f"http://corbra.{host}/?needle=we&limit=10&_action=search_json").content
    if b"<b>Warning</b>:  Limit is greater than length of array!" not in result:
        return 0, "Cannot bypass CORB"
    return 1, ""


def flag_search(host):
    header = {"Cookie": "admin_token=9pFrqCEyagsCbabGamT"}
    result = get(f"http://corbra.{host}/?needle=we&_action=search_html", headers=header).content
    if b"<strong>we</strong>" not in result:
        return 0, "Cannot search 'we' for demo"
    result = get(f"http://corbra.{host}/?needle=we{{54fce0d3-1d63-49e5-a8e"
                 f"d-220df8b23f07@cr033-0rIg1Nyyyyy}}&_action=search_json", headers=header).json()
    if len(result["result"]) < 0 or \
            result["result"][0] != "<strong>we{54fce0d3-1d63-49e5-a8ed-220df8b23f07@cr033-0rIg1Nyyyyy}</strong><br>":
        return 0, "No flag can be searched"
    result = get(f"http://corbra.{host}/?needle=we&limit=10&_action=search_json", headers=header).content
    if b"<b>Warning</b>:  Limit is greater than length of array!" not in result:
        return 0, "Cannot bypass CORB in admin mode"
    return 1, ""


FUNCTIONS = [flag_search, demo_search]

