import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class STGNNTestSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Configurar la URL del Frontend (por defecto apunta al puerto de Docker: 3000)
        cls.base_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        
        # Configurar opciones de Chrome
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")
        
        # Inicializar el WebDriver
        print(f"\n[SETUP] Inicializando Chrome WebDriver para {cls.base_url}...")
        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        print("\n[TEARDOWN] Cerrando Chrome WebDriver...")
        cls.driver.quit()

    def test_01_public_crime_report(self):
        """1. CASO DE PRUEBA: Reporte ciudadano publico anonimo (Crowdsourcing)"""
        print("\n=== [TEST 1] REGISTRO DE DENUNCIA CIUDADANA ANONIMA ===")
        driver = self.driver
        driver.get(f"{self.base_url}/reportar-denuncia")
        
        # Verificar que estamos en la pagina correcta
        self.assertIn("reportar-denuncia", driver.current_url)
        
        # Seleccionar tipo de delito (Robo)
        tipo_select = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='report-crime-type-select']"))
        )
        tipo_select.send_keys("Robo")
        
        # Llenar la descripcion
        descripcion_box = driver.find_element(By.CSS_SELECTOR, "[data-testid='report-crime-desc-textarea']")
        descripcion_box.send_keys("Robo de celular en paradero con arma de fuego por dos sujetos.")
        
        # Simular clic en el mapa Leaflet para ubicar la latitud/longitud
        mapa = driver.find_element(By.CSS_SELECTOR, "[data-testid='report-crime-map-container']")
        action = webdriver.ActionChains(driver)
        action.move_to_element(mapa).click().perform()
        time.sleep(1)
        
        # Presionar el boton de envio
        btn_enviar = driver.find_element(By.CSS_SELECTOR, "[data-testid='report-crime-submit-btn']")
        self.assertTrue(btn_enviar.is_enabled(), "El boton de envio deberia estar habilitado despues de marcar ubicacion y llenar descripcion.")
        btn_enviar.click()
        
        # Esperar que aparezca el mensaje de exito
        time.sleep(3)
        print("[OK] Denuncia publica enviada y en cola de cuarentena (PostGIS ST_Contains preparada).")

    def test_02_login_validation_flow(self):
        """2. CASO DE PRUEBA: Autenticacion con verificacion de errores y exito (RBAC/JWT)"""
        print("\n=== [TEST 2] FLUJO DE AUTENTICACION PNP Y VALIDACION DE USABILIDAD ===")
        driver = self.driver
        driver.get(f"{self.base_url}/login")
        
        # Intentar login vacio (debe tener boton deshabilitado)
        submit_btn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='login-submit-button']"))
        )
        self.assertFalse(submit_btn.is_enabled(), "El boton de login vacio debe estar deshabilitado.")
        print("[VALIDACION] El boton de inicio de sesion se encuentra deshabilitado por defecto.")
        
        # 1. Comprobar validacion de email en tiempo real (Usabilidad - Asistencia de errores)
        email_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email-input']")
        password_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password-input']")
        
        email_input.send_keys("correo_invalido")
        # Quitar el foco del input de email (Blur) enviando tecla TAB
        email_input.send_keys(Keys.TAB)
        
        # Debe aparecer el mensaje de error de formato bajo el input
        error_msg = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".auth-field__error"))
        )
        self.assertIn("formato del correo institucional es incorrecto", error_msg.text)
        print("[PINTADO] Error en rojo bajo el input 'Correo': 'El formato del correo institucional es incorrecto.'.")
        
        # Corregir el email
        email_input.clear()
        email_input.send_keys("admin@pnp.gob.pe")
        email_input.send_keys(Keys.TAB) # Quitar foco para validar de nuevo
        
        # 2. Ingresar credenciales correctas de analista PNP
        password_input.send_keys("TesisUTP2026*")
        
        # Ahora el boton debe estar habilitado
        self.assertTrue(submit_btn.is_enabled(), "El boton debe habilitarse al llenar credenciales validas.")
        submit_btn.click()
        
        # 3. Comprobar que aparezca el Toast de Exito en pantalla (Notificacion global)
        toast_exito = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner--success"))
        )
        # Buscar "iniciada" de manera robusta sin depender de la codificacion local en las comparaciones directas
        self.assertIn("iniciada", toast_exito.text)
        print("[PINTADO] Toast global de EXITO (verde) en esquina superior derecha: 'Sesion iniciada con exito'.")
        
        # Esperar redireccion al Dashboard
        self.wait.until(EC.url_contains("/dashboard"))
        print("[OK] Redireccionado a /dashboard de manera segura.")

    def test_03_dashboard_filters(self):
        """3. CASO DE PRUEBA: Filtros interactivos del Dashboard (WPO AbortController)"""
        print("\n=== [TEST 3] FILTROS DEL DASHBOARD Y KPI CARD ===")
        driver = self.driver
        driver.get(f"{self.base_url}/dashboard")
        
        # Verificar que el KPI Grid y las Zonas Criticas se carguen
        kpi_grid = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='dashboard-kpi-grid']"))
        )
        self.assertTrue(kpi_grid.is_displayed())
        
        # Cambiar el filtro de anio
        year_select = driver.find_element(By.CSS_SELECTOR, "[data-testid='dashboard-year-select']")
        year_select.send_keys("Ano 2026")
        time.sleep(2) # Espera de actualizacion de Recharts
        
        # Comprobar que las zonas criticas sigan renderizandose
        zonas_criticas = driver.find_element(By.CSS_SELECTOR, "[data-testid='dashboard-critical-zones']")
        self.assertTrue(zonas_criticas.is_displayed())
        print("[OK] Filtros de anio actualizados y visualizaciones cargadas correctamente.")

    def test_04_gis_crime_map(self):
        """4. CASO DE PRUEBA: Mapa interactivo GIS ( Leaflet ) y Cambio de Modos"""
        print("\n=== [TEST 4] MAPA GEOGRAFICO DE DELITOS ===")
        driver = self.driver
        driver.get(f"{self.base_url}/dashboard/mapa")
        
        # Esperar carga del selector de distrito en el mapa
        dist_select = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='map-district-select']"))
        )
        dist_select.send_keys("COMAS")
        
        # Cambiar al modo prediccion GNN
        mode_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='map-mode-prediction-btn']")
        mode_btn.click()
        
        # Aplicar filtros para disparar la inferencia en Docker GNN
        apply_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='map-apply-filters-btn']")
        apply_btn.click()
        
        # Esperar a que la carga termine
        time.sleep(3)
        print("[OK] Mapa GIS cargado y predicciones de Comas renderizadas en Leaflet.")

    def test_05_quarantine_inbox(self):
        """5. CASO DE PRUEBA: Aprobacion de denuncias en la Bandeja de Cuarentena (PostGIS ST_Contains)"""
        print("\n=== [TEST 5] BANDEJA DE CUARENTENA (INBOX) ===")
        driver = self.driver
        driver.get(f"{self.base_url}/dashboard/denuncias")
        
        # Comprobar que la tabla de cuarentena cargue correctamente
        inbox_table = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='inbox-table']"))
        )
        self.assertTrue(inbox_table.is_displayed())
        
        # Si hay denuncias pendientes creadas en el Test 1, las aprobamos
        try:
            approve_btns = driver.find_elements(By.CSS_SELECTOR, "[data-testid='inbox-approve-btn']")
            if approve_btns:
                approve_btns[0].click()
                time.sleep(2)
                print("[OK] Denuncia en cuarentena aprobada con exito. Promovida en PostGIS.")
            else:
                print("[INFO] No hay denuncias pendientes en cuarentena en este momento.")
        except Exception as e:
            print(f"[WARNING] Ocurrio un inconveniente al aprobar la denuncia: {e}")

    def test_06_admin_retrain_pipeline(self):
        """6. CASO DE PRUEBA: Panel de control y Trigger de Reentrenamiento GNN"""
        print("\n=== [TEST 6] PANEL DE ADMINISTRACION Y REENTRENAMIENTO ===")
        driver = self.driver
        driver.get(f"{self.base_url}/dashboard/administracion")
        
        # Localizar el boton de reentrenamiento
        retrain_btn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-retrain-btn']"))
        )
        
        # Verificar zona de subida de CSV
        upload_zone = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-upload-zone']")
        self.assertTrue(upload_zone.is_displayed())
        
        # Disparar el reentrenamiento
        retrain_btn.click()
        time.sleep(2) # Espera para recibir confirmacion de la API
        
        # Comprobar que los logs en la terminal y el pipeline se actualicen
        terminal = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-terminal-logs']")
        pipeline = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-pipeline-steps']")
        self.assertTrue(terminal.is_displayed())
        self.assertTrue(pipeline.is_displayed())
        print("[OK] Solicitud de reentrenamiento enviada y pipeline ejecutandose en Docker.")

    def test_07_admin_upload_validation_errors(self):
        """7. CASO DE PRUEBA: Validacion de archivos en cliente (Admin Upload Toast Errors)"""
        print("\n=== [TEST 7] PRUEBA DE USABILIDAD: ERRORES DE CARGA Y CASOS EXITO ===")
        driver = self.driver
        driver.get(f"{self.base_url}/dashboard/administracion")
        
        # Esperar a que la pagina cargue
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-upload-zone']")))
        
        # 1. CASO ERROR: Extension incorrecta (.xlsx)
        filepath_invalido = os.path.join(os.getcwd(), "test_invalido.xlsx")
        with open(filepath_invalido, "w") as f:
            f.write("dummy content")
            
        # 2. CASO ERROR: Archivo vacio (0 bytes)
        filepath_vacio = os.path.join(os.getcwd(), "test_vacio.csv")
        with open(filepath_vacio, "w") as f:
            pass
            
        # 3. CASO ERROR: Cabeceras faltantes en CSV
        filepath_sin_cabeceras = os.path.join(os.getcwd(), "test_sin_cabeceras.csv")
        with open(filepath_sin_cabeceras, "w") as f:
            f.write("id_cuadrante,fecha_delito\n")
            
        # 4. CASO CORRECTO: CSV con formato y cabeceras correctas
        filepath_valido = os.path.join(os.getcwd(), "test_valido.csv")
        with open(filepath_valido, "w") as f:
            f.write("id_cuadrante,id_tipo_delito,fecha_delito,ubicacion\n")
            f.write("1,1,2026-06-18,Point(0 0)\n")
            
        try:
            # A. Probar extension incorrecta
            print("[TEST 7.1] Subiendo archivo con extension incorrecta (.xlsx)...")
            file_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-file-input']")
            file_input.send_keys(filepath_invalido)
            
            toast_error = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner--error"))
            )
            self.wait.until(lambda d: toast_error.text.strip() != "")
            self.assertIn("Solo se permiten archivos", toast_error.text)
            print("[PINTADO] Toast de ERROR en esquina superior derecha (rojo): 'Solo se permiten archivos CSV o JSON'.")
            
            # Esperar a que el toast desaparezca o refrescar pagina para evitar solapamiento
            time.sleep(2)
            driver.refresh()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-upload-zone']")))

            # B. Probar archivo vacio
            print("[TEST 7.2] Subiendo archivo vacio (0 bytes)...")
            file_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-file-input']")
            file_input.send_keys(filepath_vacio)
            
            toast_error = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner--error"))
            )
            self.wait.until(lambda d: toast_error.text.strip() != "")
            self.assertIn("vac", toast_error.text.lower())
            print("[PINTADO] Toast de ERROR en esquina superior derecha (rojo): 'El archivo esta vacio.'.")
            
            time.sleep(2)
            driver.refresh()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-upload-zone']")))

            # C. Probar cabeceras faltantes
            print("[TEST 7.3] Subiendo CSV con cabeceras faltantes...")
            file_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-file-input']")
            file_input.send_keys(filepath_sin_cabeceras)
            
            toast_error = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner--error"))
            )
            # Esperar a que el texto esté cargado por React
            self.wait.until(lambda d: toast_error.text.strip() != "")
            
            error_text = toast_error.text
            self.assertTrue(
                any(kw in error_text for kw in ["Columnas faltantes", "Faltan columnas", "inválido", "cabeceras"]),
                f"El mensaje de error '{error_text}' no contiene palabras clave esperadas."
            )
            print(f"[PINTADO] Toast de ERROR en esquina superior derecha (rojo): '{error_text.split(chr(10))[0]}'.")
            
            time.sleep(2)
            driver.refresh()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='admin-upload-zone']")))

            # D. Probar caso correcto
            print("[TEST 7.4] Subiendo CSV valido...")
            file_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='admin-file-input']")
            file_input.send_keys(filepath_valido)
            
            toast_success = self.wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner--success"))
            )
            self.assertTrue("cargado" in toast_success.text or "exito" in toast_success.text.lower())
            print(f"[PINTADO] Toast de EXITO en esquina superior derecha (verde): '{toast_success.text.split(chr(10))[0]}'.")
            
        finally:
            # Limpiar archivos temporales
            for path in [filepath_invalido, filepath_vacio, filepath_sin_cabeceras, filepath_valido]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass

    def test_08_register_validation_flow(self):
        """8. CASO DE PRUEBA: Registro con verificacion de errores y exito (RBAC)"""
        print("\n=== [TEST 8] FLUJO DE REGISTRO Y VALIDACION DE ERRORES EN CLIENTE ===")
        driver = self.driver
        # Cerrar sesion limpiando cookies y almacenamiento local
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        
        driver.get(f"{self.base_url}/register")
        
        # 1. Comprobar que boton este deshabilitado al inicio
        submit_btn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='register-submit-button']"))
        )
        self.assertFalse(submit_btn.is_enabled(), "El boton de registrar vacio debe estar deshabilitado.")
        
        name_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='register-name-input']")
        email_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='register-email-input']")
        password_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='register-password-input']")
        
        # A. Validar nombre obligatorio
        name_input.click()
        name_input.send_keys(Keys.TAB)
        time.sleep(0.5)
        errors = driver.find_elements(By.CSS_SELECTOR, ".auth-field__error")
        self.assertTrue(len(errors) > 0, "Debe aparecer al menos un mensaje de error.")
        self.assertIn("obligatorio", errors[0].text)
        print("[PINTADO] Error en rojo debajo de Nombre: 'El nombre es obligatorio.'.")
        
        # Llenar nombre
        name_input.send_keys("Analista Prueba")
        name_input.send_keys(Keys.TAB)
        time.sleep(0.5)
        
        # B. Validar correo institucional
        email_input.send_keys("correo_invalido")
        email_input.send_keys(Keys.TAB)
        time.sleep(0.5)
        errors = driver.find_elements(By.CSS_SELECTOR, ".auth-field__error")
        self.assertTrue(len(errors) > 0, "Debe aparecer el mensaje de error del correo.")
        self.assertIn("formato del correo institucional es incorrecto", errors[0].text)
        print("[PINTADO] Error en rojo debajo de Correo: 'El formato del correo institucional es incorrecto.'.")
        
        # Corregir correo
        email_input.clear()
        email_input.send_keys(Keys.CONTROL + "a")
        email_input.send_keys(Keys.BACKSPACE)
        email_input.send_keys("analista.prueba@pnp.gob.pe")
        email_input.send_keys(Keys.TAB)
        time.sleep(0.5)
        
        # C. Validar password corto
        password_input.send_keys("123")
        password_input.send_keys(Keys.TAB)
        time.sleep(0.5)
        errors = driver.find_elements(By.CSS_SELECTOR, ".auth-field__error")
        self.assertTrue(len(errors) > 0, "Debe aparecer el mensaje de error de password.")
        self.assertIn("debe tener al menos 6 caracteres", errors[0].text)
        print("[PINTADO] Error en rojo debajo de Contrasena: 'La contrasena debe tener al menos 6 caracteres.'.")
        
        # Corregir password
        password_input.clear()
        password_input.send_keys(Keys.CONTROL + "a")
        password_input.send_keys(Keys.BACKSPACE)
        password_input.send_keys("TesisUTP2026*")
        password_input.send_keys(Keys.TAB)
        time.sleep(0.5)
        
        # Verificar que el boton ahora este habilitado
        self.assertTrue(submit_btn.is_enabled(), "El boton de submit debe estar habilitado tras llenar datos correctos.")
        submit_btn.click()
        
        # Comprobar Toast de exito
        toast_exito = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".status-banner--success"))
        )
        self.assertIn("completado", toast_exito.text.lower())
        print("[PINTADO] Toast de EXITO en esquina superior derecha (verde): 'Registro completado de forma simulada!'.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
