from django.contrib import admin
from .models import Historias, Mascotas, Doctores, Duenos, Usuario, Raza, Citas

# Register your models here.
admin.site.register(Historias)
admin.site.register(Mascotas)
admin.site.register(Doctores)
admin.site.register(Duenos)
admin.site.register(Usuario)
admin.site.register(Raza)
admin.site.register(Citas)