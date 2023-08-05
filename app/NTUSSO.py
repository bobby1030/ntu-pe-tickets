import requests as req
import logging
from bs4 import BeautifulSoup as bs

# NTU SSO 2.0 (SAML)
class NTUSSO:
    def __init__(self, username, password) -> None:
        self.endpoint = "https://adfs.ntu.edu.tw/adfs/ls/?wa=wsignin1.0&wtrealm=https://rent.pe.ntu.edu.tw/sso_login.php&wctx=RENT_PE&wct=2023-08-04CST21:45:37Z"
        self.username = username
        self.password = password
        self.logined = False

    def login(self):
        # set headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36",
        }

        # get ASP.NET viewstate
        login_page = req.get(self.endpoint, headers=headers)
        login_soup = bs(login_page.text, "html.parser")

        VIEWSTATE = login_soup.find(id="__VIEWSTATE")["value"]
        VIEWSTATEGENERATOR = login_soup.find(id="__VIEWSTATEGENERATOR")["value"]
        EVENTVALIDATION = login_soup.find(id="__EVENTVALIDATION")["value"]
        DB = login_soup.find("input", {"name": "__db"})["value"]

        # construct login form from viewstate
        login_form = {
            "__VIEWSTATE": VIEWSTATE,
            "__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
            "__EVENTVALIDATION": EVENTVALIDATION,
            "__db": DB,
            "ctl00$ContentPlaceHolder1$UsernameTextBox": self.username,
            "ctl00$ContentPlaceHolder1$PasswordTextBox": self.password,
            "ctl00$ContentPlaceHolder1$SubmitButton": "登入",
        }

        # login
        res = req.post(self.endpoint, data=login_form, headers=headers)

        # remote connection success
        if res.status_code == 200:
            # test if login successfully
            if "使用者名稱或密碼不正確" not in res.text:
                # login successfully
                logging.info("Login to NTU SSO successfully!")

                self.logined = True
                self.login_response = res

                login_res_soup = bs(res.text, "html.parser")
                tokens = login_res_soup.find_all("input")

                # save returned tokens
                self.tokens_form = {
                    t.get("name"): t.get("value")
                    for t in tokens
                    if t.get("name") != None
                }
            else:
                # login failed
                raise Exception(
                    "Login to NTU SSO failed! Check your username and password."
                )
        else:
            # remote connection failed
            raise Exception("Remote connection failed!")
