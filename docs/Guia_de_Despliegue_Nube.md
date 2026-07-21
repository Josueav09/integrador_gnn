# Guía de Despliegue en la Nube y Configuración de Recursos

Esta guía explica detalladamente y de forma sencilla cómo desplegar el **Sistema Predictivo Delictivo PNP (ST-GNN)** en la nube (utilizando **Render.com** u otra plataforma de contenedores similar) y cómo configurar los recursos de hardware y variables de entorno necesarios para su correcto funcionamiento.

---

## 1. El Secreto para PyTorch: Configuración de Recursos (RAM y CPU)

### ¿Por qué es necesario este paso?
El backend utiliza **PyTorch** y **torch_geometric** para ejecutar la Red Neuronal de Grafos (GNN). Estos frameworks de Inteligencia Artificial necesitan cargar en la memoria RAM del servidor el modelo completo de grafos de Lima y los pesos preentrenados del archivo `pesos_stgnn_pnp.pth` al iniciar.
* **Si usas 512 MiB (el límite gratuito estándar de Render):** El servidor se quedará sin memoria durante el arranque (Out of Memory - OOM) y se apagará o reiniciará en bucle de forma silenciosa.
* **La Solución:** Asignar un mínimo de **2 GiB** (lo ideal y recomendado son **4 GiB**) para dar suficiente holgura al cargador de PyTorch en CPU.

### Paso a Paso para configurar los recursos en Render:
1. Inicia sesión en tu cuenta de [Render](https://dashboard.render.com).
2. Crea tu servicio web (`Web Service`) conectado a tu repositorio Git del proyecto.
3. En el formulario de creación (o una vez creado, en la pestaña **Settings** / Configuración de tu servicio):
4. Desplázate hacia abajo hasta encontrar la sección colapsable llamada **"Advanced"** (Configuración Avanzada) o **"Configuración de contenedores, volúmenes, conexiones y seguridad"**. Haz clic para desplegarla.
5. Ve a la pestaña o sección de **Contenedor / Instancia (Instance Type)**.
6. Configura los siguientes parámetros exactos:
   * **Memoria Asignada (Memory):** Cámbiala a **2 GiB** o **4 GiB** (según el plan seleccionado, por ejemplo, el plan *Starter* que cuenta con 2 GiB de RAM o *Basic* con 4 GiB).
   * **CPU:** Déjalo seleccionado en **1 CPU** (1 núcleo es más que suficiente para realizar la inferencia espaciotemporal en milisegundos).

---

## 2. Inyectar las 4 Variables de Entorno

### ¿Por qué es necesario este paso?
Para que el servidor en la nube pueda guardar los datos de criminalidad y verificar los tokens JWT seguros de los analistas policiales, debe conocer la ubicación de la base de datos Supabase y la firma secreta. Esta información sensible no debe subirse al Git público, por lo que se inyecta directamente en la nube.

### Paso a Paso para registrar tus variables en Render:
1. En la misma sección desplegable de tu servicio web en Render, busca la pestaña o menú lateral llamada **"Environment"** (Variables de Entorno).
2. Haz clic en el botón **"Add Environment Variable"** (Agregar Variable).
3. Deberás registrar un total de **4 llaves** copiando el nombre y valor exactamente como figuran en tu archivo local `.env`:

| Key (Llave) | Valor a copiar | Descripción técnica |
| :--- | :--- | :--- |
| **`DATABASE_URL`** | `postgresql://postgres.zoehmypmvvqludsakifg:...` | Dirección de conexión directa de tu Base de Datos en Supabase (con PostGIS activo). |
| **`SECRET_KEY`** | `pnppredictivo_secreto_super_seguro_2026` | Clave secreta con la que FastAPI encriptará y validará los tokens de acceso JWT. |
| **`EMAIL_USER`** | `josueabrahm.av@gmail.com` | Dirección de correo electrónico utilizada para despachar los códigos de recuperación. |
| **`EMAIL_PASSWORD`** | `mrpdawkzzytdifzh` | Contraseña de aplicación (App Password) generada en Gmail para permitir el envío SMTP. |

4. Una vez agregadas las 4 variables, haz clic en el botón verde **"Save Changes"** (Guardar Cambios) al final de la página.
5. Render iniciará automáticamente un nuevo despliegue (*redeploy*) inyectando estos datos en el contenedor seguro.

¡Listo! Con estas configuraciones, tu backend de Inteligencia Artificial se levantará con total estabilidad y seguridad en la nube.

---

## 3. Despliegue en Producción

Antes de publicar el servicio, verifica estos puntos:

1. `TEST_MODE=0` en la nube para desactivar el modo laboratorio.
2. No usar `--reload` ni volúmenes de código montado en producción.
3. Confirmar que los artefactos ML obligatorios estén dentro de la imagen.
4. Ejecutar las migraciones antes de poner el servicio en línea.

### Comando recomendado con Docker Compose de producción

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Validación posterior al despliegue

```bash
curl http://localhost:8000/
curl http://localhost:8000/monitoring/status
```

Si la respuesta raíz devuelve `status: ok` y el monitoreo devuelve `status: ok`, el backend quedó operativo.
