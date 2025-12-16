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
