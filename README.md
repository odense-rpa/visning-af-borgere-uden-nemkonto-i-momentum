# Visning af borgere uden NemKonto i Momentum

Automatisering der markerer borgere uden NemKonto i Momentum, baseret på en liste fra KY.

## Hvad gør robotten?

1. **Henter opgaver** fra KY-opgaveindbakken `KH - 22. Liste nemkonto`, som indeholder CPR-numre og navne på borgere uden NemKonto
2. **Finder borgeren** i Momentum ud fra CPR-nummeret
3. **Tjekker** om borgeren allerede har en aktiv markering *"Borger har ikke NemKonto"*
4. **Opretter markeringen** i Momentum, hvis den ikke allerede findes
5. **Tracker** den udførte opgave

## Forudsætninger

- Python ≥ 3.13
- [`uv`](https://docs.astral.sh/uv/) til pakkehåndtering
- Adgang til **Automation Server** (arbejdskø)
- Adgang til **Momentum** (produktion)
- En **RoboA**-konto med adgang til KY
- En **Odense SQL Server**-konto til tracking

## Installation

```sh
uv sync
```

## Konfiguration

Kopiér `.env.example` til `.env` og udfyld følgende:

| Variabel | Beskrivelse |
|---|---|
| `ATS_URL` | URL til Automation Server API |
| `ATS_TOKEN` | Token til Automation Server |
| `ATS_WORKQUEUE_OVERRIDE` | Valgfri override af arbejdskø-id |

Derudover skal følgende Credentials være oprettet i Automation Server:

| Credential | Formål |
|---|---|
| `RoboA` | Adgang til KY |
| `Odense SQL Server` | Tracking af udførte opgaver |
| `Momentum - produktion` | Adgang til Momentum (client id/secret, api key, resource, base url) |

## Kørsel

```sh
# Fyld arbejdskøen med borgere uden NemKonto
uv run python main.py --queue

# Behandl arbejdskøen
uv run python main.py
```

### Argumenter

| Argument | Beskrivelse |
|---|---|
| `--queue` | Fyld arbejdskøen fra KY og afslut (kør ingen behandling) |

## Afhængigheder

| Pakke | Formål |
|---|---|
| `automation-server-client` | Arbejdskø-håndtering |
| `ky-client` | Integration med KY (opgaveindbakke) |
| `momentum-client` | Integration med Momentum |
| `odk-tools` | Aktivitetssporing |

## Persondatasikkerhed

Robotten behandler personoplysninger på vegne af Odense Kommune, herunder CPR-numre.

- Ingen personoplysninger må lægges i dette repository — hverken som testdata, i kode eller i kommentarer
- Legitimationsoplysninger håndteres udelukkende via miljøvariabler (`.env`) og Automation Server Credentials

