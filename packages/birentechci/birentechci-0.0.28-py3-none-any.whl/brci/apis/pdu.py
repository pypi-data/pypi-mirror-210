from os import urandom

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import functools
import signal


def timeout(sec):
    """
    timeout decorator
    :param sec: function raise TimeoutError after ? seconds
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):

            def _handle_timeout(signum, frame):
                err_msg = f'Function {func.__name__} timed out after {sec} seconds'
                raise TimeoutError(err_msg)

            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(sec)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapped_func
    return decorator


class PduWeb(object):
    def __init__(self, host, user, passwd) -> None:
        chrome_option = Options()
        chrome_option.add_argument("--no-sandbox")
        chrome_option.add_argument("--disable-dev-shm-usage")
        chrome_option.add_argument("--headless")
        self.host = host
        self.user = user
        self.passwd = passwd
        self.baseUrl = f"http://{host}"
        self.browser = webdriver.Chrome(options=chrome_option)
        self.wait = WebDriverWait(self.browser, 5)
        self.is_login = False
    @timeout(3)
    def login(self):
        url = "/"
        self.browser.get(self.baseUrl + url)
        input = self.browser.find_element(by=By.ID, value="login_username")
        input.send_keys(self.user)
        input = self.browser.find_element(by=By.ID, value="login_password")
        input.send_keys(self.passwd)
        input = self.browser.find_element(by=By.ID, value="login_but").click()
        self.wait.until(
            EC.presence_of_element_located((By.ID, "login_out_btn")), message="登录成功"
        )
        self.is_login = True

    def seat_list(self):
        if not self.is_login:
            self.login()
        out = []
        listEle = self.browser.find_elements(
            by=By.XPATH, value='//td[contains(@id,"td1_")]'
        )
        for one in listEle:
            seat = one.get_attribute("id").replace("td1_", "")
            name = one.text
            status = (
                "up"
                if self.browser.find_element(By.ID, value=f"td2_{seat}").get_attribute(
                    "class"
                )
                == "TdOnIco"
                else "down"
            )
            out.append(
                {
                    "seat": seat,
                    "name": name,
                    "status": status,
                    "host": self.host,
                }
            )
        return out

    def down_seat(self, seat):
        if not self.is_login:
            self.login()
        seat = self.browser.find_element(By.ID, value=f"td2_{seat}")
        status = "up" if seat.get_attribute("class") == "TdOnIco" else "down"
        if status != "down":
            seat.click()
        return

    def up_seat(self, seat):
        if not self.is_login:
            self.login()
        seat = self.browser.find_element(By.ID, value=f"td2_{seat}")
        status = "up" if seat.get_attribute("class") == "TdOnIco" else "down"
        if status == "down":
            seat.click()
        return

    def restart_seat(self, seat):
        if not self.is_login:
            self.login()

        def check_down(browser):
            return (
                browser.find_element(By.ID, value=f"td2_{seat}").get_attribute("class")
                == "TdOffIco"
            )

        def check_up(browser):
            return (
                browser.find_element(By.ID, value=f"td2_{seat}").get_attribute("class")
                == "TdOnIco"
            )

        self.down_seat(seat)
        self.wait.until(check_down, message="关闭成功")
        self.up_seat(seat)
        self.wait.until(check_up, message="开启成功")
