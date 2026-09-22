"""
Pydantic models for transcript data extraction and processing.
"""

from pydantic import BaseModel, Field
from typing import Optional

class Vitnemaldata(BaseModel):
    """Model for extracted transcript data."""
    isVitnemal: bool = Field(description="Indikerer om dokumentet er et vitnemål ved å sjekke om dokumentet har overskriften vitnemål,stempel fra skolen, karakterer til eleven, informasjon om studieretning og signatur av rektor.")
    navn: str = Field(description="Fullt navn på studenten")
    fodselsnummer: Optional[str] = Field(default=None, description="Fødselsnummer eller D-nummer")
    skole: str = Field(description="Navn på utdanningsinstitusjonen")
    utdanningsprogram: str = Field(description="Navn på utdanningsprogrammet")


class OcrResultatData(BaseModel):
    """
    Model for classifying and extracting data from scanned documents.

    Field descriptions are the extraction prompt itself: they are sent verbatim
    as the schema to Docling and as the annotation format to Mistral, so wording
    changes here change what the OCR services return.
    """
    Tittel: Optional[str] = Field(
        default=None,
        description="The document's main heading/title, verbatim exactly as written on the page, "
        "e.g. 'VITNEMÅL FOR VIDEREGÅENDE OPPLÆRING' or 'KOMPETANSEBEVIS FOR VIDEREGÅENDE OPPLÆRING'."
    )
    isVitnemal: bool = Field(
        description="Set to true ONLY if the document's main heading is exactly 'VITNEMÅL FOR VIDEREGÅENDE OPPLÆRING'. "
        "Set to false if the heading is 'KOMPETANSEBEVIS FOR VIDEREGÅENDE OPPLÆRING' or anything else. "
        "IMPORTANT: a kompetansebevis is NOT a vitnemål, even though it also contains grades and school information."
    )
    isKompetansebevis: bool = Field(
        description="Set to true ONLY if the document's main heading is exactly 'KOMPETANSEBEVIS FOR VIDEREGÅENDE OPPLÆRING'."
    )
    isHovedprosjekt: bool = Field(
        description="Set to true if the document contains the text 'Høyere yrkesfaglig utdanning' "
        "AND the text 'HOVEDPROSJEKT' appears at the top of the left-hand page."
    )
    navn: Optional[str] = Field(default=None, description="Full name of the student the document belongs to.")
    fodselsnummer: Optional[str] = Field(default=None, description="The Norwegian national ID number (fødselsnummer) or D-number, 11 digits.")
    utdanningssted: Optional[str] = Field(default=None, description="Name of the school or educational institution.")
    utdanningsprogram: Optional[str] = Field(default=None, description="Name of the educational program.")
