# Auditoría Arquitectónica del Frontend (APF2)

## Goal
Diagnosticar la madurez técnica del repositorio frontend (`Frontend---Integrador-2`) y diseñar una hoja de ruta para su acoplamiento con el backend predictivo (FastAPI + GNN + Supabase), logrando el cumplimiento de la rúbrica universitaria y los estándares requeridos.

---

## 1. Estado Actual del Sistema (Hallazgos Clínicos)

Tras realizar un análisis profundo del árbol de directorios, `package.json`, y los componentes React, el diagnóstico es claro: **El frontend actual es un prototipo estático (Mockup UI).** 

Tiene un diseño excepcional, pero carece de integración lógica real.

### > [!WARNING] Brechas Críticas Identificadas
1. **Ausencia de Networking (APIs):** No existen librerías de cliente HTTP (como `axios` o `@tanstack/react-query`), ni llamadas nativas `fetch`. Todo el sistema está desconectado del backend.
2. **Datos "Quemados" (Hardcoded):** Absolutamente todos los gráficos, métricas, y estadísticas se importan desde `src/data/mockData.ts` (un archivo de 260 líneas con datos falsos).
3. **Falsa Autenticación:** El archivo `src/contexts/AuthContext.tsx` finge el inicio de sesión. Simplemente guarda el email ingresado en el `localStorage` del navegador sin validarlo contra el backend ni generar un token JWT.
4. **Simulación GIS (Mapa Falso):** La vista `CrimeMapPage.tsx` no utiliza motores de renderizado cartográfico real (como Leaflet o Mapbox). El "mapa" está construido mediante etiquetas `<div>` con coordenadas CSS absolutas (`top`, `left`).

---

## 2. Impacto en la Rúbrica Universitaria (APF2)

De presentar el proyecto en este estado, existiría un alto riesgo de demérito en la calificación, dado que:
*   **"Integración con Base de Datos"**: Incumplido. El front no lee de Supabase.
*   **"Controles de Seguridad"**: Incumplido. El front es vulnerable al no validar JWT.
*   **"Validación del Servicio"**: Incumplido. No hay consumo real de la GNN.

---

## 3. Plan de Integración Propuesto (Aprobado)

Para transformar este diseño UI en una aplicación completamente funcional acoplada a nuestro backend de FastAPI, ejecutaremos la siguiente hoja de ruta secuencial:

### FASE 1: Capa de Red y Autenticación Segura (Prioridad 1)
*   **[NEW]** Instalar `axios` y configurar un interceptor (`src/api/client.ts`) para inyectar automáticamente el token JWT en cada petición.
*   **[MODIFY]** `src/contexts/AuthContext.tsx`: Conectarlo al endpoint `POST /auth/login` del backend de FastAPI, validando credenciales reales de Supabase y almacenando de forma segura el JWT devuelto.
*   **[MODIFY]** Configurar CORS en FastAPI para aceptar peticiones desde el frontend (puerto 5173).

### FASE 2: Consumo del Motor GNN (Predicciones)
*   **[MODIFY]** `src/pages/dashboard/CrimeMapPage.tsx`:
    *   Eliminar la dependencia de los datos falsos en `mockData.ts`.
    *   Implementar llamadas al endpoint `POST /predict/predecir` enviando `fecha_consulta` y `distrito`.

### FASE 3: Evolución Cartográfica (Leaflet + CartoDB Dark Matter)
*   **[NEW]** Instalar librerías 100% open-source y gratuitas: `leaflet` y `react-leaflet`.
*   **[MODIFY]** Reemplazar los `<div>` simulados de `CrimeMapPage` por un lienzo interactivo de Leaflet.
*   **[NEW]** Utilizar el proveedor de mapas `CartoDB Dark Matter` para mantener una estética oscura y moderna, ideal para superponer puntos de calor y polígonos de riesgo sin necesidad de registrar tarjetas de crédito ni tokens de pago.
*   **[NEW]** Pintar los polígonos de Lima y renderizar marcadores térmicos (*hotspots*) basados en las coordenadas físicas reales.

---

## 4. Gestión de Dependencias en Entornos Dockerizados

Para garantizar que los contenedores de Docker (tanto del frontend como del backend) no se rompan y reconozcan las nuevas herramientas instaladas (como `axios` o `mapbox-gl`), es obligatorio seguir estas reglas arquitectónicas:

### Frontend (React / Vite)
Cualquier nueva librería debe quedar registrada en los archivos `package.json` y `package-lock.json`. 
*   **Procedimiento:** Al ejecutar `npm install <paquete>` localmente, estos archivos se actualizan automáticamente. El `Dockerfile` del frontend ejecuta `npm install` internamente basándose en estos archivos.

### Backend (FastAPI / Python)
Cualquier nueva librería debe registrarse en `requirements.txt`.
*   **Procedimiento:** Al ejecutar `pip install <paquete>` localmente, Docker no se entera. Es obligatorio hacer un `pip freeze > requirements.txt` (o añadirlo manualmente al `.txt`). El `Dockerfile` del backend leerá este archivo.

### > [!IMPORTANT] Regla de Oro (Re-build)
Siempre que se instale una librería nueva y los archivos de registro (`package.json` o `requirements.txt`) cambien, **se debe reconstruir la imagen del contenedor**. De lo contrario, el código nuevo fallará al intentar importar una librería que el contenedor no tiene instalada.

Comando de reconstrucción obligatoria:
```bash
docker-compose up --build
```
