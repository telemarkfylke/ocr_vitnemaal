from pathlib import Path
from mistralai import Mistral
from mistralai.extra import response_format_from_pydantic_model
from pydantic import BaseModel, Field
from typing import Any, Optional, Type
import os
import dotenv
import base64
import shutil
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("ocr_logfile.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Import fra bibliotek-modulen
from bibliotek import (
    archive,
    freg
)

def load_environment() -> None:
    """Load environment variables from .env file."""
    dotenv.load_dotenv()

def move_to_unregistered(item: Path, source_dir: Path) -> None:
	logger.warning(f"Dokument {item.name} flyttet til feilet")
	dest = Path("UnregisteredOCR")
	os.makedirs(dest, exist_ok=True)
	shutil.move(str(source_dir / item.name), str(dest / item.name))

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

		isVitnemal: bool = Field(
        description="Sett til true KUN hvis dokumentet har hovedoverskriften 'VITNEMÅL FOR VIDEREGÅENDE OPPLÆRING'. "
        "Sett alltid til false hvis overskriften inneholder ordet 'KOMPETANSEBEVIS'. "
        "Et kompetansebevis er aldri et vitnemål, selv om det inneholder karakterer og skoleinformasjon."
    )

		isKompetansebevis: bool = Field(
        description="Sett til true KUN hvis dokumentet har hovedoverskriften 'KOMPETANSEBEVIS FOR VIDEREGÅENDE OPPLÆRING'. "
        "Sett alltid til false hvis overskriften inneholder ordet 'VITNEMÅL'."
    )

		isHovedprosjekt: bool = Field(
        description="Sett til true KUN hvis dokumentet inneholder både teksten 'Høyere yrkesfaglig utdanning' og teksten 'HOVEDPROSJEKT'."
    )

		navn: Optional[str] = Field(description="Fullt navn på studenten slik det står i dokumentet.")
		fodselsnummer: Optional[str] = Field(default=None, description="Fødselsnummer eller D-nummer (11 siffer). Returner kun sifrene uten mellomrom eller bindestreker.")
		skole: Optional[str] = Field(description="Fullt navn på utdanningsinstitusjonen slik det står i dokumentet.")
		utdanningsprogram: Optional[str] = Field(description="Navn på utdanningsprogrammet eller studieretningen slik det står i dokumentet.")

# APP -------------------------------------------------------------------

inputPath = "./MistralOCR/"
client = create_mistral_client()


directory_path = Path(inputPath) 

for item in directory_path.iterdir():

	if item.suffix.lower() != '.pdf':
		logger.info(f"Hopper over {item.name} (ikke PDF)")
		continue

	pdf_path = directory_path / item.name

	with open(pdf_path, 'rb') as f:
		header = f.read(4)
	if header != b'%PDF':
		logger.warning(f"Hopper over {item.name} (ugyldig PDF-fil)")
		move_to_unregistered(item, directory_path)
		continue

	logger.info(f"Behandler: {item.name}")
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

	logger.info(f"isVitnemål: {annotation['isVitnemal']}")
	logger.info(f"isKompetansebevis: {annotation['isKompetansebevis']}")
	logger.info(f"isHovedprosjekt: {annotation['isHovedprosjekt']}")

	if annotation['isVitnemal'] and annotation['isKompetansebevis']:
		logger.warning(f"{item.name}: OCR returnerte både isVitnemal og isKompetansebevis som true — mulig klassifiseringsfeil")

	if not annotation['fodselsnummer'] or not annotation['navn']:
		logger.warning(f"{item.name}: Ingen fødselsnummer/navn funnet")
		move_to_unregistered(item, directory_path)

	elif not freg.checkSsn(ssn=annotation['fodselsnummer'], navn=annotation['navn']):
		logger.warning(f"{item.name}: Fødselsnummer matcher ikke navn i FREG")
		move_to_unregistered(item, directory_path)

	elif annotation['isHovedprosjekt']:
			logger.info(f"Dokument {item.name} er hovedprosjekt — arkiverer")
			logger.info(f"Navn: {annotation['navn']}, Fnr: {annotation['fodselsnummer']}")
			payload = archive.lag_hovedprosjekt_arkiv_payload(base64Data=base64_pdf, elevnavn=annotation['navn'], ssn=annotation['fodselsnummer'])
			result = archive.sendToArchive(payload=payload)
			logger.info(f"Arkivresultat: {result}")
			dest = Path("Hovedprosjekt")
			os.makedirs(dest, exist_ok=True)
			shutil.move(str(directory_path / item.name), str(dest / item.name))
			logger.info(f"Dokument {item.name} flyttet til Hovedprosjekt")

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
		logger.warning(f"{item.name}: Ukjent dokumenttype — flytter til feilet")
		move_to_unregistered(item, directory_path)