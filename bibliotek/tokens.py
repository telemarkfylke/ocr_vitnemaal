
import msal
import os
import dotenv

dotenv.load_dotenv()

freg_url = os.environ.get("FREG_URL")

def fetchToken(scope:str) -> str:
	"""
		Get the token for the freg api
		Returns:
			token string
	"""
	client_id = os.environ.get("APPREG_CLIENT_ID")
	client_secret = os.environ.get("APPREG_CLIENT_SECRET")
	tenant_id = os.environ.get("APPREG_TENANT_ID")
	scopes = [scope]
	authority = 'https://login.microsoftonline.com/'+str(tenant_id)+'/'

	app = msal.ConfidentialClientApplication(
    client_id=client_id,
    authority=authority,
    client_credential=client_secret,
	)
	result = None
	result = app.acquire_token_silent(scopes, account=None)

	if not result:
		result = app.acquire_token_for_client(scopes)

	if "access_token" in result:
		print("Access token acquired successfully!")
		return result['access_token']
	
	else:
		print("Token acquisition failed.")