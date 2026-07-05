import csv
import json
from io import StringIO

REQUIRED_UPLOAD_FIELDS = (
    "id_cuadrante",
    "id_tipo_delito",
    "fecha_delito",
    "ubicacion",
)


def _normalize_row(row: dict) -> dict[str, str]:
    return {str(key).strip().lower(): str(value).strip() for key, value in row.items() if key}


def validate_csv_bytes(content: bytes) -> tuple[int, int]:
    """Valida cabeceras y filas de un CSV. Retorna (validos, invalidos)."""
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        raise ValueError("El CSV no tiene cabecera.")

    headers = {h.strip().lower() for h in reader.fieldnames if h}
    missing = [col for col in REQUIRED_UPLOAD_FIELDS if col not in headers]
    if missing:
        raise ValueError(f"Formato CSV inválido. Faltan columnas: {', '.join(missing)}.")

    valid = 0
    invalid = 0
    for row in reader:
        normalized = _normalize_row(row)
        if all(normalized.get(col) for col in REQUIRED_UPLOAD_FIELDS):
            valid += 1
        else:
            invalid += 1

    if valid + invalid == 0:
        raise ValueError("El CSV debe incluir al menos una fila de datos.")

    return valid, invalid


def validate_json_bytes(content: bytes) -> tuple[int, int]:
    """Valida estructura de un JSON de carga. Retorna (validos, invalidos)."""
    try:
        data = json.loads(content.decode("utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError("El archivo JSON no tiene un formato válido.") from exc

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("El JSON debe ser un arreglo con al menos un registro.")

    valid = 0
    invalid = 0
    for item in data:
        if not isinstance(item, dict):
            invalid += 1
            continue
        normalized = {str(key).strip().lower(): str(value).strip() for key, value in item.items()}
        if all(normalized.get(col) for col in REQUIRED_UPLOAD_FIELDS):
            valid += 1
        else:
            invalid += 1

    if valid + invalid == 0:
        raise ValueError("El JSON no contiene registros válidos.")

    return valid, invalid
