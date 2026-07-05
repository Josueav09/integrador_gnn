import pytest

from src.utils.upload_validation import validate_csv_bytes, validate_json_bytes

CSV_OK = (
    b"id_cuadrante,id_tipo_delito,fecha_delito,ubicacion\n"
    b"101,2,2024-01-01,POINT(-77.03 -12.05)\n"
)

CSV_MISSING_COL = b"id_cuadrante,fecha_delito\n1,2024-01-01\n"

JSON_OK = b"""[
  {
    "id_cuadrante": 101,
    "id_tipo_delito": 2,
    "fecha_delito": "2024-01-01",
    "ubicacion": "POINT(-77.03 -12.05)"
  }
]"""


def test_validate_csv_bytes_ok():
    valid, invalid = validate_csv_bytes(CSV_OK)
    assert valid == 1
    assert invalid == 0


def test_validate_csv_bytes_missing_columns():
    with pytest.raises(ValueError, match="Faltan columnas"):
        validate_csv_bytes(CSV_MISSING_COL)


def test_validate_json_bytes_ok():
    valid, invalid = validate_json_bytes(JSON_OK)
    assert valid == 1
    assert invalid == 0


def test_validate_json_bytes_invalid_syntax():
    with pytest.raises(ValueError, match="formato válido"):
        validate_json_bytes(b"{bad json")
