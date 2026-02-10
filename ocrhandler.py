from enum import Enum, IntEnum
from pathlib import Path
from mistralai import Mistral
import os
import dotenv
from typing import Any, Type
from mistralai import Mistral
from mistralai.extra import response_format_from_pydantic_model
from pydantic import BaseModel, Field
from typing import Optional
import base64
import shutil
import json
import sys

# Import fra bibliotek-modulen
from bibliotek import (
    archive
)

class CategoryEnum(str, Enum):
    vitnemål = 'vitnemål',
    kompetansebevis = 'kompetansebevis',
    hovedprosjekt = 'hovedprosjekt',
    annet = 'annet'

def load_environment() -> None:
    """Load environment variables from .env file."""
    dotenv.load_dotenv()

def get_api_key() -> str:
    """
    Get the Mistral API key from environment variables.

    Returns:
        API key string

    Raises:
        ValueError: If MISTRAL_API_KEY is not found in environment variables
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY ikke funnet i miljøvariabler")
    return api_key

def create_mistral_client(api_key: str | None = None) -> Mistral:
    """
    Create and return a Mistral client instance.

    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.

    Returns:
        Mistral client instance
    """
    if api_key is None:
        load_environment()
        api_key = get_api_key()

    return Mistral(api_key=api_key)

def pdf_to_base64(file_path: str | Path) -> str:
    """
    Convert a PDF file to base64 encoded string.

    Args:
        file_path: Path to the PDF file

    Returns:
        Base64 encoded string of the PDF content

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Filen {file_path} finnes ikke")

    if not path.is_file():
        raise ValueError(f"{file_path} er ikke en fil")

    pdf_bytes = path.read_bytes()
    return base64.b64encode(pdf_bytes).decode("utf-8")

def process_document_ocr(
    client: Mistral,
    document_url: str,
    annotation_model: Type[BaseModel],
    pages: list[int] | None = None,
    include_image_base64: bool = False,
    model: str = "mistral-ocr-latest"
) -> Any:
    """
    Process a document using Mistral OCR API.

    Args:
        client: Mistral client instance
        document_url: Data URL of the document (base64 encoded)
        annotation_model: Pydantic model for document annotations
        pages: List of page indices to process. If None, processes all pages up to 8
        include_image_base64: Whether to include base64 encoded images in response
        model: OCR model to use

    Returns:
        OCR processing response from Mistral API

    Note:
        Document Annotations has a limit of 8 pages. For larger documents,
        consider splitting them into chunks.
    """
    if pages is None:
        pages = list(range(8))

    response = client.ocr.process(
        model=model,
        pages=pages,
        document={
            "type": "document_url",
            "document_url": document_url
        },
        document_annotation_format=response_format_from_pydantic_model(annotation_model),
        include_image_base64=include_image_base64
    )

    return response

class OcrResultatData(BaseModel):

		type: str = Field(description="Type dokument")


		isVitnemal: bool = Field(
        description="Sett til true KUN hvis dokumentets hovedoverskrift er eksakt 'VITNEMÅL FOR VIDEREGÅENDE OPPLÆRING'. "
        "Sett til false hvis overskriften er 'KOMPETANSEBEVIS FOR VIDEREGÅENDE OPPLÆRING' eller noe annet. "
        "VIKTIG: Et kompetansebevis er IKKE et vitnemål, selv om det har karakterer og skoleinformasjon."
    )
              
		isKompetansebevis: bool = Field(
        description="Sett til true KUN hvis dokumentets hovedoverskrift er eksakt 'KOMPETANSEBEVIS FOR VIDEREGÅENDE OPPLÆRING'"
    )
              
		isHovedprosjekt: bool = Field(
        description="Sett til true hvis dokumentet innholder teksten 'Høyere yrkesfaglig utdanning' og teksten 'HOVEDPROSJEKT' står øverst på venstre side"
    )
              
		navn: Optional[str] = Field(description="Fullt navn på studenten")
		fodselsnummer: Optional[str] = Field(default=None, description="Fødselsnummer eller D-nummer")
		skole: Optional[str] = Field(description="Navn på utdanningsinstitusjonen")
		utdanningsprogram: Optional[str] = Field(description="Navn på utdanningsprogrammet")

class Vitnemåldata(BaseModel):
    """Model for extracted transcript data."""
    isVitnemal: bool = Field(description="Indikerer om dokumentet er et vitnemål ved å sjekke om dokumentet har overskriften vitnemål,stempel fra skolen, karakterer til eleven, informasjon om studieretning og signatur av rektor.")
    navn: str = Field(description="Fullt navn på studenten")
    fodselsnummer: Optional[str] = Field(default=None, description="Fødselsnummer eller D-nummer")
    skole: str = Field(description="Navn på utdanningsinstitusjonen")
    utdanningsprogram: str = Field(description="Navn på utdanningsprogrammet")

# APP -------------------------------------------------------------------

inputPath = "./MistralOCR/"
client = create_mistral_client()


directory_path = Path(inputPath) 

for item in directory_path.iterdir():

	print(item.name)
	pdf_path = Path(inputPath+item.name)
	base64_pdf = pdf_to_base64(pdf_path)
	document_url =  f"data:application/pdf;base64,{base64_pdf}"

	ocr_response = process_document_ocr(
			client=client,
			document_url=document_url,
			annotation_model=OcrResultatData,
			pages=list(range(8)),
			include_image_base64=False
	)
      
	ocr_dict = json.loads(ocr_response.model_dump_json())
	annotation = json.loads(ocr_dict['document_annotation'])

	print("isVitnemål "+ str(annotation['isVitnemal']))
	print("isKompetansebevis "+ str(annotation['isKompetansebevis']))
	print("isHovedprosjekt "+ str(annotation['isHovedprosjekt']))

	if annotation['isHovedprosjekt']:
			vitnemaldata = process_document_ocr(
										client=client,
										document_url=document_url,
										annotation_model=Vitnemåldata,
										pages=list(range(8)),
										include_image_base64=False)
			print("Dokument "+item.name+" flyttet til hovedprosjekt")
			print(annotation['navn'], annotation['fodselsnummer'])
			payload = archive.lag_hovedprosjekt_arkiv_payload(base64Data=base64_pdf, elevnavn=annotation['navn'], ssn=annotation['fodselsnummer'])
			#print("Resultatet er: " + payload)
			archive.sendToArchive(payload=payload)
			shutil.move(inputPath+item.name, "./Hovedprosjekt/"+item.name)

	# elif annotation['isKompetansebevis']:
		# vitnemaldata = process_document_ocr(
									# client=client,
									# document_url=document_url,
									# annotation_model=Vitnemåldata,
									# pages=list(range(8)),
									# include_image_base64=False)
		# print("Dokument "+item.name+" flyttet til kompetansebevis")
		# shutil.move(inputPath+item.name, "./testfiles/kompetansebevis/"+item.name)
            
	# elif annotation['isVitnemal']:
	# 		vitnemaldata = process_document_ocr(
	# 									client=client,
	# 									document_url=document_url,
	# 									annotation_model=Vitnemåldata,
	# 									pages=list(range(8)),
	# 									include_image_base64=False)
	# 		print("Dokument "+item.name+" flyttet til vitnemål")
	# 		shutil.move(inputPath+item.name, "./Vitnemal/"+item.name)		

	else:
			print("Dokument "+item.name+" flyttet til feilet")
			shutil.move(inputPath+item.name, "./UnregisteredOCR/" + item.name)