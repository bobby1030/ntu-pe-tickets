from decouple import config

from app.NTUSSO import NTUSSO
from app.RentPE import RentPE

NTUID = config("NTUID")
NTUPASSWORD = config("NTUPASSWORD")

SSO = NTUSSO(NTUID, NTUPASSWORD)
RentPE = RentPE(SSO)
RentPE.login()

tickets = RentPE.get_tickets()

tickets[0].get_qr_sn()