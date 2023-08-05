import requests as req
import logging
from bs4 import BeautifulSoup as bs

from .Ticket import Ticket


# NTU PE Rental System
class RentPE:
    def __init__(self, NTUSSO, fakeID=False) -> None:
        self.SSO = NTUSSO
        self.endpoint = "https://rent.pe.ntu.edu.tw/sso_login.php"
        self.logined = False
        self.session = req.Session()

    def get_login_cookies(self):
        res = self.session.get(
            "https://rent.pe.ntu.edu.tw/sso2_go.php?BUrl=", allow_redirects=False
        )
        self.cookies = res.cookies

    def login(self):
        # check if already logined
        if self.logined:
            # session state is logined
            # check if token is still valid
            if self.check_logined():
                # token is still valid
                logging.info("Already logined!")
                return True
            else:
                # token is invalid
                # re-login
                logging.info("Token is invalid. Re-login...")
                self.logined = False

        # get login cookies first
        self.get_login_cookies()

        # login to SSO if not
        if not self.SSO.logined:
            self.SSO.login()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36",
        }

        tokens_form = self.SSO.tokens_form

        # use the cookies and login using SSO tokens
        res = self.session.post(self.endpoint, data=tokens_form, headers=headers)

        # check if login successfully
        if "帳號認證完成" in res.text:
            # success
            print("Login to rent.pe.ntu.edu.tw successfully!")
            self.logined = True
            self.login_response = res

            return True
        else:
            raise Exception(
                "Login to rent.pe.ntu.edu.tw failed! Check your username and password."
            )

    def check_logined(self):
        res = self.session.get("https://rent.pe.ntu.edu.tw/member/")

        # "登出" exists: Logined -> True
        # "登出" does not exists: Not logined -> False
        return "登出" in res.text

    def memberPage(self):
        # login if not
        if not self.logined:
            self.login()

        memberPage = self.session.get("https://rent.pe.ntu.edu.tw/member/")

        if "登出" in memberPage.text:
            print("Get logined member page successfully!")
            return memberPage
        else:
            raise Exception("Cannot get logined member page! Check your login status.")

    def get_tickets(self):
        # get member page
        memberPage = bs(self.memberPage().text, "html.parser")

        # get tickets list
        tickets_list = memberPage.find(class_="Ticketuse").find_all(class_="List")

        # return tickets list
        return [Ticket(t_soup, self.session) for t_soup in tickets_list]
