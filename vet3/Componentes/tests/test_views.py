from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from vet3.Componentes.models import Duenos, Especialidades, Doctores, Raza, Mascotas, Historias, Citas

Usuario = get_user_model()


class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='admin',
            is_staff=True
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post_valid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_index_view_redirects_if_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_dashboard_view_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class MascotasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='admin',
            is_staff=True
        )
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

    def test_mascotas_public_list(self):
        response = self.client.get(reverse('mascotas_public'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mascotas/mascotas_list.html')

    def test_mascotas_list_requires_login(self):
        response = self.client.get(reverse('mascotas_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("mascotas_list")}')

    def test_mascotas_list_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('mascotas_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rex')

    def test_mascota_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('mascotas_create'), {
            'nombre': 'Max',
            'especie': 'gato',
            'dueno': self.dueno.pk,
            'raza': self.raza.pk
        })
        self.assertRedirects(response, reverse('mascotas_list'))
        self.assertEqual(Mascotas.objects.filter(nombre='Max').count(), 1)

    def test_mascota_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('mascotas_form', args=[self.mascota.pk]), {
            'nombre': 'Rex Updated',
            'especie': 'perro',
            'dueno': self.dueno.pk,
            'raza': self.raza.pk
        })
        self.assertRedirects(response, reverse('mascotas_list'))
        self.mascota.refresh_from_db()
        self.assertEqual(self.mascota.nombre, 'Rex Updated')

    def test_mascota_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('mascotas_delete', args=[self.mascota.pk]))
        self.assertRedirects(response, reverse('mascotas_list'))
        self.assertEqual(Mascotas.objects.filter(pk=self.mascota.pk).count(), 0)


class DuenosViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='admin',
            is_staff=True
        )
        self.dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )

    def test_duenos_list_requires_login(self):
        response = self.client.get(reverse('duenos_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("duenos_list")}')

    def test_duenos_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('duenos_create'), {
            'Nombre': 'Maria',
            'Apellido': 'Lopez',
            'Edad': 25,
            'Correo': 'maria@example.com',
            'Telefono': '0987654321'
        })
        self.assertRedirects(response, reverse('duenos_list'))
        self.assertEqual(Duenos.objects.filter(Correo='maria@example.com').count(), 1)

    def test_duenos_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('duenos_update', args=[self.dueno.pk]), {
            'Nombre': 'Juan Updated',
            'Apellido': 'Pérez',
            'Edad': 31,
            'Correo': 'juan@example.com',
            'Telefono': '1234567890'
        })
        self.assertRedirects(response, reverse('duenos_list'))
        self.dueno.refresh_from_db()
        self.assertEqual(self.dueno.Nombre, 'Juan Updated')

    def test_duenos_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('duenos_delete', args=[self.dueno.pk]))
        self.assertRedirects(response, reverse('duenos_list'))
        self.assertEqual(Duenos.objects.filter(pk=self.dueno.pk).count(), 0)


class DoctoresViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='admin',
            is_staff=True
        )
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.doctor = Doctores.objects.create(
            Nombre='Carlos',
            Apellido='Rodriguez',
            Especialidad=self.especialidad
        )

    def test_doctores_list_requires_login(self):
        response = self.client.get(reverse('doctores_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("doctores_list")}')

    def test_doctores_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('doctores_create'), {
            'Nombre': 'Ana',
            'Apellido': 'Martinez',
            'Especialidad': 'Cardiología'
        })
        self.assertRedirects(response, reverse('doctores_list'))
        self.assertEqual(Doctores.objects.filter(Nombre='Ana').count(), 1)

    def test_doctores_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('doctores_delete', args=[self.doctor.pk]))
        self.assertRedirects(response, reverse('doctores_list'))
        self.assertEqual(Doctores.objects.filter(pk=self.doctor.pk).count(), 0)


class RazasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='admin',
            is_staff=True
        )
        self.raza = Raza.objects.create(nombre='Labrador')

    def test_razas_list_requires_login(self):
        response = self.client.get(reverse('razas_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("razas_list")}')

    def test_razas_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('razas_create'), {
            'nombre': 'Pastor Alemán'
        })
        self.assertRedirects(response, reverse('razas_list'))
        self.assertEqual(Raza.objects.filter(nombre='Pastor Alemán').count(), 1)

    def test_razas_delete_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('razas_delete', args=[self.raza.pk]))
        self.assertRedirects(response, reverse('razas_list'))
        self.assertEqual(Raza.objects.filter(pk=self.raza.pk).count(), 0)


class HistoriasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin',
            is_staff=True
        )
        self.vet = Usuario.objects.create_user(
            username='vet',
            password='vet123',
            rol='veterinario'
        )
        self.recepcionista = Usuario.objects.create_user(
            username='recepcionista',
            password='rec123',
            rol='recepcionista'
        )
        
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
        self.historia = Historias.objects.create(
            numero_historia='H001',
            Descripcion='Consulta general',
            mascota=self.mascota,
            doctor=self.doctor
        )

    def test_historia_list_requires_login(self):
        response = self.client.get(reverse('historia_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("historia_list")}')

    def test_historia_list_recepcionista_denied(self):
        self.client.login(username='recepcionista', password='rec123')
        response = self.client.get(reverse('historia_list'))
        self.assertEqual(response.status_code, 403)

    def test_historia_list_vet_allowed(self):
        self.client.login(username='vet', password='vet123')
        response = self.client.get(reverse('historia_list'))
        self.assertEqual(response.status_code, 200)

    def test_historia_list_admin_allowed(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('historia_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'H001')

    def test_historia_search_by_numero(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('historia_list'), {'campo_busqueda': 'numero_historia', 'termino': 'H001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'H001')

    def test_historia_search_by_numero_no_results(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('historia_list'), {'campo_busqueda': 'numero_historia', 'termino': 'NOEXISTE'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'H001')

    def test_historia_search_by_doctor(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('historia_list'), {'campo_busqueda': 'doctor', 'termino': 'Carlos'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'H001')

    def test_historia_search_by_mascota(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('historia_list'), {'campo_busqueda': 'mascota', 'termino': 'Rex'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'H001')


class CitasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin',
            is_staff=True
        )
        self.recepcionista = Usuario.objects.create_user(
            username='recepcionista',
            password='rec123',
            rol='recepcionista'
        )
        
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
        self.cita = Citas.objects.create(
            mascota=self.mascota,
            doctor=self.doctor,
            dueno=self.dueno,
            fecha_cita=timezone.now(),
            motivo='Vacunación'
        )

    def test_citas_list_requires_login(self):
        response = self.client.get(reverse('citas_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("citas_list")}')

    def test_citas_list_recepcionista_allowed(self):
        self.client.login(username='recepcionista', password='rec123')
        response = self.client.get(reverse('citas_list'))
        self.assertEqual(response.status_code, 200)

    def test_citas_create_view(self):
        self.client.login(username='recepcionista', password='rec123')
        response = self.client.post(reverse('citas_create'), {
            'mascota': self.mascota.pk,
            'doctor': self.doctor.pk,
            'dueno': self.dueno.pk,
            'fecha_cita': timezone.now(),
            'motivo': 'Revisión',
            'estado': 'pendiente'
        })
        self.assertRedirects(response, reverse('citas_list'))
        self.assertEqual(Citas.objects.filter(motivo='Revisión').count(), 1)


class UsuarioViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin',
            is_staff=True
        )
        self.non_staff = Usuario.objects.create_user(
            username='user',
            password='user123',
            rol='recepcionista'
        )

    def test_usuario_list_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('usuario_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("usuario_list")}')

    def test_usuario_list_admin_allowed(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('usuario_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin')

    def test_usuario_create_view(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('usuario_create'), {
            'username': 'newuser',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            'rol': 'veterinario'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(Usuario.objects.filter(username='newuser').count(), 1)
