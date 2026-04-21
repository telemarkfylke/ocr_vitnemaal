import msal
import os
import dotenv
import logging

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

def fetchToken(scope: str) -> str:
	"""
		Get the token for the freg api
		Returns:
			token string
	"""
	client_id = os.environ.get("APPREG_CLIENT_ID")
	client_secret = os.environ.get("APPREG_CLIENT_SECRET")
	tenant_id = os.environ.get("APPREG_TENANT_ID")
	scopes = [scope]
	authority = f"https://login.microsoftonline.com/{tenant_id}/"

	app = msal.ConfidentialClientApplication(
		client_id=client_id,
		authority=authority,
		client_credential=client_secret,
	)
	result = app.acquire_token_silent(scopes, account=None)

	if not result:
		result = app.acquire_token_for_client(scopes)

	if "access_token" in result:
		logger.info(f"Token hentet OK for scope: {scope}")
		return result['access_token']
	else:
		logger.error(f"Token-henting feilet for scope: {scope} — feil: {result.get('error_description', 'ukjent')}")
		return None