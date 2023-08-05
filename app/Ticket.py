import urllib.parse as parse
import segno
from bs4 import BeautifulSoup as bs


class Ticket:
    def __init__(self, soup, session) -> None:
        self.session = session
        self.from_soup(soup)

    def from_soup(self, ticket_soup):
        self.facility = ticket_soup.find(class_="TL").text
        self.type = ticket_soup.find(class_="CL").text
        self.infos = [
            info.text for info in ticket_soup.find(class_="CI").find_all("span")
        ]
        self.qr_token = ticket_soup.find(
            lambda tag: "進場使用" in tag.text and tag.name == "button"
        ).get("v")

        return self

    def get_qr_sn(self):
        qrsn = TicketQRSN(self.qr_token, self.session)
        self.qr_content = qrsn.qr_content
        self.sn = qrsn.sn

        return {
            "qr_content": self.qr_content,
            "sn": self.sn,
        }

    def get_qr_img(self):
        if not hasattr(self, "qr_content"):
            self.get_qr_sn()

        return segno.make(self.qr_content, error="L", version=11)

    def __str__(self) -> str:
        return f"{self.facility}, {self.type}, {self.infos}, {self.qr_token}"

    def __repr__(self) -> str:
        return f"{self.facility}, {self.type}, {self.infos}, {self.qr_token}"


class TicketQRSN:
    def __init__(self, qr_token, session) -> None:
        self.endpoint = "https://rent.pe.ntu.edu.tw/member/UseTicket.php"
        self.session = session
        self.qr_token = qr_token

        self.getTicketPage()

    def getTicketPage(self):
        res = self.session.get(self.endpoint, params={"V": self.qr_token})
        soup = bs(res.text, "html.parser")

        # get real qr content
        qr_src = soup.find(class_="QRCode").find("img").get("src")
        qr_content = parse.parse_qs(parse.urlsplit(qr_src).query)["Q"][0]
        self.qr_content = qr_content

        # get ticket serial number
        sn = soup.find(class_="TicketUseNo").text
        self.sn = sn
