import requests
from bs4 import BeautifulSoup, ResultSet
import bs4
import urllib.parse
import urllib
import typing
from urllib import parse
import typing
import re

KEYCLOAK = "https://profile.intra.42.fr/users/auth/keycloak_student"
SEND_FORM = "https://auth.42.fr/auth/realms/students-42/login-actions/authenticate"

class Token(typing.TypedDict):
	cookie:str
	expires:int

class Creds(typing.TypedDict):
	login:str
	password:str

class SSHKey(typing.TypedDict):
	key_name:str
	key_signature:str
	vogsphere:str
	synced:bool

class SraperError(Exception):
	pass

class IntraScraper:
	def __init__(self, creds:Creds = {}):
		self.token: Token
		self.creds = creds
		self.token = {}
		self.session = requests.session()

	def set_login(self, login:str):
		self.creds["login"] = login

	def set_password(self, password:str):
		self.creds["password"] = password

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
		for c in x.cookies:
			print(c.name, c.name == '_intra_42_session_production', c.expires)
			if c.name == '_intra_42_session_production':
				self.token["expires"] = c.expires
		self.token["cookie"] = cookie

	def do_request(self, f, *args, **kwargs):
		if ("cookies" in kwargs):
			kwargs["cookies"].update({"_intra_42_session_production":self.token["cookie"]})
		else:
			kwargs["cookies"] = {"_intra_42_session_production":self.token["cookie"]}
		return (f(*args, **kwargs))

SCRAPER = IntraScraper()

def get_all_notifs(scraper:IntraScraper = SCRAPER) -> typing.List[ResultSet[typing.Any]]:
	x = scraper.do_request(requests.get, "https://profile.intra.42.fr/notifications")
	soup = BeautifulSoup(x.content, "html.parser")


	pagination = soup.find("ul", {"class":"pagination"})
	last_page = pagination.find("li", {"class":"last"}).find("a")["href"]
	query = parse.parse_qs(parse.urlsplit("https://profile.intra.42.fr" + last_page).query)
	last_page = int(query["page"][0])


	all_notifs = soup.find_all("a", {"class":"notification-link"})
	for i in range(1, last_page + 1):
		x = scraper.do_request(requests.get, "https://profile.intra.42.fr/notifications", params={"page":i})
		soup = BeautifulSoup(x.content, "html.parser")
		all_notifs += soup.find_all("a", {"class":"notification-link"})
	return all_notifs


def __gitlab_get_necessary_data(scraper:IntraScraper = SCRAPER):
	GITLAB_URL = "https://profile.intra.42.fr/gitlab_users"
	x = scraper.do_request(requests.get, GITLAB_URL)
	soup = BeautifulSoup(x.content, "html.parser")
	auth = soup.find("meta", {"name":"csrf-token"})["content"]
	try:
		id = soup.find("a", {"class":"btn btn-danger btn-xs","rel":"nofollow","data-method":"delete"})["href"].split('/')[-1]
	except:
		id = None
	return (auth, id)

def get_ssh_key(scraper:IntraScraper = SCRAPER) -> SSHKey:

	GITLAB_URL = "https://profile.intra.42.fr/gitlab_users"
	if (id is None):
		return (None)
	x = scraper.do_request(requests.get, GITLAB_URL)
	soup = BeautifulSoup(x.content, "html.parser")


	try:
		name = soup.find("a", {"href":"#keymodal-365993"}).string.split("'")[1].strip()
	except:
		name = None

	tree_p = soup.find("div", {"id":"keymodal-365993"})
	print(tree_p.prettify())
	try:
		tree_values = tree_p.find("table").find_all("tr")[1].find_all("th", {"style":'font-weight: normal;'})
	except Exception as e:
		print("Couldn't get tree values :", e)
		return {"key_name":name, "key_signature":None, "vogsphere":None, "synced":None}
	try:
		signature = tree_values[0].string.strip()
	except Exception as e:
		print("Couldn't get 'signature' :", e)
		signature = None
	try:
		vogsphere = tree_values[1].contents[0].strip()
	except Exception as e:
		print("Couldn't get 'vogsphere' :", e)
		vogsphere = None
	try:
		synced = "text-success" in tree_values[1].find("span")["class"]
	except Exception as e:
		print("Couldn't get 'synced' :", e)
		synced = None

	return {"key_name":name, "key_signature":signature, "vogsphere":vogsphere, "synced":synced}


def delete_ssh_key(scraper:IntraScraper = SCRAPER) -> requests.Response | None:
	GITLAB_URL = "https://profile.intra.42.fr/gitlab_users"
	DEL_PAYLOAD = {"_method":"delete", "authenticity_token":""}

	auth_token, id = __gitlab_get_necessary_data(scraper)

	if (id is None):
		return (None)

	DEL_PAYLOAD["authenticity_token"] = auth_token
	x = scraper.do_request(requests.post, GITLAB_URL+f"/{id}", data=DEL_PAYLOAD)
	return (x)

def set_ssh_key(new_key:str, key_name="autogenerated", scraper:IntraScraper = SCRAPER):
	"""
	Requires you to have no current ssh key.
	"""
	GITLAB_URL = "https://profile.intra.42.fr/gitlab_users"
	auth_token, id = __gitlab_get_necessary_data(scraper)

	x = scraper.do_request(requests.post, GITLAB_URL,
			data={"authenticity_token":auth_token, "gitlab_user[public_key]":new_key, "gitlab_user[name]":key_name})
	return (x)

def get_clusters_map(scraper:IntraScraper = SCRAPER) -> requests.Response:
	return scraper.do_request(requests.get, "https://meta.intra.42.fr/clusters")


