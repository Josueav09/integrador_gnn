# Registro de Pruebas Automatizadas - PNP GNN SPRED

Este documento detalla todas las **49 pruebas automatizadas** implementadas en el proyecto, divididas en pruebas de Frontend (Vitest), pruebas de Backend (Pytest) y pruebas de interfaz de extremo a extremo (Selenium).

---

## 1. Pruebas del Frontend (Vite & Vitest)
Ejecutadas localmente con el comando:
```bash
npm run test:run
```
Ubicación: `fronted_GNN/Frontend---Integrador-2/`

Hay **27 pruebas** distribuidas en 9 archivos de pruebas:

### 1.1. `VerifyVitest.test.tsx` (1 prueba)
*   **Prueba 1:** `debe ejecutar una aserción matemática básica correctamente`
    *   *Descripción:* Valida que el framework de testing Vitest esté instalado y responda correctamente con una operación básica (1 + 1 = 2).

### 1.2. `apiError.test.ts` (4 pruebas)
*   **Prueba 2:** `should parse simple error message`
    *   *Descripción:* Verifica que los errores simples de texto devueltos por el backend se extraigan y formateen de forma amigable para la interfaz.
*   **Prueba 3:** `should handle array of error details`
    *   *Descripción:* Procesa las estructuras de error complejas en formato de lista (por ejemplo, errores de validación de esquemas de FastAPI).
*   **Prueba 4:** `should handle object error structures`
    *   *Descripción:* Verifica la correcta lectura e interpretación de las respuestas de error en formato JSON estructurado.
*   **Prueba 5:** `should fallback to default error message`
    *   *Descripción:* Si la API devuelve un error nulo o un formato irreconocible, el frontend muestra un mensaje genérico por defecto.

### 1.3. `uploadValidation.test.ts` (7 pruebas)
*   **Prueba 6:** `should validate correct CSV extensions`
    *   *Descripción:* Permite el procesamiento del archivo si su extensión es estrictamente `.csv`.
*   **Prueba 7:** `should validate correct JSON extensions`
    *   *Descripción:* Permite el procesamiento del archivo si su extensión es estrictamente `.json`.
*   **Prueba 8:** `should reject other file extensions`
    *   *Descripción:* Bloquea y muestra un error si el usuario intenta cargar formatos de archivo no permitidos (ej. `.xlsx`, `.pdf`).
*   **Prueba 9:** `should detect empty files (0 bytes)`
    *   *Descripción:* Lanza una alerta e impide el envío si el archivo seleccionado tiene un peso de 0 bytes.
*   **Prueba 10:** `should validate correct CSV headers`
    *   *Descripción:* Comprueba que el archivo CSV posea exactamente las cabeceras requeridas (`id_cuadrante`, `id_tipo_delito`, `fecha_delito`, `ubicacion`).
*   **Prueba 11:** `should detect missing CSV headers`
    *   *Descripción:* Lanza error de validación indicando qué columna obligatoria falta en las cabeceras.
*   **Prueba 12:** `should validate syntax of JSON files`
    *   *Descripción:* Realiza un parseo previo en JS para garantizar que el archivo JSON cargado tenga un formato y sintaxis válidos.

### 1.4. `StatusBanner.test.tsx` (3 pruebas)
*   **Prueba 13:** `should render success status`
    *   *Descripción:* Valida la correcta visualización del banner en verde y el icono correspondiente para los casos de éxito.
*   **Prueba 14:** `should render warning/error status`
    *   *Descripción:* Comprueba la renderización del banner en color rojo para los casos de error/alerta.
*   **Prueba 15:** `should support autohide and close button`
    *   *Descripción:* Verifica la correcta interacción del botón de descarte (`x`) y el flujo de ocultación automática.

### 1.5. `AuthContext.test.tsx` (3 pruebas)
*   **Prueba 16:** `should initialize with no token/user`
    *   *Descripción:* Comprueba que al cargar la aplicación sin sesión previa, los estados de token y usuario inicialicen en nulo/vacío.
*   **Prueba 17:** `should set credentials on login`
    *   *Descripción:* Valida que al autenticarse de forma exitosa, el token JWT y el rol del usuario se almacenen correctamente en el estado global.
*   **Prueba 18:** `should clear credentials on logout`
    *   *Descripción:* Asegura que al cerrar sesión, se elimine el token del localStorage y los estados del usuario vuelvan a su estado inicial.

### 1.6. `GuestRoute.test.tsx` (2 pruebas)
*   **Prueba 19:** `should allow access to non-authenticated users`
    *   *Descripción:* Permite el acceso libre a los formularios de Login y Registro para usuarios que no han iniciado sesión.
*   **Prueba 20:** `should redirect to dashboard if already authenticated`
    *   *Descripción:* Si un usuario con sesión activa intenta ingresar a la URL de `/login`, el sistema lo redirige de forma automática al `/dashboard`.

### 1.7. `ProtectedRoute.test.tsx` (2 pruebas)
*   **Prueba 21:** `should allow access to authenticated users`
    *   *Descripción:* Permite visualizar las páginas internas del sistema (ej. Mapa de Calor, Administración) si la credencial es válida.
*   **Prueba 22:** `should redirect to login if unauthenticated`
    *   *Descripción:* Si un usuario anónimo intenta acceder a una URL del Dashboard, el sistema lo bloquea y lo redirige al `/login`.

### 1.8. `RegisterPage.test.tsx` (2 pruebas)
*   **Prueba 23:** `should keep submit button disabled if form invalid`
    *   *Descripción:* El botón de registro se mantiene deshabilitado mientras falten campos requeridos o tengan errores de validación.
*   **Prueba 24:** `should call register API on valid form submission`
    *   *Descripción:* Valida el consumo del endpoint del backend de registro de usuario cuando todos los datos del formulario son correctos.

### 1.9. `LoginPage.test.tsx` (3 pruebas)
*   **Prueba 25:** `should disable submit button by default`
    *   *Descripción:* Por usabilidad y seguridad, el botón para iniciar sesión arranca bloqueado hasta que el usuario digite los datos.
*   **Prueba 26:** `should validate email format in real time`
    *   *Descripción:* Muestra una alerta roja dinámica si el usuario ingresa un formato de correo incorrecto (o no institucional de la PNP).
*   **Prueba 27:** `should enable button and call login API on submit`
    *   *Descripción:* Habilita el botón tras ingresar credenciales con formato válido y valida el flujo de envío de datos.

---

## 2. Pruebas del Backend (Python & Pytest)
Ejecutadas localmente con el comando:
```bash
.venv\Scripts\pytest.exe
```
Ubicación: `Predicciones_GNN/`

Hay **14 pruebas** distribuidas en 4 archivos de pruebas:

### 2.1. `test_db_integration.py` (2 pruebas)
*   **Prueba 28:** `test_database_handshake`
    *   *Descripción:* Mide la latencia (RTT) en lecturas a la base de datos Supabase/PostgreSQL y confirma que responda en menos de 5 segundos.
*   **Prueba 29:** `test_smtp_delivery_task`
    *   *Descripción:* Asegura que la API retorne éxito inmediato y envíe la plantilla de restablecimiento de contraseña en segundo plano (`BackgroundTasks`) sin bloquear la petición HTTP del usuario.

### 2.2. `test_denuncias.py` (3 pruebas)
*   **Prueba 30:** `test_denuncia_publica_rechazo_xss`
    *   *Descripción:* Verifica que Pydantic y el backend intercepten y bloqueen con código HTTP 422 cualquier denuncia pública con inyección de código script HTML/JS (XSS).
*   **Prueba 31:** `test_denuncia_publica_rechazo_sqli`
    *   *Descripción:* Valida que el backend detecte palabras clave sospechosas de SQLi en las descripciones y responda con HTTP 422.
*   **Prueba 32:** `test_denuncia_publica_valida_exitosa`
    *   *Descripción:* Envía un caso de denuncia legítimo y comprueba la creación correcta en la base de datos, retornando HTTP 201 y su identificador único.

### 2.3. `test_security_robustness.py` (5 pruebas)
*   **Prueba 33:** `test_bloqueo_fuerza_bruta_login_http_429`
    *   *Descripción:* Prueba que al simular 5 credenciales inválidas desde una misma dirección IP, el sistema restrinja las solicitudes subsiguientes retornando un código de estado HTTP 429 (Too Many Requests).
*   **Prueba 34:** `test_rate_limit_forgot_password_spam_smtp`
    *   *Descripción:* Comprueba que el limitador de tasa bloquee peticiones sospechosas consecutivas de restablecimiento de contraseña a correos inexistentes para mitigar ataques de denegación de servicio SMTP.
*   **Prueba 35:** `test_rate_limit_verify_code_pin`
    *   *Descripción:* Bloquea y restringe IPs que busquen adivinar por fuerza bruta los códigos PIN de 6 dígitos temporales enviados al correo.
*   **Prueba 36:** `test_bloqueo_sqli_denuncia_publica`
    *   *Descripción:* Comprobación reiterativa de seguridad sobre las validaciones anti-inyección SQL en denuncias ciudadanas.
*   **Prueba 37:** `test_bloqueo_xss_denuncia_publica`
    *   *Descripción:* Comprobación reiterativa contra XSS malicioso en la entrada del canal ciudadano.

### 2.4. `test_upload_validation.py` (4 pruebas)
*   **Prueba 38:** `test_validate_csv_bytes_ok`
    *   *Descripción:* Valida el procesamiento correcto de un CSV cargado en bytes con cabeceras y estructura válidas.
*   **Prueba 39:** `test_validate_csv_bytes_missing_columns`
    *   *Descripción:* Lanza un error controlado de tipo `ValueError` al detectar la ausencia de columnas requeridas en el archivo CSV subido.
*   **Prueba 40:** `test_validate_json_bytes_ok`
    *   *Descripción:* Asegura el análisis y mapeo exitoso de registros estructurados dentro de un archivo JSON binario.
*   **Prueba 41:** `test_validate_json_bytes_invalid_syntax`
    *   *Descripción:* Captura las excepciones de formato y lanza un error amigable si el archivo JSON tiene errores de sintaxis o llaves corruptas.

---

## 3. Pruebas E2E de Interfaz (Selenium WebDriver)
Ejecutadas localmente con el comando:
```bash
.venv\Scripts\python.exe tests_automatizados_selenium/test_suite.py
```
Ubicación: `tests_automatizados_selenium/`

Hay **8 pruebas** funcionales integrales:

### 3.1. `STGNNTestSuite` (8 pruebas)
*   **Prueba 42:** `test_01_public_crime_report`
    *   *Descripción:* Abre el formulario público, simula la carga de un tipo de delito y su descripción, realiza un clic dinámico sobre el mapa de calor Leaflet para ubicar las coordenadas y realiza el envío, confirmando que la denuncia aparezca en la base de datos de cuarentena.
*   **Prueba 43:** `test_02_login_validation_flow`
    *   *Descripción:* Valida que el botón de login esté bloqueado inicialmente, simula un correo mal formado y comprueba el mensaje de asistencia visual rojo en tiempo real, ingresa credenciales válidas PNP y confirma la aparición del toast verde de éxito y la redirección al Dashboard.
*   **Prueba 44:** `test_03_dashboard_filters`
    *   *Descripción:* Simula la navegación por las métricas de criminalidad, manipula los filtros interactivos de año y distrito, y comprueba que los componentes y los gráficos de Recharts se actualicen sin interrupciones.
*   **Prueba 45:** `test_04_gis_crime_map`
    *   *Descripción:* Abre el visor geográfico policial, selecciona un distrito, cambia al modo "Predicción GNN" y dispara la inferencia táctica espaciotemporal, validando la colocación de los marcadores dinámicos en el mapa.
*   **Prueba 46:** `test_05_quarantine_inbox`
    *   *Descripción:* Navega a la bandeja de denuncias ciudadanas, comprueba la lista e interactúa aprobando una de las denuncias pendientes, verificando que se promueva automáticamente a la tabla de crímenes principal.
*   **Prueba 47:** `test_06_admin_retrain_pipeline`
    *   *Descripción:* Accede al módulo de administración, dispara la tarea asíncrona de reentrenamiento del modelo de inteligencia artificial y comprueba que se empiece a mostrar el pipeline animado y la consola de logs.
*   **Prueba 48:** `test_07_admin_upload_validation_errors`
    *   *Descripción:* Sube archivos secuencialmente y comprueba que la UI responda con alertas rojas específicas ante extensiones incorrectas (.xlsx), archivos sin peso (0 bytes), CSV con columnas faltantes y, finalmente, un toast verde de éxito con el archivo CSV válido.
*   **Prueba 49:** `test_08_register_validation_flow`
    *   *Descripción:* Simula el registro de una cuenta policial validando en tiempo real las asistencias rojas por campos vacíos, correos institucionales inválidos o contraseñas débiles, terminando en la confirmación de registro.
