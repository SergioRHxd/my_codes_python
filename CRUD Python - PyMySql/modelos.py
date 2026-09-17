class Usuario:
    """Clase que representa la entidad Usuario."""
    
    def __init__(self, idusuario=None, nombres="", apellido_paterno="", apellido_materno="", user="", pwd=""):
        self.idusuario = idusuario
        self.nombres = nombres
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.user = user
        self.pwd = pwd

    def __str__(self):
        """Permite imprimir los datos del usuario de forma entendible."""
        return f"ID: {self.idusuario} | Nombre: {self.nombres} {self.apellido_paterno} | User: {self.user}"

