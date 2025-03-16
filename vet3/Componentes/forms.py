from django import forms
from .models import Usuario, Mascotas, Duenos, Doctores, Especialidades, Historias, Raza, Usuario
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Mascotas






class MascotasForm(forms.ModelForm):
    class Meta:
        model = Mascotas
        fields = ['nombre', 'correo', 'dueno', 'raza']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la mascota'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el correo electrónico'
            }),
            'dueno': forms.Select(attrs={
                'class': 'form-control'
            }),
            'raza': forms.Select(attrs={
                'class': 'form-control'
            })
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
                'class': 'form-control'
            }),
            'Telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el Telefono'
            })
        }
        
        def clean_edad(self):
            Edad = self.cleaned_data.get('edad')
            if Edad is None:
             raise forms.ValidationError('Este campo es requerido.')
            if Edad < 18:
                raise forms.ValidationError('Debe ser mayor de 18 años para registrarse como dueño.')
            if Edad > 100:
                raise forms.ValidationError('La edad máxima permitida es 100 años.')
            return Edad
        

class DoctoresForm(forms.ModelForm):
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
            'Especialidad': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class EspecialidadesForm(forms.ModelForm):
    class Meta:
        model = Especialidades
        fields = ['nombre']

class HistoriasForm(forms.ModelForm):
    class Meta:
        model = Historias
        fields = ['numero_historia', 'mascota', 'doctor', 'Descripcion']
        labels = {
            'numero_historia': 'Número de Historia',
            'mascota': 'Mascota',
            'doctor': 'doctor',
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
        def clean_numero_historia(self):
            numero = self.cleaned_data.get('numero_historia')
            if self.instance.pk:  # Si es una edición, excluye la instancia actual
                if Historias.objects.filter(numero_historia=numero).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Este número de historia ya existe.')
                else:  # Si es una creación, verifica si el número ya existe
                    if Historias.objects.filter(numero_historia=numero).exists():
                     raise forms.ValidationError('Este número de historia ya existe.')
            return numero

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los campos para mostrar nombres completos
        self.fields['mascota'].queryset = Mascotas.objects.all()
        self.fields['mascota'].label_from_instance = lambda obj: obj.nombre
        
        self.fields['doctor'].queryset = Doctores.objects.all()
        self.fields['doctor'].label_from_instance = lambda obj: f"{obj.Nombre} {obj.Apellido}"
        
    

class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ['nombre', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'})
        }


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Las contraseñas no coinciden"
            )