import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.logger import logger
import os
from src.core.config import settings

# Para efectos académicos, puedes utilizar un correo real de Gmail si configuras
# una "App Password" (Contraseña de aplicación) en tu cuenta de Google.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Leer de settings (que ya cargó el .env)
SENDER_EMAIL = settings.EMAIL_USER
SENDER_PASSWORD = settings.EMAIL_PASSWORD

def enviar_bienvenida(destinatario: str, password_temporal: str):
    """
    Despacha un correo de bienvenida a un nuevo oficial de la PNP.
    Esta función bloquea el hilo, por lo que DEBE llamarse a través de BackgroundTasks.
    """
    if SENDER_EMAIL == "tu_correo@gmail.com":
        logger.warning(f"[SIMULACIÓN SMTP] Se enviaría correo a {destinatario} con pass: {password_temporal}")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = "Bienvenido al Sistema Predictivo GNN - PNP"

        cuerpo = f"""
        <html>
        <body>
            <h2>Bienvenido a la Inteligencia Espaciotemporal PNP</h2>
            <p>Se ha creado una cuenta oficial para usted.</p>
            <p><b>Usuario:</b> {destinatario}</p>
            <p><b>Contraseña Temporal:</b> {password_temporal}</p>
            <br>
            <p>Por seguridad, le recomendamos cambiar su contraseña tras el primer inicio de sesión.</p>
            <p><i>- Administrador del Sistema GNN</i></p>
        </body>
        </html>
        """
        msg.attach(MIMEText(cuerpo, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Correo de bienvenida enviado exitosamente a {destinatario}")
    except Exception as e:
        logger.error(f"Fallo al enviar correo SMTP a {destinatario}: {str(e)}")

def enviar_pin_recuperacion(destinatario: str, pin: str):
    """
    Despacha un PIN de 6 dígitos para recuperación de contraseña.
    """
    if SENDER_EMAIL == "tu_correo@gmail.com":
        logger.warning(f"[SIMULACIÓN SMTP] Se enviaría PIN {pin} a {destinatario} para recuperación.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = "PIN de Recuperación - Sistema GNN"

        cuerpo = f"""
        <html>
        <body>
            <h2>Recuperación de Acceso</h2>
            <p>Hemos recibido una solicitud para restablecer su contraseña.</p>
            <p>Su código seguro de recuperación es:</p>
            <h1 style="color: #2563eb; letter-spacing: 5px;">{pin}</h1>
            <p>Este código expirará en 15 minutos.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(cuerpo, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"PIN de recuperación enviado a {destinatario}")
    except Exception as e:
        logger.error(f"Fallo al enviar PIN SMTP a {destinatario}: {str(e)}")
