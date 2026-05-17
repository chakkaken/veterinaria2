from django.test import TestCase
from django.utils import timezone
from Componentes.models import Duenos, Especialidades, Doctores, Raza, Mascotas, Historias, Citas
from Componentes.forms import (
    DuenosForm, UsuarioCreationForm, DoctoresForm,
    HistoriasForm, CitasForm, MascotasForm, RazaForm
)


class DuenosFormTest(TestCase):
    def test_valid_form(self):
        form = DuenosForm(data={
            'Nombre': 'Juan',
            'Apellido': 'Pérez',
            'Edad': 30,
            'Correo': 'juan@example.com',
            'Telefono': '1234567890'
        })
        self.assertTrue(form.is_valid())

    def test_edad_menor_18(self):
        form = DuenosForm(data={
            'Nombre': 'Juan',
            'Apellido': 'Pérez',
            'Edad': 15,
            'Correo': 'juan@example.com',
            'Telefono': '1234567890'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Edad', form.errors)

    def test_edad_mayor_100(self):
        form = DuenosForm(data={
            'Nombre': 'Juan',
            'Apellido': 'Pérez',
            'Edad': 105,
            'Correo': 'juan@example.com',
            'Telefono': '1234567890'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Edad', form.errors)

    def test_edad_exact_18(self):
        form = DuenosForm(data={
            'Nombre': 'Juan',
            'Apellido': 'Pérez',
            'Edad': 18,
            'Correo': 'juan@example.com',
            'Telefono': '1234567890'
        })
        self.assertTrue(form.is_valid())

    def test_email_invalido(self):
        form = DuenosForm(data={
            'Nombre': 'Juan',
            'Apellido': 'Pérez',
            'Edad': 30,
            'Correo': 'correo-invalido',
            'Telefono': '1234567890'
        })
        self.assertFalse(form.is_valid())


class UsuarioCreationFormTest(TestCase):
    def test_valid_form(self):
        form = UsuarioCreationForm(data={
            'username': 'testuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'rol': 'recepcionista'
        })
        self.assertTrue(form.is_valid())

    def test_passwords_no_coinciden(self):
        form = UsuarioCreationForm(data={
            'username': 'testuser',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass456!',
            'rol': 'recepcionista'
        })
        self.assertFalse(form.is_valid())

    def test_username_duplicado(self):
        from django.contrib.auth import get_user_model
        Usuario = get_user_model()
        Usuario.objects.create_user(username='existing', password='pass123')
        
        form = UsuarioCreationForm(data={
            'username': 'existing',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'rol': 'recepcionista'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class DoctoresFormTest(TestCase):
    def test_crear_doctor_con_especialidad_nueva(self):
        form = DoctoresForm(data={
            'Nombre': 'Carlos',
            'Apellido': 'Rodriguez',
            'Especialidad': 'Cardiología'
        })
        self.assertTrue(form.is_valid())
        doctor = form.save()
        self.assertEqual(doctor.Especialidad.nombre, 'Cardiología')

    def test_crear_doctor_con_especialidad_existente(self):
        Especialidades.objects.create(nombre='Cirugía')
        
        form = DoctoresForm(data={
            'Nombre': 'Carlos',
            'Apellido': 'Rodriguez',
            'Especialidad': 'Cirugía'
        })
        self.assertTrue(form.is_valid())
        doctor = form.save()
        self.assertEqual(doctor.Especialidad.nombre, 'Cirugía')
        self.assertEqual(Especialidades.objects.filter(nombre='Cirugía').count(), 1)


class HistoriasFormTest(TestCase):
    def setUp(self):
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        self.raza = Raza.objects.create(nombre='Labrador')
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.doctor = Doctores.objects.create(
            Nombre='Carlos',
            Apellido='Rodriguez',
            Especialidad=self.especialidad
        )
        self.mascota = Mascotas.objects.create(
            nombre='Rex',
            especie='perro',
            dueno=self.dueno,
            raza=self.raza
        )

    def test_numero_historia_duplicado(self):
        Historias.objects.create(
            numero_historia='H001',
            Descripcion='Consulta',
            mascota=self.mascota,
            doctor=self.doctor
        )
        
        form = HistoriasForm(data={
            'numero_historia': 'H001',
            'Descripcion': 'Otra consulta',
            'mascota': self.mascota.pk,
            'doctor': self.doctor.pk
        })
        self.assertFalse(form.is_valid())
        self.assertIn('numero_historia', form.errors)

    def test_form_valido(self):
        form = HistoriasForm(data={
            'numero_historia': 'H002',
            'Descripcion': 'Consulta general',
            'mascota': self.mascota.pk,
            'doctor': self.doctor.pk
        })
        self.assertTrue(form.is_valid())


class CitasFormTest(TestCase):
    def setUp(self):
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        self.raza = Raza.objects.create(nombre='Labrador')
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.doctor = Doctores.objects.create(
            Nombre='Carlos',
            Apellido='Rodriguez',
            Especialidad=self.especialidad
        )
        self.mascota = Mascotas.objects.create(
            nombre='Rex',
            especie='perro',
            dueno=self.dueno,
            raza=self.raza
        )

    def test_form_valido(self):
        form = CitasForm(data={
            'mascota': self.mascota.pk,
            'doctor': self.doctor.pk,
            'dueno': self.dueno.pk,
            'fecha_cita': timezone.now(),
            'motivo': 'Vacunación',
            'estado': 'pendiente'
        })
        self.assertTrue(form.is_valid())


class MascotasFormTest(TestCase):
    def setUp(self):
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        self.raza = Raza.objects.create(nombre='Labrador')

    def test_form_valido(self):
        form = MascotasForm(data={
            'nombre': 'Rex',
            'especie': 'perro',
            'dueno': self.dueno.pk,
            'raza': self.raza.pk
        })
        self.assertTrue(form.is_valid())


class RazaFormTest(TestCase):
    def test_form_valido(self):
        form = RazaForm(data={
            'nombre': 'Labrador'
        })
        self.assertTrue(form.is_valid())
