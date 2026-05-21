from sqlalchemy.orm import Session
from sqlalchemy import text
from src.core.models import DenunciaCiudadana, Delito, Cuadrante

class DenunciaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_denuncia_publica(self, id_tipo_delito: int, fecha_delito, hora_delito, lat: float, lng: float, descripcion: str):
        # Usamos ST_MakePoint para la inserción geográfica
        nueva_denuncia = DenunciaCiudadana(
            id_tipo_delito=id_tipo_delito,
            fecha_delito=fecha_delito,
            hora_delito=hora_delito,
            ubicacion_exacta=f"SRID=4326;POINT({lng} {lat})",
            descripcion=descripcion,
            estado="pendiente"
        )
        self.db.add(nueva_denuncia)
        self.db.commit()
        self.db.refresh(nueva_denuncia)
        return nueva_denuncia

    def get_denuncias_pendientes(self):
        return self.db.query(DenunciaCiudadana).filter(DenunciaCiudadana.estado == "pendiente").all()

    def aprobar_denuncia(self, id_denuncia: int):
        denuncia = self.db.query(DenunciaCiudadana).filter(DenunciaCiudadana.id_denuncia_ciudadana == id_denuncia).first()
        if not denuncia or denuncia.estado != "pendiente":
            return None

        # Cambiamos estado
        denuncia.estado = "aprobada"

        # Debemos encontrar en qué cuadrante cae esta denuncia usando ST_Contains
        # ST_Contains(geometria_poligono, ubicacion_exacta)
        cuadrante = self.db.query(Cuadrante).filter(
            text(f"ST_Contains(geometria_poligono, ST_GeomFromWKB(:geom, 4326))")
        ).params(geom=denuncia.ubicacion_exacta.data).first()

        id_cuadrante = cuadrante.id_cuadrante if cuadrante else 1 # Fallback al cuadrante 1 si cae fuera del mapa exacto (solo por robustez en demos)

        # Trasladar a tabla oficial Delitos
        nuevo_delito = Delito(
            id_cuadrante=id_cuadrante,
            id_tipo_delito=denuncia.id_tipo_delito,
            fecha_delito=denuncia.fecha_delito,
            hora_delito=denuncia.hora_delito,
            ubicacion_exacta=denuncia.ubicacion_exacta,
            descripcion_delito=f"Reporte Ciudadano: {denuncia.descripcion}"
        )
        self.db.add(nuevo_delito)
        self.db.commit()
        return denuncia

    def rechazar_denuncia(self, id_denuncia: int):
        denuncia = self.db.query(DenunciaCiudadana).filter(DenunciaCiudadana.id_denuncia_ciudadana == id_denuncia).first()
        if not denuncia or denuncia.estado != "pendiente":
            return None
        denuncia.estado = "rechazada"
        self.db.commit()
        return denuncia
