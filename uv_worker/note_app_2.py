PASSWORD = "Lq#QHMnpyk6Y+.]"


def check(selenium_obj, host):
    current_host = f"http://na2.{host}/"
    selenium_obj.get(current_host)
    selenium_obj.add_cookie({'name': 'token', 'value': PASSWORD, 'path': '/'})
