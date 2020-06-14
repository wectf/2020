from requests import *
import utils
import re

match_ids = re.compile("href=\"/note/(.+?)\">")

def check(host):
    s = session()
    # reg
    result = s.post(f"http://na2.{host}/", data={
        "username": utils.randomString(),
        "password": "9pFrqCEyagsCbabGamT"
    }).content
    if b"Welcome to our super-duper-duper safe note app!" not in result:
        return 0, "Failed to login"

    # add note
    result = s.post(f"http://na2.{host}/add_note", data={
        "content": "<script>alert(1)</script>",
        "xsrf": s.cookies.get("token")
    }).content
    if b"Note ID: " not in result:
        return 0, "Wrong result of add note"

    # test xss
    note_id = match_ids.findall(str(result))[0]
    result = s.get(f"http://na2.{host}/note/{note_id}").content
    if b"<script>alert(1)</script>" not in result:
        return 0, "Cannot trigger XSS"

    # test logout
    s.post(f"http://na2.{host}/logout")

    if "token" in s.cookies:
        return 0, "Logout failed"

    # test admin
    result = s.post(f"http://na2.{host}/", data={
        "username": "admin",
        "password": "Lq#QHMnpyk6Y+.]"
    }).content

    # admin flag
    result = s.get(f"http://na2.{host}/note/1").content
    if b'we{f93486a2-4f82-42b6-8dc8-04cd765501f3@1nsp1reD-bY-cHa1I-1N-BbC7F}' not in result:
        return 0, "Failed to get flag"
    return 1, ""

FUNCTIONS = [check]
if __name__ == "__main__":
    print(check("w-va.cf"))