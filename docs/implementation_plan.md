# Plan de Implementación Unificado: Ajustes de Código, Auditoría y APF2 (Actualizado)

Este documento detalla el plan de acción técnico unificado para modificar el código fuente de la aplicación, abordando tanto los requerimientos de la rúbrica del **Avance de Proyecto Final 2 (APF2)** como las mejoras de rendimiento, desacoplamiento y rigor matemático señaladas en la **Auditoría Académica**, incorporando la retroalimentación de diseño.

---

## 1. Cambios Propuestos por Componente

### Componente 1: Base de Datos y Repositorios (APF2 - Ítems 1 y 3)

#### [MODIFY] [models.py](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/src/core/models.py)
*   **Acción:** Reemplazar el archivo para mapear las 12 tablas físicas de Supabase en SQLAlchemy.
*   **Integración GIS:** Importar e implementar `Geometry` de `geoalchemy2` para las columnas espaciales `geometria_distrito`, `centroide`, `geometria_poligono` y `ubicacion_exacta`.
*   **Relaciones:** Configurar los mapeos `relationship()` y llaves foráneas (`ForeignKey`) correspondientes.

#### [MODIFY] [crime_repo.py](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/src/repository/crime_repo.py)
*   **Acción:** Refactorizar el repositorio para que trabaje sobre la entidad ORM `Delito` en lugar de ejecutar una consulta SQL cruda, logrando consistencia con el patrón Repository.

---

### Componente 2: Modelo e Inferencia GNN (Auditoría - Ítems 2.1 y 2.2)

#### [MODIFY] [st_gnn.py](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/src/model/st_gnn.py)
*   **Optimización CUDA Acotada:** Refactorizar el método `forward()` para eliminar el bucle secuencial espacial `for b in range(batch_size)`. La paralelización se aplicará únicamente sobre la dimensión espacial (el lote de grafos) empaquetando el batch en un grafo disjunto nativo con `torch_geometric.data.Batch`. La dimensión temporal ($T=14$) conservará su procesamiento secuencial/recurrente iterativo para que la GRU capture correctamente las dinámicas temporales.
*   **Activación Softplus:** Sustituir la capa de salida lineal o el parche `np.maximum` por la función de activación `nn.Softplus()`. Esto garantiza matemáticamente salidas no negativas ($\ge 0$), previniendo el problema de la "ReLU muerta" en los cuadrantes de baja o nula tasa delictiva diaria y manteniendo estables los gradientes durante el entrenamiento.

---

### Componente 3: Desacoplamiento de API e Inferencia (Auditoría - Ítem 3.1)

#### [MODIFY] [predict.py](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/src/api/routes/predict.py)
*   **Acción:** Modificar el esquema Pydantic `ConsultaPredictiva` para recibir parámetros de negocio:
    ```python
    class ConsultaPredictiva(BaseModel):
        fecha_consulta: str # 'YYYY-MM-DD'
        distrito: str       # Ubicación para el filtrado
    ```
    Esto evita que el frontend tenga que estructurar y enviar el tensor de características `[14, 400, 5]`.

#### [MODIFY] [gnn_service.py](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/src/services/gnn_service.py)
*   **Ingeniería de Características en el Servidor:** Implementar la lógica que:
    1. Consulte los delitos de los últimos 14 días en Supabase a través del `CrimeRepository`.
    2. Construye dinámicamente el tensor espaciotemporal de entrada `[14, 400, 5]` calculando las variables sinusoidales temporales (`sin_tiempo`, `cos_tiempo`), feriados y días de la semana de forma interna.
*   **Estrategia Anti-Cuello de Botella (Buffer/Caché):** Implementar un búfer asíncrono en memoria RAM para almacenar los datos consolidados de delitos de los últimos 14 días. Al ingresar la petición, la API solo inyectará las características dinámicas del día en curso (sinusoides de tiempo, feriados) sobre el tensor pre-estructurado, ejecutando la inferencia en fracciones de milisegundo y garantizando el SLA de $< 500$ ms.

---

### Componente 4: Pruebas y Validación (APF2 - Ítem 8)

#### [NEW] [verify_system.py](file:///c:/Users/JOSUE/Downloads/CICLO%209/Integrador_de_software/Entrenamiento_GNN/Predicciones_GNN/verify_system.py)
*   **Acción:** Crear un script de pruebas locales utilizando `fastapi.testclient.TestClient` para certificar:
    *   Flujo de registro y login de usuarios policiales.
    *   Activación del bloqueo por IP de fuerza bruta (Rate Limiting) tras 5 fallos.
    *   **Verificación Forense:** Incluir un bloque de aserciones que valide físicamente que, tras forzar el rate limiting con 5 intentos erróneos, el archivo `logs/auditoria_pnp.log` contenga una traza formal con nivel `CRITICAL`.
    *   Inferencia exitosa de la GNN utilizando el nuevo esquema desacoplado.

---

## 2. Encuadre Teórico y Trabajos Futuros (Sustentación de Tesis)

*   **Encuadre de Tesis:** Definir oficialmente la investigación en el informe escrito como un *"Framework Metodológico de Simulación en Entornos de Escasez de Datos"* (Simulation Framework in Data-Sparse Environments). Esto justifica académicamente la desagregación temporal y espacial de datos delictivos debido al secreto estadístico y confidencialidad policial, convirtiendo la escasez de microdatos reales en una propuesta metodológica defendible.
*   **Trabajos Futuros:** Incluir en el informe escrito la propuesta de migrar el Rate Limiter en memoria RAM local hacia una arquitectura distribuida basada en **Redis** para entornos cloud de producción a gran escala.

---

## 3. Plan de Verificación

*   Correr `verify_system.py` localmente y verificar que los códigos de respuesta y aserciones de logs se ejecuten exitosamente.
