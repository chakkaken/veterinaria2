from django.contrib import admin
from .models import Historias, Mascotas, Doctores, Duenos, Usuario, Raza, Citas, VerificationToken


class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_active', 'is_verified', 'is_staff')
    list_filter = ('is_active', 'is_verified', 'rol', 'is_staff')
    search_fields = ('username', 'email')


admin.site.register(Historias)
admin.site.register(Mascotas)
admin.site.register(Doctores)
admin.site.register(Duenos)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Raza)
admin.site.register(Citas)
admin.site.register(VerificationToken)