"""
Genera front/src/data/historicoAgregado.json y distritos.ts desde el CSV procesado.
Ejecutar desde la raíz del repo back:
  python scripts/generate_front_historico.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CSV_PATH = BASE / "data" / "processed" / "dataset_gnn_granular_final.csv"
FRONT_DATA = BASE.parent / "front" / "src" / "data"


def main():
    distritos: set[str] = set()
    by_dist: dict = defaultdict(lambda: {"count": 0, "lat_sum": 0.0, "lng_sum": 0.0, "tipos": defaultdict(int)})
    by_tipo: dict = defaultdict(int)

    with open(CSV_PATH, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i >= 200_000:
                break
            d = row["distrito"].strip()
            distritos.add(d)
            by_dist[d]["count"] += 1
            by_dist[d]["lat_sum"] += float(row["latitud"])
            by_dist[d]["lng_sum"] += float(row["longitud"])
            by_dist[d]["tipos"][row["tipo_delito"].strip()] += 1
            by_tipo[row["tipo_delito"].strip()] += 1

    lats = [v["lat_sum"] / v["count"] for v in by_dist.values() if v["count"]]
    lngs = [v["lng_sum"] / v["count"] for v in by_dist.values() if v["count"]]
    lat_min, lat_max = min(lats), max(lats)
    lng_min, lng_max = min(lngs), max(lngs)

    def to_pct(lat: float, lng: float) -> tuple[float, float]:
        x = 5 + ((lng - lng_min) / (lng_max - lng_min + 1e-9)) * 85
        y = 5 + ((lat_max - lat) / (lat_max - lat_min + 1e-9)) * 85
        return round(x, 1), round(y, 1)

    max_count = max((v["count"] for v in by_dist.values()), default=1)
    map_districts = []
    for d, v in sorted(by_dist.items(), key=lambda x: -x[1]["count"])[:24]:
        if not v["count"]:
            continue
        lat = v["lat_sum"] / v["count"]
        lng = v["lng_sum"] / v["count"]
        x, y = to_pct(lat, lng)
        risk = min(100, round((v["count"] / max_count) * 100))
        name = d.title() if d.isupper() else d
        map_districts.append(
            {"name": name, "code": d, "risk": risk, "x": x, "y": y, "count": v["count"]}
        )

    colors = {"HURTO": "#ef4444", "ROBO": "#f97316", "VIOLENCIA": "#eab308"}
    crimes_by_type = [
        {"name": t.title(), "value": c, "color": colors.get(t, "#3b82f6")}
        for t, c in sorted(by_tipo.items(), key=lambda x: -x[1])[:6]
    ]

    FRONT_DATA.mkdir(parents=True, exist_ok=True)
    (FRONT_DATA / "historicoAgregado.json").write_text(
        json.dumps(
            {
                "mapDistricts": map_districts,
                "crimesByType": crimes_by_type,
                "zoneStats": [{"name": m["name"], "value": m["risk"]} for m in map_districts[:5]],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    sorted_d = sorted(distritos)
    (FRONT_DATA / "distritos.ts").write_text(
        f"export const DISTRITOS_CSV = {json.dumps(sorted_d)} as const\n"
        f'export const DEFAULT_DISTRITO = {json.dumps(sorted_d[0] if sorted_d else "ANCON")}\n',
        encoding="utf-8",
    )
    print(f"OK: {len(sorted_d)} distritos, {len(map_districts)} puntos mapa -> {FRONT_DATA}")


if __name__ == "__main__":
    main()
