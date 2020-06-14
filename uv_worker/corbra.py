  
PASSWORD = "9pFrqCEyagsCbabGamT"


def check(selenium_obj, host):
    current_host = f"https://corbra.cf/"
    selenium_obj.get(current_host)
    selenium_obj.add_cookie({'name': 'admin_token', 'value': PASSWORD, 'path': '/'})
