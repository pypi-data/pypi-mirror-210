import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib
import typing
import os
import base64

KEYCLOAK = "https://profile.intra.42.fr/users/auth/keycloak_student"
SEND_FORM = "https://auth.42.fr/auth/realms/students-42/login-actions/authenticate"

class IntraScraper:
	def __init__(self, creds: typing.Dict[str,str]):
		self.creds = creds
		self.session = requests.session()
		self.token = self.get_token()

	def get_token(self) -> str:
		response = self.session.get(KEYCLOAK)
		connect_page = response.content

		soup = BeautifulSoup(connect_page, "html.parser")
		form = soup.find("form", {"id": "kc-form-login"})
		send_forms_params = {t[0]:t[1] for t in urllib.parse.parse_qsl(form["action"].split('?')[1])}

		data = urllib.parse.urlencode({"username":self.creds['login'], "password":self.creds['password']})
		x = self.session.post(SEND_FORM,
			data=data,
			headers=self.session.headers.update({
				"Content-Type" : "application/x-www-form-urlencoded",
				"Content-Length":f"{len(data)}"
				}),
			params=send_forms_params)

		cookie = x.cookies.get("_intra_42_session_production")
		return (cookie)

	def do_request(self, f, *args, **kwargs):
		if ("cookies" in kwargs):
			kwargs["cookies"].update({"_intra_42_session_production":self.token})
		else:
			kwargs["cookies"] = {"_intra_42_session_production":self.token}
		return (f(*args, **kwargs))

login = os.environ["INTRA_LOGIN"]
pswd = base64.b64decode(os.environ["INTRA_PASS"]).decode("utf-8")

SCRAPER = IntraScraper(
	{"login":login, "password":pswd}
)