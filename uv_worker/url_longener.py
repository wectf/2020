import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
IMPORTANT_DOC = "https://docs.google.com/document/d/1fSKalc75oJd9d3W3138r3oK1-pLPADbQnT9hfy1cZaw/edit?usp=sharing"
def check(selenium_obj, host):
    selenium_obj.get(f"http://url.{host}/")
    try:
        element = WebDriverWait(selenium_obj, 3).until(
            EC.presence_of_element_located((By.ID, "url"))
        )
    except:
        return
    element.send_keys(IMPORTANT_DOC)
    element.send_keys(Keys.RETURN)
    time.sleep(1)
