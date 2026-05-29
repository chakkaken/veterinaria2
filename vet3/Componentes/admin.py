from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Historias, Mascotas, Doctores, Duenos, Usuario, Raza, Citas, VerificationToken
from .forms import UsuarioCreationForm, UsuarioChangeForm


class UsuarioAdmin(BaseUserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    list_display = ('username', 'email', 'rol', 'is_active', 'is_verified', 'is_staff')
    list_filter = ('is_active', 'is_verified', 'rol', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('email', 'telefono', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'rol', 'telefono', 'is_staff', 'is_active')
        }),
    )


admin.site.register(Historias)
admin.site.register(Mascotas)
admin.site.register(Doctores)
admin.site.register(Duenos)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Raza)
admin.site.register(Citas)
admin.site.register(VerificationToken)