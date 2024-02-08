from os import environ

BASE_URL = "/api/v1"
BASE_URL_LOG = "../logs/"

API_HOST = environ.get("API_HOST")
API_PORT = environ.get("API_PORT")
PREF_FARPOST = "/api/v1/farpost"

URL_API = f"http://{API_HOST}:{API_PORT}{PREF_FARPOST}/"
