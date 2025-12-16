# VitnemalOCR

Et Python-basert OCR (Optical Character Recognition) system for prosessering av norske vitnemål ved hjelp av Mistral AI's avanserte OCR-teknologi.

Made with ❤️ by TFK.

## Oversikt

VitnemalOCR automatiserer tekstutvinning fra vitnemål i PDF-format. Systemet bruker Mistral AI's OCR-teknologi med Pydantic-modeller for å generere annoteringer og strukturert markdown-output.

## Funksjoner

- **Automatisert OCR-prosessering**: Utvinn tekst fra PDF-dokumenter med høy nøyaktighet
- **Annotasjoner med Pydantic**: Dokumentannoteringer basert på typesikre datamodeller
- **Markdown-output**: Ren, strukturert markdown fra OCR-prosessering
- **JSON-lagring**: Resultater lagres i strukturert JSON-format
- **Konfigurerbar**: Miljøbasert konfigurasjon for API-nøkler

## Forutsetninger

- Python 3.10 eller høyere
- [uv](https://github.com/astral-sh/uv) pakkebehandler (anbefalt) eller pip
- Mistral AI API-nøkkel ([Få en her](https://console.mistral.ai/))

## Installasjon

### 1. Klon repositoriet

```bash
git clone <repository-url>
cd ocr_vitnemaal
```

### 2. Opprett virtuelt miljø

Ved bruk av `uv` (anbefalt):
```bash
uv venv
```

Eller ved bruk av standard Python:
```bash
python -m venv .venv
```

### 3. Aktiver virtuelt miljø

På macOS/Linux:
```bash
source .venv/bin/activate
```

På Windows:
```bash
.venv\Scripts\activate
```

### 4. Installer avhengigheter

Ved bruk av `uv`:
```bash
uv pip install -r requirements.txt
```

Eller ved bruk av pip:
```bash
pip install -r requirements.txt
```

### 5. Konfigurer miljøvariabler

Kopier eksempel-miljøfilen:
```bash
cp .env.example .env
```

Rediger `.env` og legg til din Mistral AI API-nøkkel:
```env
MISTRAL_API_KEY=din_faktiske_api_nøkkel_her
```

## Bruk

### Grunnleggende bruk

Plasser dine PDF-filer i `vitnemal/`-mappen, og kjør deretter:

```bash
python 01-vitnemal_ocr.py
```

### Output

Prosesserte resultater lagres i `ocr_resultat/`-mappen:
- `*_ocr_annotations.json` - OCR-resultat med markdown-tekst, annoteringer og metadata

### Eksempel på output-struktur

```json
{
  "pages": [
    {
      "index": 0,
      "markdown": "# VITNEMÅL\n...",
      "dimensions": { "dpi": 200, "height": 2339, "width": 1654 }
    }
  ],
  "model": "mistral-ocr-latest",
  "usage_info": {
    "pages_processed": 1,
    "doc_size_bytes": 318077
  },
  "document_annotation": {
    "isVitnemal": true,
    "navn": "...",
    "fodselsnummer": "...",
    "skole": "...",
    "utdanningsprogram": "..."
  }
}
```

## Prosjektstruktur

```
ocr_vitnemaal/
├── bibliotek/              # Kjernebibliotek for OCR
│   ├── __init__.py        # Pakkeeksporter
│   ├── config.py          # Konfigurasjon og API-klient
│   ├── file_io.py         # Fil I/O-verktøy
│   ├── models.py          # Pydantic-datamodeller
│   ├── ocr.py            # OCR-prosessering
│   └── pdf_utils.py      # PDF-håndteringsverktøy
├── vitnemal/             # Input PDF-filer (ikke i git)
├── ocr_resultat/         # Output-mappe (ikke i git)
├── 01-vitnemal_ocr.py   # Hovedapplikasjonsskript
├── requirements.txt      # Python-avhengigheter
├── requirements-dev.txt  # Utviklingsavhengigheter
├── pyproject.toml        # Prosjektkonfigurasjon
├── uv.lock              # UV låsefil
├── .env                  # Miljøvariabler (ikke i git)
├── .env.example          # Miljømal
├── .gitignore           # Git ignore-regler
└── README.md             # Denne filen
```

## Utvikling

### Installer utviklingsavhengigheter

```bash
uv pip install -r requirements-dev.txt
```

Dette inkluderer:
- `pytest` - Testrammeverk
- `black` - Kodeformatterer
- `ruff` - Rask Python-linter
- `mypy` - Statisk typekontroll

### Kodeformattering

```bash
black .
```

### Linting

```bash
ruff check .
```

## Konfigurasjon

Prosjektet bruker miljøvariabler for konfigurasjon. Se `.env.example` for tilgjengelige alternativer:

- `MISTRAL_API_KEY` - Din Mistral AI API-nøkkel (påkrevd)

## Avhengigheter

### Kjerneavhengigheter

- **mistralai** (>=1.9.0) - Mistral AI SDK for OCR-prosessering
- **pydantic** (>=2.12.0) - Datavalidering og modellering
- **pydantic-core** (>=2.41.0) - Kjernevalideringslogikk
- **python-dotenv** (>=1.2.0) - Håndtering av miljøvariabler

### Utviklingsavhengigheter

- **pytest** (>=8.0.0) - Testing
- **black** (>=24.0.0) - Formattering
- **ruff** (>=0.2.0) - Linting
- **mypy** (>=1.8.0) - Typekontroll

## API-bruk

Prosjektet bruker kun **Mistral OCR endpoint**:
- `client.ocr.process()` - For OCR-prosessering av PDF-dokumenter

## Feilsøking

### ModuleNotFoundError

Hvis du ser `ModuleNotFoundError: No module named 'mistralai'`:
1. Sørg for at det virtuelle miljøet er aktivert
2. Sjekk hvilken Python du bruker: `which python`
3. Reinstaller avhengigheter: `uv pip install -r requirements.txt`

### API-nøkkelproblemer

Hvis du ser "MISTRAL_API_KEY ikke funnet i miljøvariabler":
1. Verifiser at `.env`-filen finnes i prosjektets rot
2. Sjekk at API-nøkkelen er satt riktig
3. Sørg for at `python-dotenv` er installert

### Import-feil

Hvis du får importfeil med `bibliotek`-pakken:
1. Sørg for at du er i prosjektets rotmappe
2. Verifiser at det virtuelle miljøet er aktivert
3. Sjekk at alle avhengigheter er installert: `uv pip list`

## Tekniske detaljer

### Kodekvalitet
- **Total kodelinjer**: ~301 linjer
- **Type hints**: 100% dekning
- **Dokumentasjon**: 100% (alle funksjoner)
- **Modulær struktur**: 6 bibliotekmoduler + hovedskript

### Ytelse
- Støtter opptil 8 sider per OCR-forespørsel
- Base64-enkoding av PDF
- Effektiv JSON-lagring

## Support

For problemer og spørsmål, vennligst kontakt utviklingsteamet eller opprett en issue i repositoriet.
