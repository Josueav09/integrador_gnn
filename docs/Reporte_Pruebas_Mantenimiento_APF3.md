# Reporte de Pruebas de Mantenimiento APF3

## 19. Pruebas de Mantenimiento

### a. Escenario del cambio realizado

Se realizó un mantenimiento preventivo y perfectivo sobre la capa de observabilidad y resiliencia del backend FastAPI del sistema predictivo de delitos.

El cambio tuvo dos objetivos concretos:

1. Formalizar una ruta de mantenimiento controlado para pruebas de resiliencia, evitando el comportamiento destructivo del antiguo prototipo de ingeniería del caos.
2. Integrar esa ruta al enrutador principal del backend para que la prueba sea ejecutable, trazable y reutilizable en laboratorio.

La implementación se apoyó en dos componentes ya existentes del sistema:

- El endpoint de monitoreo en tiempo real, que expone estado de base de datos, modelo GNN, seguridad y recursos del servidor.
- El script de monitoreo operativo, que consume ese endpoint y genera trazas de evidencia en archivo.

### Tipo de mantenimiento

Se clasifica como:

- Preventivo, porque mejora la capacidad de detección temprana del estado del sistema.
- Perfectivo, porque convierte un archivo aislado en un componente reutilizable y registrable dentro de la API.

### b. Casos de prueba ejecutados (antes y después)

#### Antes del cambio

- La ruta de caos existía solo como código aislado y no estaba registrada en `main.py`.
- No había una prueba automática que validara su comportamiento.
- El prototipo anterior intentaba terminar el proceso con una llamada destructiva, lo cual no era apto para ejecución repetida ni para evidencia académica.

Casos evaluados antes del cambio:

- `POST /admin/chaos/crash` no disponible como ruta integrada.
- No existía verificación automática de bloqueo fuera de laboratorio.
- No existía simulación segura para laboratorio.

#### Después del cambio

- `POST /admin/chaos/crash` queda registrado como ruta real del backend.
- Fuera de `TEST_MODE`, la ruta devuelve `403 Forbidden`.
- En `TEST_MODE`, la ruta devuelve una simulación controlada sin detener el servidor.
- Se agregaron pruebas automáticas para validar ambos estados.

Casos ejecutados después del cambio:

- Bloqueo de la ruta fuera de laboratorio.
- Simulación controlada dentro de laboratorio.
- Monitoreo del sistema mediante `/monitoring/status`.
- Validación de robustez de seguridad con rate limiting y filtros de entrada.

### c. Evidencias de ejecución

Las evidencias técnicas que respaldan el cambio son:

- Registro de la ruta en `src/api/main.py`.
- Implementación del componente en `src/api/routes/chaos.py`.
- Pruebas automatizadas en `tests/test_chaos_endpoint.py`.
- Endpoint de monitoreo en `src/api/routes/monitoring.py`.
- Script de evidencia operativa en `scripts/monitor_system.py`.
- Pruebas de robustez en `tests/test_security_robustness.py`.

Evidencias que deben adjuntarse en la sustentación:

- Captura de la respuesta HTTP `403` cuando `TEST_MODE=0`.
- Captura de la respuesta HTTP `200` con simulación cuando `TEST_MODE=1`.
- Captura o log generado por `python scripts/monitor_system.py`.
- Captura del reporte automático en `logs/monitoreo_reporte.txt`.
- Captura de la ejecución de `pytest tests/test_chaos_endpoint.py -v`.

### d. Impacto del cambio en el sistema

El impacto del cambio fue positivo y acotado:

- No altera la lógica predictiva del modelo GNN.
- Mejora la modularidad porque la prueba de mantenimiento ahora es un router reutilizable.
- Aumenta la trazabilidad porque el comportamiento queda documentado por logs y tests.
- Reduce el riesgo operacional porque el entorno de producción no ejecuta una terminación real del proceso.
- Facilita la evaluación según ISO 25010 en la dimensión de mantenibilidad, especialmente analizabilidad, modificabilidad y reutilización.

### e. Estado final y conclusiones

Estado final:

- La API incorpora una ruta de mantenimiento controlado.
- El monitoreo de salud y recursos ya forma parte del backend.
- Existen pruebas automáticas para validar el comportamiento esperado.
- El sistema mantiene estabilidad funcional y queda mejor preparado para auditorías de mantenimiento.

Conclusión técnica:

El cambio demuestra que el sistema no solo funciona, sino que puede ser monitoreado, probado y modificado de manera segura sin comprometer su operación principal. Esto fortalece la capacidad de mantenimiento exigida por la evaluación y aporta evidencia verificable de modularidad y reutilización.

## Evaluación del monitoreo y mantenimiento según ISO 25010

### 1) Monitoreo de recursos

El endpoint `GET /monitoring/status` reporta uso de CPU, memoria RSS, latencia de base de datos, estado del modelo GNN y cantidad de IPs bloqueadas por rate limiting. Si `psutil` está disponible, el reporte incluye métricas reales del proceso.

### 2) Reportes y capturas de monitoreo

El script `scripts/monitor_system.py` consume el endpoint de monitoreo y genera una traza persistente en `logs/monitoreo_reporte.txt`. Ese archivo funciona como evidencia reproducible para revisión del docente.

### 3) Perfilamiento de código

Para evidenciar perfilamiento en sustentación se recomienda ejecutar:

```bash
python -m cProfile -o logs/perfilamiento_monitoring.prof scripts/monitor_system.py
```

Con ello se obtiene un archivo de perfil que permite analizar tiempos de ejecución y detectar cuellos de botella en la rutina de monitoreo.

### 4) Observaciones y conclusiones de monitoreo

- La salud del sistema depende de la conexión a base de datos y de la carga correcta del modelo GNN.
- El endpoint de monitoreo permite verificar rápidamente si el backend está operativo o degradado.
- El rate limiting en memoria es útil para laboratorio, pero para escalamiento horizontal se recomienda Redis o un gateway externo.

### 5) Escenario del cambio realizado

Se reemplazó un prototipo destructivo por una simulación controlada, registrable y testeable. Este enfoque es más adecuado para un entorno académico y para pruebas repetibles en producción controlada.

### 6) Casos de prueba ejecutados (antes y después)

- Antes: no existía validación automática de la ruta de caos y el prototipo era no seguro para automatización.
- Después: la ruta responde según el modo de ejecución y cuenta con pruebas de aceptación.

### 7) Impacto del cambio en el sistema

- Mayor seguridad operacional.
- Menor riesgo de indisponibilidad accidental.
- Mejor mantenibilidad y reutilización del componente.
- Evidencia más sólida para la sustentación académica.

### 8) Estado final y conclusiones

El sistema termina con una base más robusta para mantenimiento continuo. El monitoreo ya no es una idea conceptual sino una capacidad real y verificable dentro de la API.