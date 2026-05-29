from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from vet3.Componentes.models import Duenos, Especialidades, Doctores, Raza, Mascotas, Historias, Citas

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username='admin1',
            password='admin123',
            rol='admin',
            is_staff=True
        )
        self.vet = Usuario.objects.create_user(
            username='vet1',
            password='vet123',
            rol='veterinario'
        )
        self.recepcionista = Usuario.objects.create_user(
            username='recepcionista1',
            password='rec123',
            rol='recepcionista'
        )

    def test_usuario_str(self):
        self.assertEqual(str(self.admin), 'admin1')
        self.assertEqual(str(self.vet), 'vet1')

    def test_usuario_roles(self):
        self.assertTrue(self.admin.es_admin)
        self.assertFalse(self.admin.es_veterinario)
        self.assertFalse(self.admin.es_recepcionista)

        self.assertTrue(self.vet.es_veterinario)
        self.assertFalse(self.vet.es_admin)

        self.assertTrue(self.recepcionista.es_recepcionista)
        self.assertFalse(self.recepcionista.es_admin)

    def test_usuario_password_hashed(self):
        admin = Usuario.objects.get(username='admin1')
        self.assertNotEqual(admin.password, 'admin123')
        self.assertTrue(admin.password.startswith('pbkdf2_'))

    def test_usuario_authenticate(self):
        from django.contrib.auth import authenticate
        user = authenticate(username='admin1', password='admin123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'admin1')

    def test_usuario_invalid_authenticate(self):
        from django.contrib.auth import authenticate
        user = authenticate(username='admin1', password='wrong')
        self.assertIsNone(user)

    def test_create_superuser(self):
        superuser = Usuario.objects.create_superuser(
            username='super',
            password='super123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)


class DuenosModelTest(TestCase):
    def setUp(self):
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )

    def test_duenos_str(self):
        self.assertEqual(str(self.dueno), 'Juan Pérez')

    def test_duenos_verbose_name(self):
        self.assertEqual(str(Duenos._meta.verbose_name), 'Dueño')
        self.assertEqual(str(Duenos._meta.verbose_name_plural), 'Dueños')

    def test_duenos_unique_email(self):
        with self.assertRaises(Exception):
            Duenos.objects.create(
                Nombre='Maria',
                Apellido='Lopez',
                Edad=25,
                Correo='juan@example.com',
                Telefono='0987654321'
            )


class EspecialidadesModelTest(TestCase):
    def setUp(self):
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')

    def test_especialidades_str(self):
        self.assertEqual(str(self.especialidad), 'Cirugía')

    def test_especialidades_verbose_name(self):
        self.assertEqual(str(Especialidades._meta.verbose_name), 'Especialidad')
        self.assertEqual(str(Especialidades._meta.verbose_name_plural), 'Especialidades')


class DoctoresModelTest(TestCase):
    def setUp(self):
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.doctor = Doctores.objects.create(
            Nombre='Carlos',
            Apellido='Rodriguez',
            Especialidad=self.especialidad
        )

    def test_doctores_str(self):
        self.assertEqual(str(self.doctor), 'Carlos Rodriguez')

    def test_doctores_verbose_name(self):
        self.assertEqual(str(Doctores._meta.verbose_name), 'Doctor')
        self.assertEqual(str(Doctores._meta.verbose_name_plural), 'Doctores')

    def test_doctor_especialidad_fk(self):
        self.assertEqual(self.doctor.Especialidad, self.especialidad)


class RazaModelTest(TestCase):
    def setUp(self):
        self.raza = Raza.objects.create(nombre='Labrador')

    def test_raza_str(self):
        self.assertEqual(str(self.raza), 'Labrador')

    def test_raza_verbose_name(self):
        self.assertEqual(str(Raza._meta.verbose_name), 'Raza')
        self.assertEqual(str(Raza._meta.verbose_name_plural), 'Razas')


class MascotasModelTest(TestCase):
    def setUp(self):
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        self.raza = Raza.objects.create(nombre='Labrador')
        self.mascota = Mascotas.objects.create(
            nombre='Rex',
            especie='perro',
            dueno=self.dueno,
            raza=self.raza
        )

    def test_mascotas_str(self):
        self.assertEqual(str(self.mascota), 'Rex')

    def test_mascotas_verbose_name(self):
        self.assertEqual(str(Mascotas._meta.verbose_name), 'Mascota')
        self.assertEqual(str(Mascotas._meta.verbose_name_plural), 'Mascotas')

    def test_mascota_dueno_fk(self):
        self.assertEqual(self.mascota.dueno, self.dueno)

    def test_mascota_raza_fk(self):
        self.assertEqual(self.mascota.raza, self.raza)

    def test_mascota_especie_default(self):
        self.assertEqual(self.mascota.especie, 'perro')

    def test_mascota_especie_choices(self):
        especies = [choice[0] for choice in Mascotas.ESPECIE_CHOICES]
        self.assertIn('perro', especies)
        self.assertIn('gato', especies)
        self.assertIn('otro', especies)

    def test_mascota_otra_especie(self):
        mascota_otra = Mascotas.objects.create(
            nombre='Loro',
            especie='otro',
            otra_especie='Ave',
            dueno=self.dueno,
            raza=self.raza
        )
        self.assertEqual(mascota_otra.especie_display, 'Ave')


class HistoriasModelTest(TestCase):
    def setUp(self):
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        self.raza = Raza.objects.create(nombre='Labrador')
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
        self.historia = Historias.objects.create(
            numero_historia='H001',
            Descripcion='Consulta general',
            mascota=self.mascota,
            doctor=self.doctor
        )

    def test_historias_str(self):
        self.assertEqual(str(self.historia), 'Historia H001 - Rex')

    def test_historias_verbose_name(self):
        self.assertEqual(str(Historias._meta.verbose_name), 'Historia')
        self.assertEqual(str(Historias._meta.verbose_name_plural), 'Historias')

    def test_historia_unique_numero(self):
        with self.assertRaises(Exception):
            Historias.objects.create(
                numero_historia='H001',
                Descripcion='Otra consulta',
                mascota=self.mascota,
                doctor=self.doctor
            )

    def test_historia_ordering(self):
        self.assertEqual(Historias._meta.ordering, ['-Fecha'])


class CitasModelTest(TestCase):
    def setUp(self):
        from django.utils import timezone
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        self.raza = Raza.objects.create(nombre='Labrador')
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
        self.cita = Citas.objects.create(
            mascota=self.mascota,
            doctor=self.doctor,
            dueno=self.dueno,
            fecha_cita=timezone.now(),
            motivo='Vacunación'
        )

    def test_citas_str(self):
        expected = f"Cita - {self.mascota.nombre}"
        self.assertIn(expected, str(self.cita))

    def test_citas_verbose_name(self):
        self.assertEqual(str(Citas._meta.verbose_name), 'Cita')
        self.assertEqual(str(Citas._meta.verbose_name_plural), 'Citas')

    def test_cita_default_estado(self):
        self.assertEqual(self.cita.estado, 'pendiente')

    def test_cita_estado_choices(self):
        estados = [choice[0] for choice in Citas.ESTADO_CHOICES]
        self.assertIn('pendiente', estados)
        self.assertIn('confirmada', estados)
        self.assertIn('cancelada', estados)
        self.assertIn('completada', estados)

    def test_cita_ordering(self):
        self.assertEqual(Citas._meta.ordering, ['-fecha_cita'])
