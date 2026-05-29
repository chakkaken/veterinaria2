from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from vet3.Componentes.models import Duenos, Especialidades, Doctores, Raza, Mascotas, Historias, Citas
from vet3.Componentes.services.email_service import EmailNotificationService
from vet3.Componentes.services.report_service import ReportService

Usuario = get_user_model()


class EmailNotificationServiceTest(TestCase):
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
        self.cita = Citas.objects.create(
            mascota=self.mascota,
            doctor=self.doctor,
            dueno=self.dueno,
            fecha_cita=timezone.now(),
            motivo='Vacunación'
        )

    def test_enviar_confirmacion_cita_no_crash(self):
        EmailNotificationService.enviar_confirmacion_cita(self.cita)

    def test_enviar_cambio_estado_cita_no_crash(self):
        estado_anterior = self.cita.estado
        self.cita.estado = 'confirmada'
        EmailNotificationService.enviar_cambio_estado_cita(self.cita, estado_anterior)

    def test_enviar_recordatorio_cita_no_crash(self):
        EmailNotificationService.enviar_recordatorio_cita(self.cita)

    def test_enviar_bienvenida_no_crash(self):
        usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            rol='recepcionista'
        )
        EmailNotificationService.enviar_bienvenida(usuario)


class ReportServiceTest(TestCase):
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
        self.cita = Citas.objects.create(
            mascota=self.mascota,
            doctor=self.doctor,
            dueno=self.dueno,
            fecha_cita=timezone.now(),
            motivo='Vacunación'
        )

    def test_get_estadisticas_generales(self):
        stats = ReportService.get_estadisticas_generales()
        self.assertEqual(stats['total_mascotas'], 1)
        self.assertEqual(stats['total_duenos'], 1)
        self.assertEqual(stats['total_doctores'], 1)
        self.assertEqual(stats['total_citas'], 1)

    def test_get_citas_por_estado(self):
        result = ReportService.get_citas_por_estado()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['total'], 1)

    def test_get_citas_por_doctor(self):
        result = ReportService.get_citas_por_doctor()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['total'], 1)

    def test_get_top_mascotas_frecuentes(self):
        result = ReportService.get_top_mascotas_frecuentes()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['total'], 1)

    def test_get_citas_rango_fechas(self):
        now = timezone.now()
        fecha_inicio = now - timezone.timedelta(days=30)
        fecha_fin = now + timezone.timedelta(days=30)
        
        result = ReportService.get_citas_rango_fechas(fecha_inicio, fecha_fin)
        self.assertEqual(result.count(), 1)

    def test_generar_pdf_citas(self):
        citas = Citas.objects.all()
        pdf = ReportService.generar_pdf_citas(citas)
        self.assertIsNotNone(pdf)
        self.assertTrue(len(pdf) > 0)

    def test_generar_pdf_estadisticas(self):
        pdf = ReportService.generar_pdf_estadisticas()
        self.assertIsNotNone(pdf)
        self.assertTrue(len(pdf) > 0)

    def test_generar_csv_citas(self):
        citas = Citas.objects.all()
        csv_data = ReportService.generar_csv_citas(citas)
        self.assertIsNotNone(csv_data)
        self.assertIn('Mascota', csv_data)
        self.assertIn('Rex', csv_data)

    def test_generar_csv_mascotas(self):
        csv_data = ReportService.generar_csv_mascotas()
        self.assertIsNotNone(csv_data)
        self.assertIn('Nombre', csv_data)
        self.assertIn('Rex', csv_data)

    def test_generar_csv_duenos(self):
        csv_data = ReportService.generar_csv_duenos()
        self.assertIsNotNone(csv_data)
        self.assertIn('Nombre', csv_data)
        self.assertIn('Juan', csv_data)


class ReportesViewsTest(TestCase):
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

    def test_reportes_view_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('reportes'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("reportes")}')

    def test_reportes_view_admin_allowed(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('reportes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportes/reportes.html')

    def test_reporte_citas_pdf_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('reporte_citas_pdf'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("reporte_citas_pdf")}')

    def test_reporte_citas_pdf_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('reporte_citas_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_reporte_estadisticas_pdf_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('reporte_estadisticas_pdf'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("reporte_estadisticas_pdf")}')

    def test_reporte_estadisticas_pdf_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('reporte_estadisticas_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_reporte_citas_csv_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('reporte_citas_csv'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("reporte_citas_csv")}')

    def test_reporte_citas_csv_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('reporte_citas_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_reporte_mascotas_csv_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('reporte_mascotas_csv'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("reporte_mascotas_csv")}')

    def test_reporte_mascotas_csv_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('reporte_mascotas_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_reporte_duenos_csv_requires_staff(self):
        self.client.login(username='non_staff', password='user123')
        response = self.client.get(reverse('reporte_duenos_csv'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("reporte_duenos_csv")}')

    def test_reporte_duenos_csv_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('reporte_duenos_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')


class CitasEmailNotificationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='admin123',
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

    def test_citas_create_sends_email(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('citas_create'), {
            'mascota': self.mascota.pk,
            'doctor': self.doctor.pk,
            'dueno': self.dueno.pk,
            'fecha_cita': timezone.now(),
            'motivo': 'Vacunación',
            'estado': 'pendiente'
        }, follow=True)
        self.assertEqual(Citas.objects.filter(motivo='Vacunación').count(), 1)

    def test_citas_update_cambio_estado_sends_email(self):
        self.client.login(username='admin', password='admin123')
        
        cita = Citas.objects.create(
            mascota=self.mascota,
            doctor=self.doctor,
            dueno=self.dueno,
            fecha_cita=timezone.now(),
            motivo='Consulta',
            estado='pendiente'
        )
        
        response = self.client.post(reverse('citas_update', args=[cita.pk]), {
            'mascota': self.mascota.pk,
            'doctor': self.doctor.pk,
            'dueno': self.dueno.pk,
            'fecha_cita': timezone.now(),
            'motivo': 'Consulta',
            'estado': 'confirmada'
        }, follow=True)
        
        cita.refresh_from_db()
        self.assertEqual(cita.estado, 'confirmada')
