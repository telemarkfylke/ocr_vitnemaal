import requests
import os
import dotenv
import logging
from . import tokens

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

token = tokens.fetchToken(scope=os.environ.get("FREG_SCOPE"))
freg_url = os.environ.get("FREG_URL")

def checkSsn(ssn: str, navn: str) -> bool:
	"""
		Check the name of a ssn
		Returns:
			bool
	"""
	try:
		valid_ssn = ssn.replace(" ", "")
		if len(valid_ssn) != 11:
			logger.warning(f"FREG: Ugyldig fødselsnummer (lengde {len(valid_ssn)})")
			return False

		payload = {"ssn": valid_ssn}
		headers = {"Authorization": f"Bearer {token}"}
		response = requests.post(freg_url, json=payload, headers=headers)
		res = response.json()

		if res.get('status') is None:
			logger.warning(f"FREG: Ingen status i svar for oppslag")
			return False

		match = res['fulltnavn'] == navn
		if match:
			logger.info(f"FREG: Navn OK for fnr {valid_ssn[:6]}*****")
		else:
			logger.warning(f"FREG: Navn stemmer ikke — forventet '{navn}', fikk '{res['fulltnavn']}'")
		return match
	except Exception as e:
		logger.error(f"FREG: Oppslag feilet — {e}")
		return False

