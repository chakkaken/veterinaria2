import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Mascotas, Duenos, Doctores, Especialidades, Historias, Raza, Citas


class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rol'
    )
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'telefono', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }
        labels = {
            'username': 'Nombre de usuario',
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula.')

        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')

        if not re.search(r'[^a-zA-Z0-9]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un símbolo (ej: @, #, $, %, etc.).')

        return password


class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'telefono', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar contraseña'
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            usuario.set_password(password)
        if commit:
            usuario.save()
        return usuario


class MascotasForm(forms.ModelForm):
    class Meta:
        model = Mascotas
        fields = ['nombre', 'especie', 'otra_especie', 'dueno', 'raza']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la mascota'
            }),
            'especie': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_especie'
            }),
            'otra_especie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especifique la especie',
                'id': 'id_otra_especie'
            }),
            'dueno': forms.Select(attrs={
                'class': 'form-control'
            }),
            'raza': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'especie': 'Especie',
            'otra_especie': 'Especifique la especie',
            'dueno': 'Dueño',
            'raza': 'Raza',
        }


class DuenosForm(forms.ModelForm):
    class Meta:
        model = Duenos
        fields = ['Nombre', 'Apellido', 'Edad', 'Correo', 'Telefono']
        widgets = {
            'Nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'Apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido'
            }),
            'Edad': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'Correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el correo'
            }),
            'Telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el teléfono'
            })
        }

    # BUGFIX: clean_edad estaba dentro de class Meta, nunca se ejecutaba
    def clean_Edad(self):
        edad = self.cleaned_data.get('Edad')
        if edad is None:
            raise forms.ValidationError('Este campo es requerido.')
        if edad < 18:
            raise forms.ValidationError('Debe ser mayor de 18 años para registrarse como dueño.')
        if edad > 100:
            raise forms.ValidationError('La edad máxima permitida es 100 años.')
        return edad


class DoctoresForm(forms.ModelForm):
    Especialidad = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la especialidad'
        })
    )

    class Meta:
        model = Doctores
        fields = ['Nombre', 'Apellido', 'Especialidad']
        widgets = {
            'Nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'Apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.Especialidad:
            self.fields['Especialidad'].initial = self.instance.Especialidad.nombre

    def clean_Especialidad(self):
        especialidad_nombre = self.cleaned_data.get('Especialidad')
        if not especialidad_nombre:
            raise forms.ValidationError('La especialidad es requerida.')
        especialidad, _ = Especialidades.objects.get_or_create(nombre=especialidad_nombre)
        return especialidad


class EspecialidadesForm(forms.ModelForm):
    class Meta:
        model = Especialidades
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la especialidad'
            })
        }


class HistoriasForm(forms.ModelForm):
    class Meta:
        model = Historias
        fields = ['numero_historia', 'mascota', 'doctor', 'Descripcion']
        labels = {
            'numero_historia': 'Número de Historia',
            'mascota': 'Mascota',
            'doctor': 'Doctor',
            'Descripcion': 'Descripción',
        }
        widgets = {
            'numero_historia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de historia'
            }),
            'mascota': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'Descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la descripción de la historia clínica',
                'rows': 4
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mascota'].queryset = Mascotas.objects.all()
        self.fields['mascota'].label_from_instance = lambda obj: obj.nombre
        self.fields['doctor'].queryset = Doctores.objects.all()
        self.fields['doctor'].label_from_instance = lambda obj: f"{obj.Nombre} {obj.Apellido}"

    # BUGFIX: clean_numero_historia estaba dentro de class Meta, nunca se ejecutaba
    def clean_numero_historia(self):
        numero = self.cleaned_data.get('numero_historia')
        qs = Historias.objects.filter(numero_historia=numero)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este número de historia ya existe.')
        return numero


class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ['nombre', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la raza'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'})
        }





class CitasForm(forms.ModelForm):
    class Meta:
        model = Citas
        fields = ['mascota', 'doctor', 'dueno', 'fecha_cita', 'motivo', 'descripcion', 'estado', 'notas']
        labels = {
            'mascota': 'Mascota',
            'doctor': 'Doctor',
            'dueno': 'Dueño',
            'fecha_cita': 'Fecha y Hora de la Cita',
            'motivo': 'Motivo de la Cita',
            'descripcion': 'Descripción',
            'estado': 'Estado',
            'notas': 'Notas del Doctor',
        }
        widgets = {
            'mascota': forms.Select(attrs={
                'class': 'form-control'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'dueno': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_cita': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Vacunación, Revisión General, Cirugía'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción adicional de la cita',
                'rows': 3
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notas del doctor después de la cita',
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mascota'].queryset = Mascotas.objects.all()
        self.fields['mascota'].label_from_instance = lambda obj: obj.nombre
        self.fields['doctor'].queryset = Doctores.objects.all()
        self.fields['doctor'].label_from_instance = lambda obj: f"{obj.Nombre} {obj.Apellido} ({obj.Especialidad.nombre})"
        self.fields['dueno'].queryset = Duenos.objects.all()
        self.fields['dueno'].label_from_instance = lambda obj: f"{obj.Nombre} {obj.Apellido}"