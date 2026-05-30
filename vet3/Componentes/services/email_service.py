import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Servicio para enviar notificaciones por email."""

    @staticmethod
    def enviar_confirmacion_cita(cita):
        """Envía email de confirmación cuando se crea una cita."""
        subject = f'Confirmación de Cita - {cita.mascota.nombre}'
        message = f"""
Estimado/a {cita.dueno.Nombre} {cita.dueno.Apellido},

Su cita ha sido agendada exitosamente en VetSystem.

Detalles de la cita:
- Mascota: {cita.mascota.nombre}
- Doctor: Dr. {cita.doctor.Nombre} {cita.doctor.Apellido}
- Especialidad: {cita.doctor.Especialidad.nombre}
- Fecha: {cita.fecha_cita.strftime('%d/%m/%Y %H:%M')}
- Motivo: {cita.motivo}

Por favor llegue 10 minutos antes de la hora programada.

Saludos,
Equipo VetSystem
"""
        EmailNotificationService._safe_send_mail(subject, message, [cita.dueno.Correo], fail_silently=True)

    @staticmethod
    def enviar_cambio_estado_cita(cita, estado_anterior):
        """Envía email cuando cambia el estado de una cita."""
        estado_labels = {
            'pendiente': 'Pendiente',
            'confirmada': 'Confirmada',
            'cancelada': 'Cancelada',
            'completada': 'Completada',
        }
        
        subject = f'Cita {estado_labels.get(cita.estado, cita.estado)} - {cita.mascota.nombre}'
        message = f"""
Estimado/a {cita.dueno.Nombre} {cita.dueno.Apellido},

El estado de su cita ha cambiado de '{estado_labels.get(estado_anterior, estado_anterior)}' a '{estado_labels.get(cita.estado, cita.estado)}'.

Detalles de la cita:
- Mascota: {cita.mascota.nombre}
- Doctor: Dr. {cita.doctor.Nombre} {cita.doctor.Apellido}
- Fecha: {cita.fecha_cita.strftime('%d/%m/%Y %H:%M')}
- Motivo: {cita.motivo}

Saludos,
Equipo VetSystem
"""
        EmailNotificationService._safe_send_mail(subject, message, [cita.dueno.Correo], fail_silently=True)

    @staticmethod
    def enviar_recordatorio_cita(cita):
        """Envía recordatorio 24 horas antes de la cita."""
        subject = f'Recordatorio de Cita Mañana - {cita.mascota.nombre}'
        message = f"""
Estimado/a {cita.dueno.Nombre} {cita.dueno.Apellido},

Le recordamos que tiene una cita programada para mañana:

- Mascota: {cita.mascota.nombre}
- Doctor: Dr. {cita.doctor.Nombre} {cita.doctor.Apellido}
- Hora: {cita.fecha_cita.strftime('%H:%M')}
- Motivo: {cita.motivo}

Por favor confirme su asistencia respondiendo a este email.

Saludos,
Equipo VetSystem
"""
        EmailNotificationService._safe_send_mail(subject, message, [cita.dueno.Correo], fail_silently=True)

    @staticmethod
    def enviar_verificacion(usuario, token, request):
        """Envía email de verificación con token."""
        link = request.build_absolute_uri(
            reverse('verificar_email', kwargs={'token': token.token})
        )
        subject = 'Verifica tu cuenta - VetSystem'
        message = f"""
Estimado/a {usuario.username},

Gracias por registrarte en VetSystem.

Para activar tu cuenta, haz clic en el siguiente enlace:
{link}

Este enlace expirará en 24 horas.

Si no solicitaste esta cuenta, ignora este mensaje.

Saludos,
Equipo VetSystem
"""
        if usuario.email:
            EmailNotificationService._safe_send_mail(subject, message, [usuario.email], fail_silently=False)

    @staticmethod
    def enviar_bienvenida(usuario):
        """Envía email de bienvenida a un nuevo usuario del sistema."""
        subject = 'Bienvenido/a a VetSystem'
        message = f"""
Estimado/a {usuario.username},

Su cuenta ha sido creada exitosamente en VetSystem.

Detalles de su cuenta:
- Usuario: {usuario.username}
- Rol: {usuario.get_rol_display()}
- Email: {usuario.email}

Si tiene alguna pregunta, contacte al administrador del sistema.

Saludos,
Equipo VetSystem
"""
        if usuario.email:
            EmailNotificationService._safe_send_mail(subject, message, [usuario.email], fail_silently=True)

    @staticmethod
    def _safe_send_mail(subject, message, recipient_list, fail_silently=True):
        """Internal helper that wraps django.core.mail.send_mail with logging.

        Returns True on success, False on failure.
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=fail_silently,
            )
            logger.info('Email sent to %s: %s', recipient_list, subject)
            return True
        except Exception as e:
            logger.exception('Failed to send email to %s: %s', recipient_list, e)
            return False
