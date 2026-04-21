from typing import List
from datetime import datetime
from dataclasses import dataclass, asdict
import requests
import msal
import os
import dotenv
from . import tokens


@dataclass
class HpContact:
	ReferenceNumber:str
	Role:str
	IsUnofficial:str

@dataclass
class HpFile:
	Base64Data:str
	Category:str
	Format:str
	Status:str
	Title:str
	VersionFormat:str

@dataclass
class HpParameter:
	Category:str
	Contacts:List[HpContact]
	Files:List[HpFile]
	Status:str
	DocumentDate:datetime
	UnofficialTitle:str
	Title:str
	Archive:str
	CaseNumber:str
	ResponsibleEnterpriseRecno:str
	AccessCode:str
	Paragraph:str
	AccessGroup:str

@dataclass
class HpPayload:
	service:str
	method:str
	parameter: HpParameter

dotenv.load_dotenv()

environment = os.environ.get("ENVIRONMENT")
archive_url = os.environ.get("ARCHIVE_URL")

token = tokens.fetchToken(scope = os.environ.get("ARCHIVE_SCOPE"))

def lag_hovedprosjekt_arkiv_payload(base64Data:str, elevnavn:str, ssn:str) -> str:
	"""
		Get the Payload to be sent to the archive for hovedprosjekt .
		Returns:
			payload string
	"""

	if environment=="PROD":
		recno = "215093"
	else:
		recno = "200314"

	# Retrieve the casenumber for the ssn
	case_response = getCaseNumber(ssn)
	casenr:str = case_response['elevmappe']['CaseNumber']


	data = HpPayload(
		service = "DocumentService",
		method = "CreateDocument",
		parameter = HpParameter(
			Category="Dokument ut",
			Contacts=[
				HpContact(
					ReferenceNumber="recno:"+recno,
					Role="Avsender",
					IsUnofficial=True
				),
				HpContact(
					ReferenceNumber=ssn,
					Role="Mottaker",
					IsUnofficial=True
        		),
			],
			Files=[
				HpFile(
					Base64Data=base64Data,
					Category="1",
					Format="pdf",
					Status="F",
					Title="Vitnemål - Høyere yrkesfaglig utdanning - " + elevnavn,
					VersionFormat="A"
				)
			],
			Status= "J",
			DocumentDate=datetime.now().isoformat(),
			UnofficialTitle="Vitnemål - Høyere yrkesfaglig utdanning - " + elevnavn,
			Title="Vitnemål - Høyere yrkesfaglig utdanning - " + elevnavn,
			Archive="Elevdokument",
			CaseNumber=casenr,
			ResponsibleEnterpriseRecno=recno,
			AccessCode="13",
			Paragraph="Offl. § 13 jf. fvl. § 13 (1) nr.1",
			AccessGroup="Studentmapper"
		)		
	)
	data_dict = asdict(data)
	return data_dict


def sendToArchive(payload:str) -> str:
	"""
		Posts the archive data to the archive
		Returns:
			payload string
	"""
	url = f"{archive_url}/archive"
	headers = {"Authorization": f"Bearer {token}"}
	response = requests.post(url, json=payload, headers=headers)
	return response.json()


def getCaseNumber(ssn:str) -> str:
	"""
		Get the casenumber for a SocialSecurityNumber
		Returns:
			payload string
	"""
	url = f"{archive_url}/SyncElevmappe"
	headers = {"Authorization": f"Bearer {token}"}
	payload = { "ssn":ssn, "isStudentmappe": True }
	response = requests.post(url, json=payload, headers=headers)
	return response.json()
