# Pruebas Automatizadas de Interfaz y Usabilidad (Selenium WebDriver)

Este directorio contiene la suite de pruebas automatizadas de extremo a extremo (E2E) para certificar la calidad funcional y la usabilidad (ISO/IEC 25010) del sistema ST-GNN.

## Prerrequisitos

Para ejecutar estas pruebas en tu máquina host (Windows), necesitas:
1. Tener instalado **Python 3** en tu sistema.
2. Tener instalado el navegador **Google Chrome**.
3. Asegurarte de que tus contenedores Docker (`gnn_frontend` y `pnp-backend`) estén encendidos y operativos en los puertos estándar (`localhost:3000` y `localhost:8000`).

---

## Instrucciones de Ejecución

### Paso 1: Instalar dependencias
Abre una terminal (PowerShell o CMD) en esta carpeta (`tests_automatizados_selenium/`) e instala las librerías necesarias ejecutando:

```bash
pip install -r requirements.txt
```

*Nota: La librería `webdriver-manager` se encargará de descargar y enlazar el controlador ChromeDriver correspondiente a tu versión de Chrome de manera automática.*

### Paso 2: Correr las pruebas
Para ejecutar la suite de pruebas unificada, corre el siguiente comando en tu consola:

```bash
python test_suite.py
```

Al hacerlo, verás cómo se abre automáticamente una ventana de Google Chrome, realiza las interacciones (Login, filtros del Dashboard, reportar denuncia en el mapa Leaflet, aprobación en cuarentena y activación de reentrenamiento) y se cierra al finalizar.

---

## Configurar otra URL (Opcional)

Por defecto, el script de Selenium apunta al puerto expuesto de producción en Docker (`http://localhost:3000`). Si deseas correr las pruebas contra tu servidor de desarrollo Vite (`http://localhost:5173`), puedes definir la variable de entorno `FRONTEND_URL`:

*   **En PowerShell (Windows):**
    ```powershell
    $env:FRONTEND_URL="http://localhost:5173"; python test_suite.py
    ```
*   **En CMD (Windows):**
    ```cmd
    set FRONTEND_URL=http://localhost:5173 && python test_suite.py
    ```
*   **En Linux / macOS:**
    ```bash
    FRONTEND_URL="http://localhost:5173" python test_suite.py
    ```
