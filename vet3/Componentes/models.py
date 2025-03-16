from django.db import models


# Create your models here.
class Meta:

    def __str__(self):
        return self.name

    

# Create your models here.
class Usuario(models.Model):
    IdUsuario= models.BigAutoField(primary_key=True)
    nombre= models.CharField(max_length=30,null= False,)
    password= models.CharField(max_length=50,null=False)

    def __str__(self):
        return self.nombre

class Mascotas(models.Model):
    IdMascota= models.BigAutoField(primary_key=True)
    nombre= models.CharField(max_length=30,null=False,blank=False)
  
    correo= models.EmailField(max_length=50,null=False,unique=True)
    dueno= models.ForeignKey("Duenos", on_delete=models.PROTECT,blank=True,null=False)
    raza= models.ForeignKey("raza", on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"

class Duenos(models.Model):
    Id= models.BigAutoField(primary_key=True),
    Nombre= models.CharField(max_length=30,null=False,blank=False)
    Apellido= models.CharField(max_length=30,null=False,blank=False)
    Edad= models.IntegerField()
    Correo= models.EmailField(max_length=50,null=False,blank=False,unique=True)
    Telefono= models.CharField(max_length=10)

    def __str__(self):
        return self.Nombre
    

class Doctores(models.Model):
    IDDoctor= models.BigAutoField(primary_key=True)
    Nombre=models.CharField(max_length=30,null=False,blank=True)
    Apellido= models.CharField(max_length=30,null=False,blank=False)
    Especialidad=models.ForeignKey("Especialidades", on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre

class Especialidades(models.Model):
    IDEspecialidad=models.BigAutoField(primary_key=True)
    nombre=models.CharField(max_length=20,null=False,blank=True)

    def __str__(self):
        return self.nombre

class Historias(models.Model):
    IDHistoria=models.BigAutoField(primary_key=True)
    numero_historia = models.CharField(max_length=10, unique=True)
    Descripcion=models.TextField(max_length=500)
    mascota= models.ForeignKey("mascotas",verbose_name="nombre",on_delete=models.DO_NOTHING)
    doctor=models.ForeignKey("Doctores",verbose_name="nombre", on_delete=models.DO_NOTHING)
    Fecha= models.DateField(auto_now_add=True,verbose_name="Fecha de creación")

    def __str__(self):
        return f"Historia {self.numero_historia} - {self.mascota.nombre}"

    class Meta:
        verbose_name = "Historia"
        verbose_name_plural = "Historias"

class Raza(models.Model):
    IdRaza= models.BigAutoField(primary_key=True),
    nombre=models.CharField(max_length=30,null=False,blank=True)
    imagen = models.ImageField(upload_to='razas/', null=True, blank=True)

    class Meta:
        verbose_name = 'Raza'
        verbose_name_plural = 'Razas'
    
    def __str__(self):
        return self.nombre
    
        
