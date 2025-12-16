"""
VitnemalOCR - Student Transcript OCR Processing

This script processes student transcripts (vitnemål) using Mistral AI's OCR
to extract text with annotations.
"""

from pathlib import Path
import json

# Import fra bibliotek-modulen
from bibliotek import (
    create_mistral_client,
    pdf_to_base64,
    create_document_url,
    process_document_ocr,
    save_json,
    Vitnemaldata,
)


def main():
    """Main function for OCR processing."""

    # Configuration - process a single transcript
    pdf_path = Path("./vitnemal/Vitnemål_EvenElev.pdf")
    output_dir = Path("./ocr_resultat")

    # 1. Opprett Mistral-klient
    print("Oppretter Mistral-klient...")
    client = create_mistral_client()

    # 2. Konverter PDF til base64
    print(f"Konverterer {pdf_path.name} til base64...")
    base64_pdf = pdf_to_base64(pdf_path)
    document_url = create_document_url(base64_pdf)

    # 3. Prosesser dokument med OCR
    print("Prosesserer dokument med OCR...")
    ocr_response = process_document_ocr(
        client=client,
        document_url=document_url,
        annotation_model=Vitnemaldata,
        pages=list(range(8)),
        include_image_base64=False
    )

    print(f"Fant {len(ocr_response.pages)} side(r) med OCR-annotasjoner")

    # 4. Lagre resultater
    print("\nLagrer resultater...")

    # Opprett output-filnavn basert på input PDF-navn
    base_filename = pdf_path.stem
    ocr_output_path = output_dir / f"{base_filename}_ocr_annotations.json"

    # Lagre OCR-respons med annoteringer
    ocr_dict = json.loads(ocr_response.model_dump_json())
    save_json(ocr_dict, ocr_output_path)
    print(f"✓ OCR-respons lagret: {ocr_output_path}")
    print("\n✅ OCR-prosessering fullført!")


if __name__ == "__main__":
    main()
