from django.contrib import admin
from .models import Historias, Mascotas, Doctores,Duenos,Usuario,Raza

# Register your models here.
admin.site.register(Historias)
admin.site.register(Mascotas)
admin.site.register(Doctores)
admin.site.register(Duenos)
admin.site.register(Usuario)
admin.site.register(Raza)