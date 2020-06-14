from requests import *
import utils


def check(host):
    s = session()
    # reg
    result = s.post(f"http://customer.{host}/", data={
        "username": utils.randomString(),
        "password": "9pFrqCEyagsCbabGamT"
    }).content
    if b"You are not eligible to view flag!" not in result:
        return 0, "Failed to login"

    # check promote
    result = s.post(f"http://customer.{host}/promote", data={
        "user_token": "123"
    }).content
    if b"Not Admin..." not in result:
        return 0, "Wrong result of plebian promotion"

    # admin promotion
    headers = {"cookie": "token=bi6yQTB5nhBi7CaSMYF"}
    result = post(f"http://customer.{host}/promote", data={
        "user_token": s.cookies.get("token")
    }, headers=headers).content
    result = s.get(f"http://customer.{host}/").content
    if b'we{3d090a68-02bf-4e6d-b2d7-3d9db9a2f6f1@p00r-A6m1n}' not in result:
        return 0, "Failed to get flag"
    return 1, ""

FUNCTIONS = [check]

if __name__ == "__main__":
    print(check("w-va.cf"))