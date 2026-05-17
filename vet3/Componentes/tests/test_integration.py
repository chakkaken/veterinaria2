from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from Componentes.models import Duenos, Especialidades, Doctores, Raza, Mascotas, Historias, Citas

Usuario = get_user_model()


class FullAuthenticationFlowTest(TestCase):
    def test_complete_login_dashboard_logout_flow(self):
        client = Client()
        
        Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            rol='admin',
            is_staff=True
        )
        
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        response = client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testuser', str(response.content))


class CRUDMascotaFlowTest(TestCase):
    def test_complete_mascota_crud_flow(self):
        client = Client()
        
        user = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin',
            is_staff=True
        )
        client.login(username='admin', password='admin123')
        
        dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        raza = Raza.objects.create(nombre='Labrador')
        
        response = client.get(reverse('mascotas_list'))
        self.assertEqual(response.status_code, 200)
        
        response = client.post(reverse('mascotas_create'), {
            'nombre': 'Rex',
            'especie': 'perro',
            'dueno': dueno.pk,
            'raza': raza.pk
        })
        self.assertRedirects(response, reverse('mascotas_list'))
        self.assertEqual(Mascotas.objects.filter(nombre='Rex').count(), 1)
        
        mascota = Mascotas.objects.get(nombre='Rex')
        
        response = client.post(reverse('mascotas_form', args=[mascota.pk]), {
            'nombre': 'Rex Updated',
            'especie': 'perro',
            'dueno': dueno.pk,
            'raza': raza.pk
        })
        self.assertRedirects(response, reverse('mascotas_list'))
        mascota.refresh_from_db()
        self.assertEqual(mascota.nombre, 'Rex Updated')
        
        response = client.post(reverse('mascotas_delete', args=[mascota.pk]))
        self.assertRedirects(response, reverse('mascotas_list'))
        self.assertEqual(Mascotas.objects.filter(nombre='Rex Updated').count(), 0)


class RoleBasedAccessTest(TestCase):
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
        
        self.especialidad = Especialidades.objects.create(nombre='Cirugía')
        self.doctor = Doctores.objects.create(
            Nombre='Carlos',
            Apellido='Rodriguez',
            Especialidad=self.especialidad
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
        self.historia = Historias.objects.create(
            numero_historia='H001',
            Descripcion='Consulta',
            mascota=self.mascota,
            doctor=self.doctor
        )

    def test_admin_access_all(self):
        self.client.login(username='admin', password='admin123')
        
        urls = ['mascotas_list', 'duenos_list', 'doctores_list', 
                'razas_list', 'historia_list', 'citas_list', 'usuario_list']
        
        for url_name in urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, f"Admin should access {url_name}")

    def test_veterinario_access_historias(self):
        self.client.login(username='vet', password='vet123')
        
        response = self.client.get(reverse('historia_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('usuario_list'))
        self.assertEqual(response.status_code, 403)

    def test_recepcionista_no_access_historias(self):
        self.client.login(username='recepcionista', password='rec123')
        
        response = self.client.get(reverse('historia_list'))
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(reverse('citas_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('usuario_list'))
        self.assertEqual(response.status_code, 403)


class DashboardStatsTest(TestCase):
    def test_dashboard_shows_correct_stats(self):
        client = Client()
        user = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin',
            is_staff=True
        )
        client.login(username='admin', password='admin123')
        
        dueno = Duenos.objects.create(
            Nombre='Juan',
            Apellido='Pérez',
            Edad=30,
            Correo='juan@example.com',
            Telefono='1234567890'
        )
        raza = Raza.objects.create(nombre='Labrador')
        mascota = Mascotas.objects.create(
            nombre='Rex',
            especie='perro',
            dueno=dueno,
            raza=raza
        )
        
        response = client.get(reverse('dashboard'))
        
        self.assertEqual(response.context['total_mascotas'], 1)
        self.assertEqual(response.context['total_duenos'], 1)
        self.assertEqual(response.context['total_razas'], 1)


class PasswordResetFlowTest(TestCase):
    def test_password_reset_pages_exist(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
