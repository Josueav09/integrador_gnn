import bcrypt

class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        """
        Toma una contraseña en texto plano, le genera una 'sal' aleatoria
        y devuelve un hash indescifrable (estándar nativo).
        """
        # Bcrypt requiere que el string sea convertido a bytes antes de encriptar
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)
        
        # Devolvemos el hash como un string normal (utf-8) para guardarlo en Supabase
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        """
        Compara el intento de login con el hash de la base de datos.
        """
        # Convertimos ambos a bytes para la comparación matemática
        password_byte_enc = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(password_byte_enc, hashed_password_bytes)