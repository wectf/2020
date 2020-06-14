USER_OBJ = open("uv_worker/na3_obj.txt").read()
FLAG = "we{10cc984b-2a34-4cdc-88fa-4190d4b2ce19@c00l-hassSsh}"

def check(selenium_obj, host):
    current_host = f"http://na3.{host}/"
    selenium_obj.get(current_host)
    selenium_obj.execute_script("localStorage.setItem('safe_mode', '1')")
    selenium_obj.add_cookie({'name': 'flag', 'value': FLAG, 'path': '/'})
