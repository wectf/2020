PASSWORD = "bi6yQTB5nhBi7CaSMYF"

def check(selenium_obj, host):
    current_host = f"http://customer.{host}/"
    selenium_obj.get(current_host)
    selenium_obj.add_cookie({'name': 'token', 'value': PASSWORD, 'path': '/'})
