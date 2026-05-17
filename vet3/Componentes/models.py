from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('veterinario', 'Veterinario'),
        ('recepcionista', 'Recepcionista'),
    ]

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=50, blank=True, default='')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='recepcionista')
    telefono = models.CharField(max_length=15, blank=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    @property
    def es_veterinario(self):
        return self.rol == 'veterinario'

    @property
    def es_recepcionista(self):
        return self.rol == 'recepcionista'

    @property
    def es_admin(self):
        return self.rol == 'admin'

    class Meta:
        db_table = 'componentes_usuario'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Duenos(models.Model):
    # BUGFIX: se eliminó la coma extra que convertía el campo en una tupla
    id = models.BigAutoField(primary_key=True)
    Nombre = models.CharField(max_length=30, null=False, blank=False)
    Apellido = models.CharField(max_length=30, null=False, blank=False)
    Edad = models.IntegerField()
    Correo = models.EmailField(max_length=50, null=False, blank=False, unique=True)
    Telefono = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"

    class Meta:
        verbose_name = "Dueño"
        verbose_name_plural = "Dueños"


class Especialidades(models.Model):
    IDEspecialidad = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"


class Doctores(models.Model):
    IDDoctor = models.BigAutoField(primary_key=True)
    Nombre = models.CharField(max_length=30, null=False, blank=False)
    Apellido = models.CharField(max_length=30, null=False, blank=False)
    Especialidad = models.ForeignKey("Especialidades", on_delete=models.PROTECT)

    def __str__(self):
        # BUGFIX: era self.nombre (minúscula) pero el campo es Nombre (mayúscula)
        return f"{self.Nombre} {self.Apellido}"

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"


class Raza(models.Model):
    # BUGFIX: se eliminó la coma extra que convertía el campo en una tupla
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=30, null=False, blank=False)
    imagen = models.ImageField(upload_to='razas/', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Raza'
        verbose_name_plural = 'Razas'


class Mascotas(models.Model):
    ESPECIE_CHOICES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('otro', 'Otro'),
    ]

    IdMascota = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=30, null=False, blank=False)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES, default='perro')
    otra_especie = models.CharField(max_length=30, blank=True, default='', verbose_name='Especie (otro)')
    dueno = models.ForeignKey("Duenos", on_delete=models.PROTECT, blank=True, null=False)
    raza = models.ForeignKey("Raza", on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre

    @property
    def especie_display(self):
        if self.especie == 'otro' and self.otra_especie:
            return self.otra_especie
        return self.get_especie_display()

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"


class Historias(models.Model):
    IDHistoria = models.BigAutoField(primary_key=True)
    numero_historia = models.CharField(max_length=10, unique=True)
    Descripcion = models.TextField(max_length=500)
    mascota = models.ForeignKey("Mascotas", verbose_name="Mascota", on_delete=models.DO_NOTHING)
    doctor = models.ForeignKey("Doctores", verbose_name="Doctor", on_delete=models.DO_NOTHING)
    Fecha = models.DateField(auto_now_add=True, verbose_name="Fecha de creación")

    def __str__(self):
        return f"Historia {self.numero_historia} - {self.mascota.nombre}"

    class Meta:
        verbose_name = "Historia"
        verbose_name_plural = "Historias"
        ordering = ['-Fecha']


class Citas(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    IdCita = models.BigAutoField(primary_key=True)
    mascota = models.ForeignKey("Mascotas", verbose_name="Mascota", on_delete=models.CASCADE)
    doctor = models.ForeignKey("Doctores", verbose_name="Doctor", on_delete=models.PROTECT)
    dueno = models.ForeignKey("Duenos", verbose_name="Dueño", on_delete=models.PROTECT)
    fecha_cita = models.DateTimeField(verbose_name="Fecha y Hora de la Cita")
    motivo = models.CharField(max_length=100, verbose_name="Motivo de la Cita")
    descripcion = models.TextField(max_length=500, blank=True, null=True, verbose_name="Descripción")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas del Doctor")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    def __str__(self):
        return f"Cita - {self.mascota.nombre} ({self.fecha_cita.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['-fecha_cita']
