import json
from typing import List
from datetime import datetime
from dataclasses import dataclass, asdict
import requests
import os

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


archive_url = "https://archive-test.api.telemarkfylke.no/api" # test
# archive_url = "https://archive.api.telemarkfylke.no/api" # prod

recno = "200314"	# test
#recno = "215093" # prod

token = #Token må legges inn her
print(token)

def lag_hovedprosjekt_arkiv_payload(base64Data:str, elevnavn:str, ssn:str) -> str:
	"""
		Get the Payload to be sent to the archive for hovedprosjekt .
		Returns:
			payload string
	"""

	# Retrieve the casenumber for the ssn
	casenr:str = getCaseNumber(ssn)


	data = HpPayload(
		service = "DocumentService",
		method = "CreateDocument",
		parameter = HpParameter(
			Category="Dokument inn",
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
			DocumentDate=str(datetime.now()),
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
	print(datetime.now())
	print(str(datetime.now()))
	data_dict = asdict(data)
	data_json = json.dumps(data_dict)
	return data_json


def sendToArchive(payload:str) -> str:
	"""
		Posts the archive data to the archive
		Returns:
			payload string
	"""
	print("Hei hei")
	url = archive_url+"/archive"
	headers = {"Authorization": "Bearer "+token}
	response = requests.post(url, json=payload, headers=headers)
	return response.json()


def getCaseNumber(ssn:str) -> str:
	"""
		Get the casenumber for a SocialSecurityNumber
		Returns:
			payload string
	"""
	url = archive_url+"/SyncElevmappe"
	headers = {"Authorization": "Bearer "+ token}
	payload = { "ssn":ssn, "isStudentmappe": True }
	response = requests.post(url, json=payload, headers=headers)
	return response.json()
