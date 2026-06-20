# Plan de Reversa (Rollback Plan) - Sistema Predictivo GNN

Este documento establece el protocolo oficial y los procedimientos técnicos detallados para restaurar el Sistema Predictivo Delictivo PNP (ST-GNN) a una versión anterior estable en caso de fallos críticos detectados durante o después de un despliegue en producción.

---

## 1. Objetivos del Plan de Reversa
* **Garantizar la Continuidad Operativa (SLA):** Minimizar el tiempo de inactividad del sistema (RTO < 15 minutos).
* **Asegurar la Integridad de los Datos:** Prevenir la pérdida o corrupción de datos relacionales e históricos en la base de datos PostgreSQL/PostGIS.
* **Restauración Rápida de la IA:** Proveer un mecanismo rápido para revertir los pesos del modelo de Deep Learning (`.pth`) en caso de divergencia o falsos positivos extremos en producción.

---

## 2. Procedimiento A: Reversa de la Base de Datos (PostgreSQL + PostGIS)

En caso de que una migración o actualización de la estructura de la base de datos falle o corrompa las tablas espaciales:

### Paso A.1: Restauración de Backups Físicos/Lógicos (Supabase/PostgreSQL)
Si se realiza un backup diario automático (Dump SQL):
1. **Poner el servidor en modo mantenimiento:** Desviar temporalmente el tráfico a una página estática para evitar escrituras concurrentes.
2. **Eliminar esquemas corruptos (si es necesario):**
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   -- Activar extensiones espaciales requeridas
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
3. **Restaurar el último punto de restauración (RPO de 24 horas máximo) o dump lógico:**
   ```bash
   pg_restore -h aws-1-us-east-1.pooler.supabase.com -U postgres -d postgres -v "C:\backups\pnp_backup_dia.dump"
   ```

### Paso A.2: Rollback Manual de Esquema (script_bd.txt)
Si los cambios se realizaron a través del script SQL directo:
1. Localizar los scripts de reversión creados por el analista antes de la actualización.
2. Si se crearon índices o tablas nuevas que generan bloqueos:
   ```sql
   DROP INDEX IF EXISTS idx_delito_fecha_anio;
   ALTER TABLE denuncias_ciudadanas DROP COLUMN IF EXISTS nuevo_campo_prueba;
   ```

---

## 3. Procedimiento B: Reversa de Contenedores y Código (Render / AWS)

Si el backend de FastAPI o la visualización del frontend fallan tras un despliegue continuo:

### Paso B.1: Reversión de la Imagen de Contenedor en Render
1. Iniciar sesión en el panel administrativo de [Render](https://dashboard.render.com).
2. Seleccionar el servicio web correspondiente al backend (`integrador-gnn-backend`) o frontend.
3. Ir al menú **Events** (Eventos) o **Deploy History** (Historial de Despliegues).
4. Localizar la última versión operativa exitosa (ejemplo: Commit `a7f23c9` o tag `v2.0.0-stable`).
5. Hacer clic en **Rollback to this deploy** (Revertir a este despliegue). Render detendrá la compilación defectuosa y redirigirá el tráfico de inmediato a la instancia anterior segura.

### Paso B.2: Rollback manual de Docker Image (Local/VPS)
Si el despliegue es en una máquina dedicada con Docker Compose:
1. Abrir la consola en la carpeta del backend.
2. Editar el archivo `docker-compose.yml` para apuntar a la etiqueta estable anterior:
   ```yaml
   services:
     api:
       image: pnp-predictivo-gnn:v2.0.0-stable # Cambiar de latest a la versión estable anterior
   ```
3. Reiniciar el contenedor en caliente:
   ```bash
   docker compose up -d --build
   ```

---

## 4. Procedimiento C: Reversa de Pesos del Modelo GNN

Si el modelo predictivo ST-GNN cargado en el arranque empieza a arrojar predicciones erróneas o presenta fugas de memoria por pesos defectuosos:

1. **Localizar el directorio del modelo:**
   La carpeta del modelo es [src/model](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/src/model).
2. **Reemplazar el archivo binario de pesos `.pth`:**
   En cada entrenamiento exitoso, el sistema guarda una copia de seguridad llamada `pesos_stgnn_pnp.pth.bak`.
   Ejecutar los siguientes comandos en el servidor para restaurar la versión anterior validada por el científico de datos:
   ```powershell
   # En Windows Powershell
   Copy-Item -Path "src/model/pesos_stgnn_pnp.pth.bak" -Destination "src/model/pesos_stgnn_pnp.pth" -Force
   ```
3. **Forzar reinicio del servicio backend:**
   FastAPI cargará los pesos anteriores del disco duro a la RAM durante el arranque de su ciclo de vida (`lifespan`), solventando la desviación predictiva de forma inmediata.

---

## 5. Procedimiento D: Reversa de Variables de Entorno

Si un cambio en el archivo `.env` o en las configuraciones del hosting bloquea el acceso de la API:
1. Restaurar la copia de respaldo del archivo de entorno:
   ```powershell
   Copy-Item -Path ".env.bak" -Destination ".env" -Force
   ```
2. Re-inyectar las variables antiguas en Render ingresando al menú **Environment** y aplicando los valores anteriores de la clave secreta y base de datos.
3. Hacer clic en **Save Changes** para regenerar el servicio.
