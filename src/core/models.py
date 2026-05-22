from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric, Date, Time, JSON, func, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from src.core.database import Base

# =============================================================================
# BLOQUE 1: KERNEL DEL SISTEMA (Seguridad y Usuarios)
# =============================================================================

class Rol(Base):
    __tablename__ = "sistema_roles"

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre_rol = Column(String(50), nullable=False)
    descripcion_rol = Column(Text)
    estado_rol = Column(String(20), default="activo")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "sistema_usuarios"

    id_usuario_sistema = Column(Integer, primary_key=True, autoincrement=True)
    id_rol = Column(Integer, ForeignKey("sistema_roles.id_rol", ondelete="RESTRICT"), nullable=False)
    nombre_usuario_sistema = Column(String(100), nullable=False)
    apellido_usuario_sistema = Column(String(100), nullable=False)
    email_usuario_sistema = Column(String(150), unique=True, index=True, nullable=False)
    password_usuario_sistema = Column(String(255), nullable=False)
    avatar_usuario_sistema = Column(String(255), default=None)
    estado_usuario_sistema = Column(String(20), default="activo")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")
    lotes = relationship("LoteImportacion", back_populates="usuario")
    modelos = relationship("ModeloGNN", back_populates="usuario")
    predicciones = relationship("Prediccion", back_populates="usuario")


class CodigoRecuperacion(Base):
    __tablename__ = "codigos_recuperacion"
    
    id_codigo = Column(Integer, primary_key=True, index=True)
    email_usuario = Column(String(150), ForeignKey("sistema_usuarios.email_usuario_sistema", ondelete="CASCADE"), nullable=False)
    pin_recuperacion = Column(String(6), nullable=False)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    usado = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

class Configuracion(Base):
    __tablename__ = "sistema_configuraciones"

    id_configuracion = Column(Integer, primary_key=True, autoincrement=True)
    llave_configuracion = Column(String(100), unique=True, nullable=False)
    valor_configuracion = Column(Text)
    descripcion_configuracion = Column(String(255), default=None)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# =============================================================================
# BLOQUE 2: DOMINIO GEOGRÁFICO Y TOPOLÓGICO (POSTGIS)
# =============================================================================

class Distrito(Base):
    __tablename__ = "distritos"

    id_distrito = Column(Integer, primary_key=True, autoincrement=True)
    nombre_distrito = Column(String(100), nullable=False)
    codigo_ubigeo_distrito = Column(String(10), unique=True, nullable=False)
    provincia_distrito = Column(String(100), default="Lima")
    geometria_distrito = Column(Geometry(geometry_type="POLYGON", srid=4326), default=None)
    estado_distrito = Column(String(20), default="activo")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cuadrantes = relationship("Cuadrante", back_populates="distrito")


class Cuadrante(Base):
    __tablename__ = "cuadrantes"

    id_cuadrante = Column(Integer, primary_key=True, autoincrement=True)
    id_distrito = Column(Integer, ForeignKey("distritos.id_distrito", ondelete="RESTRICT"), nullable=False)
    codigo_cuadrante = Column(String(20), unique=True, nullable=False)
    nombre_cuadrante = Column(String(150), nullable=False)
    centroide = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    geometria_poligono = Column(Geometry(geometry_type="POLYGON", srid=4326), default=None)
    area_km2_cuadrante = Column(Numeric(10, 4), default=None)
    estado_cuadrante = Column(String(20), default="activo")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    distrito = relationship("Distrito", back_populates="cuadrantes")
    delitos = relationship("Delito", back_populates="cuadrante")
    predicciones_valores = relationship("PrediccionCuadrante", back_populates="cuadrante")


class CuadranteAdyacente(Base):
    __tablename__ = "cuadrantes_adyacentes"

    id_cuadrante_origen = Column(Integer, ForeignKey("cuadrantes.id_cuadrante", ondelete="CASCADE"), primary_key=True)
    id_cuadrante_destino = Column(Integer, ForeignKey("cuadrantes.id_cuadrante", ondelete="CASCADE"), primary_key=True)
    peso_adyacencia = Column(Numeric(8, 6), default=1.000000, nullable=False)
    tipo_adyacencia = Column(String(20), default="contiguo")
    distancia_m_adyacencia = Column(Numeric(10, 2), default=None)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# =============================================================================
# BLOQUE 3: DOMINIO DELICTIVO
# =============================================================================

class TipoDelito(Base):
    __tablename__ = "tipos_delitos"

    id_tipo_delito = Column(Integer, primary_key=True, autoincrement=True)
    codigo_tipo_delito = Column(String(20), unique=True, nullable=False)
    nombre_tipo_delito = Column(String(100), nullable=False)
    categoria_tipo_delito = Column(String(100), nullable=False)
    descripcion_tipo_delito = Column(Text, default=None)
    estado_tipo_delito = Column(String(20), default="activo")

    delitos = relationship("Delito", back_populates="tipo_delito")


class LoteImportacion(Base):
    __tablename__ = "lotes_importacion"

    id_lote_importacion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario_sistema = Column(Integer, ForeignKey("sistema_usuarios.id_usuario_sistema", ondelete="RESTRICT"), nullable=False)
    nombre_archivo_lote = Column(String(255), nullable=False)
    formato_lote = Column(String(10), nullable=False)
    total_registros = Column(Integer, default=0, nullable=False)
    validos = Column(Integer, default=0, nullable=False)
    invalidos = Column(Integer, default=0, nullable=False)
    cobertura = Column(Numeric(5, 2))  # Columna computada (GENERATED ALWAYS)
    estado_lote = Column(String(20), default="procesando")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="lotes")
    delitos = relationship("Delito", back_populates="lote")


class Delito(Base):
    __tablename__ = "delitos"

    id_delito = Column(Integer, primary_key=True, autoincrement=True)
    id_cuadrante = Column(Integer, ForeignKey("cuadrantes.id_cuadrante", ondelete="RESTRICT"), nullable=False)
    id_tipo_delito = Column(Integer, ForeignKey("tipos_delitos.id_tipo_delito", ondelete="RESTRICT"), nullable=False)
    id_lote_importacion = Column(Integer, ForeignKey("lotes_importacion.id_lote_importacion", ondelete="SET NULL"), default=None)
    fecha_delito = Column(Date, nullable=False)
    hora_delito = Column(Time, default=None)
    ubicacion_exacta = Column(Geometry(geometry_type="POINT", srid=4326), default=None)
    descripcion_delito = Column(Text, default=None)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cuadrante = relationship("Cuadrante", back_populates="delitos")
    tipo_delito = relationship("TipoDelito", back_populates="delitos")
    lote = relationship("LoteImportacion", back_populates="delitos")


# =============================================================================
# BLOQUE 4: MLOps E INTELIGENCIA ARTIFICIAL (GNN)
# =============================================================================

class ModeloGNN(Base):
    __tablename__ = "modelos_gnn"

    id_modelo_gnn = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario_sistema = Column(Integer, ForeignKey("sistema_usuarios.id_usuario_sistema", ondelete="RESTRICT"), nullable=False)
    version_modelo_gnn = Column(String(20), unique=True, nullable=False)
    nombre_modelo_gnn = Column(String(100), nullable=False)
    arquitectura_modelo_gnn = Column(String(20), default="ST-GNN")
    hiperparametros_modelo_gnn = Column(JSON, default=None)
    ruta_archivo_modelo_gnn = Column(String(255), default=None)
    rmse_modelo_gnn = Column(Numeric(10, 6), default=None)
    f1_score_modelo_gnn = Column(Numeric(5, 4), default=None)
    estado_modelo_gnn = Column(String(20), default="entrenando")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="modelos")
    predicciones = relationship("Prediccion", back_populates="modelo")


class Prediccion(Base):
    __tablename__ = "predicciones"

    id_prediccion = Column(Integer, primary_key=True, autoincrement=True)
    id_modelo_gnn = Column(Integer, ForeignKey("modelos_gnn.id_modelo_gnn", ondelete="RESTRICT"), nullable=False)
    id_usuario_sistema = Column(Integer, ForeignKey("sistema_usuarios.id_usuario_sistema", ondelete="RESTRICT"), nullable=False)
    fecha_objetivo_prediccion = Column(Date, nullable=False)
    latencia_ms_prediccion = Column(Integer, default=None)
    estado_prediccion = Column(String(20), default="procesando")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    modelo = relationship("ModeloGNN", back_populates="predicciones")
    usuario = relationship("Usuario", back_populates="predicciones")
    valores = relationship("PrediccionCuadrante", back_populates="prediccion", cascade="all, delete-orphan")


class PrediccionCuadrante(Base):
    __tablename__ = "predicciones_cuadrantes"

    id_prediccion_cuadrante = Column(Integer, primary_key=True, autoincrement=True)
    id_prediccion = Column(Integer, ForeignKey("predicciones.id_prediccion", ondelete="CASCADE"), nullable=False)
    id_cuadrante = Column(Integer, ForeignKey("cuadrantes.id_cuadrante", ondelete="RESTRICT"), nullable=False)
    score_riesgo = Column(Numeric(5, 4), nullable=False)
    nivel_riesgo = Column(String(20), nullable=False)

    prediccion = relationship("Prediccion", back_populates="valores")
    cuadrante = relationship("Cuadrante", back_populates="predicciones_valores")


# =============================================================================
# BLOQUE 5: CROWDSOURCING Y DENUNCIAS CIUDADANAS (CUARENTENA)
# =============================================================================

class DenunciaCiudadana(Base):
    __tablename__ = "denuncias_ciudadanas"

    id_denuncia_ciudadana = Column(Integer, primary_key=True, autoincrement=True)
    id_tipo_delito = Column(Integer, ForeignKey("tipos_delitos.id_tipo_delito", ondelete="RESTRICT"), nullable=False)
    fecha_delito = Column(Date, nullable=False)
    hora_delito = Column(Time, default=None)
    ubicacion_exacta = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    descripcion = Column(Text, default=None)
    estado = Column(String(20), default="pendiente")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tipo_delito = relationship("TipoDelito")