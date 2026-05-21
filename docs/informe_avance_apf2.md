# INFORME DE AVANCE DE PROYECTO FINAL 2 (APF2) - ACTUALIZADO
**CURSO:** Integrador de Software  
**PROYECTO:** Sistema Inteligente de Predicción delictiva espaciotemporal en Lima Metropolitana mediante Redes Neuronales de Grafos (ST-GNN)  
**ORGANIZACIÓN OBJETIVO:** Policía Nacional del Perú (PNP) - Dirección de Inteligencia (DIRIN)

---

## 1. Análisis Empresarial

### a. Introducción
La criminalidad en Lima Metropolitana representa uno de los mayores desafíos de seguridad pública. Los métodos tradicionales de asignación de patrullaje policial se basan en mapas de calor (KDE) estáticos y denuncias históricas agregadas mensualmente, lo que impide una respuesta preventiva en tiempo real y a nivel de micro-cuadrantes (escala de calle). El presente proyecto implementa un sistema inteligente basado en inteligencia artificial no euclidiana (Redes Neuronales de Grafos - GNN) para predecir puntos calientes (hotspots) delictivos con una resolución espacial de micro-cuadrantes y una ventana temporal diaria, optimizando los recursos de patrullaje de la PNP. Debido al secreto estadístico y confidencialidad de los datos de la PNP, esta investigación se encuadra oficialmente como un **"Framework Metodológico de Simulación en Entornos de Escasez de Datos"** (Simulation Framework in Data-Sparse Environments), el cual permite modelar dinámicas sobre topologías viales virtuales y distribuciones bimodales realistas.

### b. Descripción de la empresa
La **Policía Nacional del Perú (PNP)**, a través de la **Dirección de Inteligencia (DIRIN)** y las Divisiones de Emergencia (DIVEME), es la entidad encargada de planificar, coordinar y ejecutar acciones preventivas y tácticas contra la delincuencia común y organizada en el territorio nacional.

### c. Visión
Ser una institución policial moderna, eficiente y transparente al año 2030, integrada con tecnologías de vanguardia y análisis de datos avanzados para garantizar la paz social y la seguridad ciudadana.

### d. Misión
Garantizar, mantener y restablecer el orden interno, prestar ayuda y protección a la comunidad, y prevenir e investigar la delincuencia mediante el uso estratégico de herramientas tecnológicas de inteligencia policial.

### e. Análisis de Negocio (Lean Canvas)

| Problema | Solución | Propuesta de Valor | Ventaja Especial | Segmento de Clientes |
| :--- | :--- | :--- | :--- | :--- |
| 1. Patrullaje ineficiente y reactivo.<br>2. Concentración de recursos en zonas incorrectas.<br>3. Alta cifra negra del delito que sesga las estadísticas. | 1. Algoritmo ST-GNN que captura relaciones espaciotemporales.<br>2. API en tiempo real con niveles de alerta (Semáforo).<br>3. Panel visual interactivo. | Optimización del 40% en la efectividad del patrullaje preventivo policial mediante alertas predictivas a nivel de micro-cuadrantes bajo un framework de simulación. | Modelo entrenado en topología vial física real (OSM) y correlacionado con factores temporales bimodal-diarios. | 1. Comisarías de Lima Metropolitana.<br>2. Central de Emergencias 105.<br>3. Municipalidades (Serenazgo). |
| **Alternativas Existentes:**<br>Mapas de calor manuales Excel; Patrullaje por intuición. | **Métricas Clave:**<br>1. Cobertura del delito (Recall F2 > 85%).<br>2. Latencia API < 500ms.<br>3. Precisión Alerta > 50%. | **Canales:**<br>API interna segura (FastAPI); Aplicación web policial intranet (React). | **Estructura de Costos:**<br>Infraestructura Cloud (Supabase/Render); Entrenamiento GPU AWS. | **Flujo de Valor:**<br>Reducción del índice de robos callejeros; Incremento de detenciones en flagrancia. |

### f. Mapa de Procesos (AS-IS)
```mermaid
graph TD
    A[Ocurre un Delito] --> B[Denuncia del Ciudadano en Comisaría]
    B --> C[Registro en el Sistema SIDPOL]
    C --> D[Análisis de Estadísticas Mensuales]
    D --> E[Diseño Manual de Ruta de Patrullaje]
    E --> F[Patrullaje Reactivo]
```

### g. Oportunidades de mejora y modelo propuesto (TO-BE)
El modelo propuesto automatiza la ingesta y georreferenciación de los delitos, entrenando una Red Neuronal de Grafos (GNN) que interactúa directamente con el historial delictivo y factores calendáricos y climatológicos.

```mermaid
graph TD
    A[Denuncia en Base de Datos Supabase] --> B[Pipeline ETL Automatizado]
    B --> C[Construcción del Grafo de Calles/Cuadrantes]
    C --> D[Inferencia ST-GNN en Tiempo Real]
    D --> E[Generación de Hotspots y Alertas de Riesgo]
    E --> F[Patrullaje Preventivo Focalizado en Zonas Rojas]
```

---

## 2. Planificación y Gestión del Proyecto

### a. Project Charter (Ficha de Constitución)
*   **Nombre del Proyecto:** Sistema de Inteligencia Espaciotemporal GNN para la PNP.
*   **Patrocinador:** Dirección de Tecnología de la Información y Comunicaciones (DIRTIC - PNP).
*   **Líder de Proyecto:** Josué (Estudiante Tesista).
*   **Objetivo Principal:** Reducir la latencia de respuesta predictiva a menos de 500ms y lograr un Recall de detección superior al 85% sobre cuadrantes viales.

### b. Alcance y objetivos del proyecto
*   **En Alcance:** Pipeline de datos espaciales (PostGIS), módulo de entrenamiento ST-GNN, API REST segura de inferencia (FastAPI) con buffer en memoria, y panel React de visualización.
*   **Fuera de Alcance:** Integración física con GPS de patrullas policiales en esta fase.

### c. Cronograma del proyecto (Diagrama de Gantt)
```
[Fase 1: Ingesta y Limpieza]   ████████ 100%
[Fase 2: Arquitectura GNN]     ████████ 100%
[Fase 3: Integración DB/API]   ████████ 100%  <-- HITO ACTUAL APF2
[Fase 4: Despliegue y Pruebas] ████████ 100%  <-- HITO ACTUAL APF2
[Fase 5: Validación Operativa] ░░░░░░░░ 0% (Fase Final)
```

### d. Planificación ágil – Sprint Planning
*   **Sprint 1:** Modelamiento Físico de Base de Datos y Creación de Repositorios (DAO).
*   **Sprint 2:** Implementación del Módulo de Seguridad (JWT + IP Rate Limiter).
*   **Sprint 3:** Pruebas Locales de Integración y Pruebas de Seguridad Web (ZAP).
*   **Sprint 4:** Dockerización, Configuración de CI/CD y Despliegue Cloud en Render.

### e. Historias de usuario (User Stories)

#### Historia de Usuario 1: Autenticación Policial
*   **Como:** Comisario de la Comisaría de Lima.
*   **Quiero:** Iniciar sesión con mis credenciales institucionales de manera segura.
*   **Para:** Acceder al mapa predictivo y coordinar el patrullaje diario del sector.
*   **Criterio de Aceptación (Gherkin):**
    ```gherkin
    Dado que el usuario ingresa su correo y contraseña válidos
    Cuando presiona el botón "Iniciar Sesión"
    Entonces el sistema debe retornar un token JWT firmado y redirigir al panel de control.
    Y si intenta loguearse incorrectamente más de 5 veces, su IP debe ser bloqueada por 15 minutos, y debe registrarse una traza CRITICAL en auditoria_pnp.log.
    ```

#### Historia de Usuario 2: Consulta Predictiva GNN
*   **Como:** Analista de Inteligencia de la DIRIN.
*   **Quiero:** Consultar las zonas rojas delictivas (hotspots) para las siguientes 24 horas.
*   **Para:** Exportar las coordenadas prioritarias a las patrullas tácticas de la DIVEME.
*   **Criterio de Aceptación (Gherkin):**
    ```gherkin
    Dado que el analista está autenticado en el sistema
    Cuando envía la fecha y distrito para consulta
    Entonces la API procesa la inferencia mediante el tensor de buffer precargado
    Y retorna un JSON ordenado con los hotspots de nivel "Rojo" y "Amarillo" en menos de 500ms.
    ```

---

## 3. Selección y Configuración de Herramientas de Desarrollo

### a. Selección de herramientas
*   **Backend:** FastAPI (Python 3.10+) por su alto rendimiento asíncrono y auto-documentación OpenAPI (Swagger).
*   **Base de Datos:** PostgreSQL 16 con extensión espacial PostGIS (alojado en Supabase AWS).
*   **Librerías Core IA:** PyTorch 2.5.1 y PyTorch Geometric (PyG).
*   **Seguridad:** Bcrypt (hashing de claves), PyJWT (autenticación) y un limitador de tasa de peticiones personalizado.
*   **Despliegue:** Docker (Containerización), docker-compose, y Render Cloud.

### b. Evidencias de configuración de herramientas
La configuración de variables de entorno y base de datos se maneja a través de un archivo `.env` centralizado leído por la clase `Settings` en `src/core/config.py`.

```ini
# Archivo de Configuración de Entorno (.env)
DATABASE_URL=postgresql://postgres.[ID_SUPABASE]:[CLAVE]@aws-1-us-east-1.pooler.supabase.com:5432/postgres
SECRET_KEY=pnppredictivo_secreto_super_seguro_2026
```

### c. Repositorio GitHub
Estructura del repositorio alineada con las mejores prácticas de arquitectura modular y desacoplada (ver sección 3.c del plan anterior).

---

## 4. Prototipos (Mockups de Alta Fidelidad)

El frontend de la aplicación (React + Vite) interactúa con la API backend para pintar en tiempo real los cuadrantes priorizados:
1.  **Pantalla de Login:** Formulario limpio con cifrado del lado del cliente, protegido contra inyección de SQL y limitación de tasa visualizable.
2.  **Panel de Visualización Mapbox/Leaflet:** Renderiza la grilla vial de los 400 nodos de Lima Metropolitana. Los cuadrantes cambian de color según el score de inferencia de la API (`predict/predecir`):
    *   🔴 **Zonas Rojas:** Score $\ge 0.007$ (Prioridad Crítica de patrullaje).
    *   🟡 **Zonas Amarillas:** Score entre $0.0007$ y $0.007$ (Monitoreo Preventivo).
    *   🟢 **Zonas Verdes:** Score $< 0.0007$ (Bajo Riesgo).

---

## 5. Gestión de Riesgos del Proyecto

### a. Identificación y Matriz de Riesgos (Heatmap)
(Ver matriz 5.a del plan unificado anterior).

### b. Plan de gestión de riesgos
*   **Mitigación R1:** Inyección de secrets mediante variables de entorno del contenedor Docker y exclusión de `.env` en `.gitignore`.
*   **Mitigación R2:** Implementación de IP Rate Limiting en el middleware de FastAPI para evitar ataques DDoS y de fuerza bruta.
*   **Mitigación R3:** Implementación de re-entrenamiento mensual automático del modelo cargando pesos previos (transfer learning).

---

## 6. Definición de Métricas y Niveles de Servicio (SLA/SLO)

### a. KPIs del sistema y del negocio
*   **Recall Espaciotemporal ($F_2$-Score):** Debe ser superior al 85% para priorizar la sensibilidad sobre la precisión, garantizando que el patrullaje policial cubra el máximo posible de delitos reales, evitando puntos ciegos.
*   **Latencia de Inferencia:** Tiempo promedio transcurrido desde la recepción del JSON hasta la respuesta procesada de hotspots.

### b. Definición de SLA y SLO
*   **SLA (Service Level Agreement):** Disponibilidad de la API Predictiva del **99.9%** mensual y respuesta en menos de **500ms** para las comisarías del sector.
*   **SLO (Service Level Objective):**
    *   **SLO 1:** 95% de las peticiones de inferencia (`P95 Latency`) deben ser resueltas en menos de **250ms**.
    *   **SLO 2:** Tasa de error HTTP 5xx menor al **0.1%** mensual.

### c. Plan de medición y monitoreo
*   Se utilizará la biblioteca interna de `logging` en Python (`src/utils/logger.py`) para registrar todas las transacciones de inferencia en archivos rotativos en el volumen seguro del backend.
*   En producción se implementará **Prometheus** y **Grafana** para graficar latencias y consumo de memoria del proceso de inferencia de PyTorch.

---

## 7. Desarrollo e Implementación Técnica

### a. Arquitectura general del sistema
El sistema se rige bajo una arquitectura desacoplada basada en capas de software tradicionales para aplicaciones empresariales robustas:

```
[ Capa de Presentación (React Intranet) ]
                   │ (HTTP / JSON / JWT)
                   ▼
[ Capa de Controladores (FastAPI - routes/) ]
                   │
                   ▼
[ Capa de Servicios (Inferencia GNN / MLOps) ] ── (Carga pesos_stgnn_pnp.pth)
                   │
                   ▼
[ Capa de Acceso a Datos (Repository Pattern) ]
                   │ (SQLAlchemy ORM)
                   ▼
[ Base de Datos Física (Supabase PostgreSQL + PostGIS) ]
```

### b. Estructura del código fuente del backend
La estructura se implementa según el diagrama presentado en la sección 3.c.

### c. Estrategias WPO (Web Performance Optimization) y Optimización de la IA

Para asegurar la latencia de inferencia y la estabilidad del sistema en micro-cuadrantes de Lima Metropolitana, se implementaron las siguientes estrategias de optimización de rendimiento:

1.  **Optimización CUDA Acotada (Vectorización Espacial):**
    Se elimina el bucle secuencial espacial `for b in range(batch_size)` en el método `forward()` del modelo de grafos. Esto se logra paralelizando sobre la dimensión espacial (el lote de grafos) empaquetando el lote en un único grafo disjunto nativo usando `torch_geometric.data.Batch`. Para preservar la dinámica y dependencia temporal delictiva diaria, la dimensión temporal ($T=14$) se conserva secuencial e iterativa alimentando a la unidad GRU.
2.  **Activación Softplus en la Salida:**
    Se reemplaza el parche post-hoc `np.maximum(predicciones_array, 0)` en la capa final del modelo de grafos por la función de activación continua `nn.Softplus()`. Esta función matemática garantiza salidas estrictamente no negativas ($\ge 0$), previniendo el fenómeno de la "ReLU muerta" en las múltiples zonas metropolitanas con baja tasa de denuncias y manteniendo estables los gradientes durante la fase de entrenamiento.
3.  **Buffer de Características Asíncrono en RAM:**
    Para evitar consultar y estructurar el tensor histórico `[14, 400, 5]` de manera síncrona en tiempo real con cada petición (lo cual causaría latencias de E/S de base de datos insostenibles), el servicio mantiene un búfer asíncrono en RAM que actualiza los datos delictivos acumulados cada 14 días. Al ingresar la petición, el backend simplemente inyecta las variables dinámicas de fecha del día consultado en fracciones de milisegundo.

---

## 8. Implementación y Administración de Base de Datos

### a. Diseño físico de base de datos
El diseño de la base de datos se enfoca en el soporte espaciotemporal y el control de accesos policiales.

#### Script SQL DDL de Creación (Anexo A):
El script completo habilita la extensión geoespacial `postgis`, crea las tablas de auditoría, las tablas espaciales de distritos y cuadrantes utilizando columnas `GEOMETRY` de SRID 4326 (WGS84), y las tablas de IA (`modelos_gnn`, `predicciones`).

### b. Informe de Administración y Replicación
*   **Motor de Base de Datos:** PostgreSQL 16 (Alojado en Supabase - AWS us-east-1).
*   **Tipo de Replicación Propuesta:** **Replicación por Transmisión Asíncrona (Streaming Replication)** con una instancia de base de datos principal de escritura (Write) y dos instancias de réplicas de lectura (Read-Only) distribuidas para balancear la carga de consultas geográficas complejas del frontend React.
*   **Estrategia de Respaldo (Backup):** Copias de seguridad automáticas diarias a las 02:00 (hora local de menor tráfico) gestionadas por Supabase con retención de 7 días, además de backups lógicos semanales cifrados y almacenados en AWS S3.
*   **Justificación Técnica:** PostGIS proporciona funciones de indexación espacial tipo R-Tree (GIST) indispensables para consultas geoespaciales veloces a nivel de micro-cuadrantes de Lima.
*   **Trabajos Futuros:** Se ha planificado la migración del rate limiter local en memoria hacia una arquitectura distribuida que centralice el estado de peticiones de manera segura utilizando **Redis** en una infraestructura multi-nodo.

### c. Implementación del Patrón de Acceso a Datos (DAO/Repository)
(Ver diagramas y código en la sección 8.c del informe anterior).

---

## 9. Seguridad del Sistema

### a. Catálogo de Controles de Seguridad del Proyecto (ISO 27001 / OWASP)
1.  **A1: Inyección (OWASP):** Uso obligatorio de SQLAlchemy ORM que parametriza todas las sentencias SQL de manera automática, neutralizando inyecciones SQL.
2.  **A2: Pérdida de Autenticación (OWASP):** Implementación de firmas digitales simétricas HMAC con SHA-256 para JWT con expiración de 8 horas.
3.  **A4: Exposición de Datos Sensibles (OWASP):** Cifrado de contraseñas de agentes en reposo utilizando **Bcrypt** con un factor de trabajo de 12.
4.  **Trabajo Futuro (Seguridad):** Despliegue de un backend Redis para almacenar los tokens inactivos (blacklist) y evitar fugas de sesión.

### b. Módulo de Autenticación y Autorización
*   El login verifica al usuario contra la base de datos Supabase utilizando `UserRepository`.
*   Si las credenciales coinciden, genera el JWT agregando el rol del agente policial.
*   El endpoint de predicción está protegido con la inyección de dependencias `Depends(get_current_user)` que extrae y valida el token JWT del header `Authorization`.

### c. Informe Técnico de Seguridad, Cifrado de Datos y Trazabilidad
*   **En Tránsito:** Todo tráfico entre React, FastAPI y Supabase viaja forzosamente cifrado mediante **HTTPS/TLS 1.3**.
*   **En Reposo:** Contraseñas encriptadas con Bcrypt. Supabase cifra el almacenamiento de PostgreSQL utilizando cifrado AES-256 a nivel de disco de AWS.
*   **Trazabilidad y Evidencia Forense:** Cada login fallido o exitoso y cada petición de inferencia genera un registro de auditoría en la consola y logs locales mediante `src/utils/logger.py`. El sistema escribe una traza de nivel `CRITICAL` cuando se detecta y bloquea una IP por fuerza bruta:
    ```
    2026-05-20 04:40:15 | [CRITICAL] | DEFENSA ACTIVA: IP 190.235.12.98 bloqueada por fuerza bruta (Máx. 5 intentos).
    ```

### d. Prueba de seguridad web (Kali Linux / OWASP ZAP)
(Ver reporte 9.d del informe anterior).

---

## 10. Validación y Verificación del Sistema

### a. Plan de pruebas del sistema
*   **Alcance:** Cobertura total de los endpoints del backend (`/auth/login` y `/predict/predecir`) y validación física de escritura de logs forenses en `logs/auditoria_pnp.log`.
*   **Herramienta:** Script de validación automatizada mediante `TestClient` de FastAPI.

### b. Casos de Prueba del Sistema (Especificación)

| ID Caso | Escenario de Prueba | Entrada | Resultado Esperado | Resultado Real |
| :--- | :--- | :--- | :--- | :--- |
| **TC-001** | Autenticación Exitosa | Email: `analista@pnp.gob.pe`<br>Password válido. | HTTP 200 con Token JWT Bearer. | **Exitoso** |
| **TC-002** | Autenticación Fallida | Email: `usuario_invalido@pnp.gob.pe` | HTTP 401 Credenciales incorrectas. | **Exitoso** |
| **TC-003** | Mitigación Fuerza Bruta y Evidencia Forense | 5 logins erróneos desde IP local. | HTTP 429 Demasiados intentos fallidos. IP bloqueada. Aserción de escritura `CRITICAL` en `logs/auditoria_pnp.log`. | **Exitoso** |
| **TC-004** | Inferencia GNN Protegida | Petición `/predict/predecir` sin Header Auth. | HTTP 401 Unauthorized. | **Exitoso** |
| **TC-005** | Inferencia GNN Válida | Token JWT Bearer + Fecha de consulta. | HTTP 200 con JSON de hotspots en menos de 500ms mediante búfer de caché en RAM. | **Exitoso** |

---

## 11. Despliegue

### a. Manual de despliegue cloud
(Ver sección 11.a del informe anterior).

### b. Evidencia de pruebas de despliegue
*   **Health Check de Inferencia:** Acceso a `https://api-gnn-pnp.onrender.com/docs` cargando correctamente la interfaz OpenAPI de Swagger.
*   **Validación de Logs de Ejecución:**
    ```
    === INICIANDO SERVIDOR DE INTELIGENCIA PNP ===
    [INFO] Carga exitosa de pesos_stgnn_pnp.pth en CPU
    [INFO] Carga de grafo_edge_index.npz exitosa (400 nodos)
    ¡Sistema Predictivo Operativo, Seguro y en Línea!
    Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    ```

---

## Anexos

### Anexo A. Script SQL DDL de la Base de Datos
Corresponde al script SQL provisto por el usuario en Supabase.

### Anexo B. Script de Verificación Automatizada (`verify_system.py`)
El script automatizado que simula el plan de pruebas utilizando el cliente de FastAPI e incluye la validación de la traza de logs forenses.

```python
# verify_system.py
from fastapi.testclient import TestClient
from src.api.main import app
from pathlib import Path

client = TestClient(app)

def test_rate_limit_and_log_assertion():
    # Intentamos loguearnos 5 veces con datos incorrectos
    for _ in range(5):
        client.post("/auth/login", json={"email": "sospechoso@pnp.gob.pe", "password": "mal"})
    
    # El 6to intento debe dar HTTP 429
    response = client.post("/auth/login", json={"email": "sospechoso@pnp.gob.pe", "password": "mal"})
    assert response.status_code == 429
    
    # Verificamos físicamente la escritura del log forense
    log_path = Path("logs/auditoria_pnp.log")
    assert log_path.exists()
    
    log_content = log_path.read_text(encoding="utf-8")
    assert "DEFENSA ACTIVA" in log_content or "bloqueada por fuerza bruta" in log_content
```

### Referencias Bibliográficas
*   Brantingham, P. J., & Brantingham, P. L. (2013). *Criminality of place: Directed patrols and hot spots*.
*   Kipf, T. N., & Welling, M. (2016). *Semi-supervised classification with graph convolutional networks*. arXiv preprint arXiv:1609.02907.
