import requests
import msal
import os
import dotenv
import tokens

dotenv.load_dotenv()

token = tokens.fetchToken(scope = os.environ.get("FREG_SCOPE"))
freg_url = os.environ.get("FREG_URL")

def checkSsn(ssn:str, navn:str) -> bool:
	"""
		Check the name of a ssn
		Returns:
			payload string
	"""
	payload= { "ssn":ssn }
	headers = {"Authorization": "Bearer "+token}
	response = requests.post(freg_url, json=payload, headers=headers)
	res =  response.json()

	if res['status'] is None:
		return False
	
	return res['fulltnavn'] == navn


