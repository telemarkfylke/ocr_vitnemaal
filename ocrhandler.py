from pathlib import Path
import os
import shutil
import json
import logging
import requests

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
from bibliotek import archive, freg
from bibliotek.config import create_mistral_client
from bibliotek.models import OcrResultatData
from bibliotek.ocr import process_document_ocr, process_document_ocr_docling
from bibliotek.pdf_utils import pdf_to_base64

def move_to_unregistered(item: Path, source_dir: Path) -> None:
	logger.warning(f"Dokument {item.name} flyttet til feilet")
	dest = Path("UnregisteredOCR")
	os.makedirs(dest, exist_ok=True)
	shutil.move(str(source_dir / item.name), str(dest / item.name))

# APP -------------------------------------------------------------------

OCR_PROVIDER = "docling"  # "mistral" eller "docling"

inputPath = "./MistralOCR/"
client = create_mistral_client() if OCR_PROVIDER == "mistral" else None
logger.info(f"OCR-leverandør: {OCR_PROVIDER}")


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

	try:
		if OCR_PROVIDER == "docling":
			annotation = process_document_ocr_docling(
					file_path=pdf_path,
					annotation_model=OcrResultatData,
					max_pages=2
			)
		else:
			document_url = f"data:application/pdf;base64,{base64_pdf}"
			ocr_response = process_document_ocr(
					client=client,
					document_url=document_url,
					annotation_model=OcrResultatData,
					pages=list(range(8)),
					include_image_base64=False
			)
			ocr_dict = json.loads(ocr_response.model_dump_json())
			annotation = json.loads(ocr_dict['document_annotation'])
	except requests.exceptions.HTTPError as e:
		if e.response is not None and e.response.status_code == 422:
			logger.warning(f"{item.name}: OCR ({OCR_PROVIDER}) fant ingen match — {e.response.text}")
			move_to_unregistered(item, directory_path)
		else:
			logger.error(f"{item.name}: OCR ({OCR_PROVIDER}) feilet — lar filen ligge for nytt forsøk — {e}")
		continue
	except Exception as e:
		logger.error(f"{item.name}: OCR ({OCR_PROVIDER}) feilet — lar filen ligge for nytt forsøk — {e}")
		continue

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