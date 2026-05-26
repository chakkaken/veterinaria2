from django.conf import settings
from django.views.generic import (
    CreateView, TemplateView, ListView, DetailView,
    UpdateView, DeleteView
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect

from .models import Mascotas, Duenos, Doctores, Raza, Usuario, Historias, Especialidades, Citas, VerificationToken
from .forms import (
    UsuarioCreationForm, UsuarioChangeForm, UsuarioNuevoForm, UsuarioForm, MascotasForm, DuenosForm, DoctoresForm,
    EspecialidadesForm, HistoriasForm, RazaForm, CitasForm
)
from .services.email_service import EmailNotificationService
from .services.report_service import ReportService
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Count
from django.db.models.deletion import ProtectedError


# ─── Mixins ───────────────────────────────────────────────────────────────────

class StaffRequiredMixin(UserPassesTestMixin):
    """Restringe el acceso solo a usuarios con is_staff=True."""
    def test_func(self):
        return self.request.user.is_staff


class VeterinarioRequiredMixin(UserPassesTestMixin):
    """Restringe el acceso a veterinarios o admins."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.rol in ['admin', 'veterinario']


class RecepcionistaRequiredMixin(UserPassesTestMixin):
    """Permite acceso a recepcionistas, veterinarios y admins."""
    def test_func(self):
        return self.request.user.is_authenticated


# ─── Autenticación ────────────────────────────────────────────────────────────

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)


# ─── Página Principal ──────────────────────────────────────────────────────────

class IndexView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        # Si el usuario está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mascotas'] = Mascotas.objects.count()
        context['total_duenos'] = Duenos.objects.count()
        context['total_doctores'] = Doctores.objects.count()
        context['total_historias'] = Historias.objects.count()
        context['total_razas'] = Raza.objects.count()
        context['total_citas'] = Citas.objects.count()
        context['citas_pendientes'] = Citas.objects.filter(estado='pendiente').count()
        # BUGFIX: se añadió select_related para evitar N+1 queries
        context['historias_recientes'] = Historias.objects.select_related(
            'mascota', 'doctor'
        ).order_by('-Fecha')[:5]
        context['citas_proximas'] = Citas.objects.select_related(
            'mascota', 'doctor', 'dueno'
        ).filter(estado__in=['pendiente', 'confirmada']).order_by('fecha_cita')[:5]
        context['doctores'] = Doctores.objects.select_related('Especialidad').all()[:5]
        return context


# ─── Mascotas ─────────────────────────────────────────────────────────────────

class MascotasPublicListView(ListView):
    """Vista pública de mascotas sin autenticación - solo lectura"""
    model = Mascotas
    template_name = 'mascotas/mascotas_list.html'
    context_object_name = 'mascotas'
    paginate_by = 8

    def get_queryset(self):
        return Mascotas.objects.select_related('dueno', 'raza').all()


class MascotaListView(LoginRequiredMixin, ListView):
    # BUGFIX: faltaba LoginRequiredMixin — cualquiera podía ver las mascotas
    login_url = 'login'
    model = Mascotas
    template_name = 'mascotas/mascotas_list.html'
    context_object_name = 'mascotas'
    paginate_by = 8

    def get_queryset(self):
        return Mascotas.objects.select_related('dueno', 'raza').all()


class MascotaCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Mascotas
    form_class = MascotasForm
    template_name = 'mascotas/mascotas_form.html'
    success_url = reverse_lazy('mascotas_list')

    def form_valid(self, form):
        messages.success(self.request, 'Mascota creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la mascota. Revise los datos.')
        return super().form_invalid(form)


class MascotaUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Mascotas
    form_class = MascotasForm
    template_name = 'mascotas/mascotas_form.html'
    success_url = reverse_lazy('mascotas_list')

    def form_valid(self, form):
        messages.success(self.request, 'Mascota actualizada exitosamente.')
        return super().form_valid(form)


class MascotaDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Mascotas
    template_name = 'mascotas/mascotas_delete.html'
    success_url = reverse_lazy('mascotas_list')

    def form_valid(self, form):
        messages.success(self.request, 'Mascota eliminada exitosamente.')
        return super().form_valid(form)


# ─── Dueños ───────────────────────────────────────────────────────────────────

class DuenosListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Duenos
    template_name = 'duenos/duenos_list.html'
    context_object_name = 'duenos'
    ordering = ['Nombre', 'Apellido']
    paginate_by = 8

    def get_queryset(self):
        # BUGFIX: el filtro anterior usaba 'id' (minúscula) que no existe en el modelo
        return Duenos.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_duenos'] = Duenos.objects.count()
        return context


class DuenosCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Duenos
    form_class = DuenosForm
    template_name = 'duenos/duenos_create.html'
    success_url = reverse_lazy('duenos_list')

    def form_valid(self, form):
        messages.success(self.request, 'Dueño registrado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al registrar el dueño. Por favor, revise los datos.')
        return super().form_invalid(form)


class DuenosUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Duenos
    form_class = DuenosForm
    template_name = 'duenos/duenos_form.html'
    success_url = reverse_lazy('duenos_list')

    def form_valid(self, form):
        messages.success(self.request, 'Dueño actualizado exitosamente.')
        return super().form_valid(form)


class DuenosDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Duenos
    template_name = 'duenos/duenos_delete.html'
    # BUGFIX: success_url tenía '/Duenos/' con mayúscula (URL incorrecta)
    success_url = reverse_lazy('duenos_list')

    def form_valid(self, form):
        messages.success(self.request, 'Dueño eliminado exitosamente.')
        return super().form_valid(form)


# ─── Razas ────────────────────────────────────────────────────────────────────

class RazasListView(LoginRequiredMixin, ListView):
    # BUGFIX: faltaba LoginRequiredMixin
    login_url = 'login'
    model = Raza
    template_name = 'razas/razas_list.html'
    context_object_name = 'razas'
    paginate_by = 5


class RazasCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Raza
    form_class = RazaForm
    template_name = 'razas/razas_create.html'
    success_url = reverse_lazy('razas_list')

    def form_valid(self, form):
        messages.success(self.request, 'Raza creada exitosamente.')
        return super().form_valid(form)


class RazasUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Raza
    form_class = RazaForm
    template_name = 'razas/razas_form.html'
    success_url = reverse_lazy('razas_list')

    def form_valid(self, form):
        messages.success(self.request, 'Raza actualizada exitosamente.')
        return super().form_valid(form)


class RazasDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Raza
    template_name = 'razas/razas_delete.html'
    success_url = reverse_lazy('razas_list')

    def form_valid(self, form):
        try:
            messages.success(self.request, 'Raza eliminada exitosamente.')
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, 'No se puede eliminar la raza porque está asociada a una o más mascotas.')
            return redirect(self.success_url)


# ─── Doctores ─────────────────────────────────────────────────────────────────

class DoctoresListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Doctores
    template_name = 'doctores/doctores_list.html'
    context_object_name = 'doctores'
    ordering = ['Nombre', 'Apellido']
    paginate_by = 6

    def get_queryset(self):
        return Doctores.objects.select_related('Especialidad').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_doctores'] = Doctores.objects.count()
        return context


class DoctoresCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Doctores
    form_class = DoctoresForm
    template_name = 'doctores/doctores_create.html'
    success_url = reverse_lazy('doctores_list')

    def form_valid(self, form):
        messages.success(self.request, 'Doctor registrado exitosamente.')
        return super().form_valid(form)


class DoctoresUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Doctores
    form_class = DoctoresForm
    template_name = 'doctores/doctores_form.html'
    success_url = reverse_lazy('doctores_list')

    def form_valid(self, form):
        messages.success(self.request, 'Doctor actualizado exitosamente.')
        return super().form_valid(form)


class DoctoresDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Doctores
    template_name = 'doctores/doctores_delete.html'
    success_url = reverse_lazy('doctores_list')

    def form_valid(self, form):
        messages.success(self.request, 'Doctor eliminado exitosamente.')
        return super().form_valid(form)


# ─── Historias Clínicas ───────────────────────────────────────────────────────

class HistoriaListView(LoginRequiredMixin, RecepcionistaRequiredMixin, ListView):
    login_url = 'login'
    model = Historias
    template_name = 'historias/historia_list.html'
    context_object_name = 'historias'
    paginate_by = 5

    def get_queryset(self):
        queryset = Historias.objects.select_related('mascota', 'doctor').order_by('-Fecha')
        
        campo_busqueda = self.request.GET.get('campo_busqueda', '')
        termino = self.request.GET.get('termino', '').strip()
        
        if termino and campo_busqueda:
            if campo_busqueda == 'numero_historia':
                queryset = queryset.filter(numero_historia__icontains=termino)
            elif campo_busqueda == 'doctor':
                queryset = queryset.filter(
                    doctor__Nombre__icontains=termino
                ) | queryset.filter(
                    doctor__Apellido__icontains=termino
                )
            elif campo_busqueda == 'mascota':
                queryset = queryset.filter(mascota__nombre__icontains=termino)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campo_busqueda'] = self.request.GET.get('campo_busqueda', '')
        context['termino'] = self.request.GET.get('termino', '')
        return context


class HistoriaDetailView(LoginRequiredMixin, RecepcionistaRequiredMixin, DetailView):
    login_url = 'login'
    model = Historias
    template_name = 'historias/historia_detail.html'
    context_object_name = 'historia'

    def get_queryset(self):
        return Historias.objects.select_related('mascota', 'doctor')


class HistoriaCreateView(LoginRequiredMixin, RecepcionistaRequiredMixin, CreateView):
    login_url = 'login'
    model = Historias
    form_class = HistoriasForm
    template_name = 'historias/historia_form.html'
    success_url = reverse_lazy('historia_list')

    def form_valid(self, form):
        messages.success(self.request, 'Historia clínica creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la historia. Revise los datos.')
        return super().form_invalid(form)


class HistoriaUpdateView(LoginRequiredMixin, RecepcionistaRequiredMixin, UpdateView):
    login_url = 'login'
    model = Historias
    form_class = HistoriasForm
    template_name = 'historias/historia_form.html'
    success_url = reverse_lazy('historia_list')

    def form_valid(self, form):
        messages.success(self.request, 'Historia clínica actualizada exitosamente.')
        return super().form_valid(form)


class HistoriaDeleteView(LoginRequiredMixin, RecepcionistaRequiredMixin, DeleteView):
    login_url = 'login'
    model = Historias
    template_name = 'historias/historia_delete.html'
    success_url = reverse_lazy('historia_list')

    def form_valid(self, form):
        messages.success(self.request, 'Historia clínica eliminada exitosamente.')
        return super().form_valid(form)


# ─── Usuario ──────────────────────────────────────────────────────────────────

class UsuarioCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    login_url = 'login'
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el usuario. Revise los datos.')
        return super().form_invalid(form)


class UsuarioListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    login_url = 'login'
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10


class UsuarioUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    login_url = 'login'
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)


class UsuarioDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    login_url = 'login'
    model = Usuario
    template_name = 'usuarios/usuario_delete.html'
    success_url = reverse_lazy('usuario_list')

    def dispatch(self, request, *args, **kwargs):
        usuario_a_eliminar = self.get_object()

        if usuario_a_eliminar.username == 'admin':
            messages.error(request, 'No se puede eliminar el administrador principal.')
            return redirect(self.success_url)

        if request.user.username != 'admin' and usuario_a_eliminar.rol == 'admin':
            messages.error(request, 'Solo el administrador principal puede eliminar administradores.')
            return redirect(self.success_url)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Usuario eliminado exitosamente.')
        return super().form_valid(form)


class UsuarioNuevoCreateView(CreateView):
    model = Usuario
    form_class = UsuarioNuevoForm
    template_name = 'usuarios/usuario_nuevo.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.is_active = False
                self.object.save()
                form.save_m2m()

                token = VerificationToken.objects.create(usuario=self.object)

            try:
                EmailNotificationService.enviar_verificacion(self.object, token, self.request)
                messages.success(
                    self.request,
                    'Cuenta creada. Hemos enviado un enlace de verificación a tu correo electrónico.'
                )
            except Exception:
                messages.success(
                    self.request,
                    'Cuenta creada. Por favor contacta al administrador para activar tu cuenta.'
                )

            return HttpResponseRedirect(self.success_url)

        except Exception as e:
            messages.error(
                self.request,
                f'Error al crear la cuenta: {e}'
            )
            return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el usuario. Revise los datos.')
        return super().form_invalid(form)


# ─── Verificación de Email ───────────────────────────────────────────────────

class VerificarEmailView(TemplateView):
    template_name = 'registration/verificar_email.html'

    def get(self, request, *args, **kwargs):
        token_str = kwargs.get('token')
        try:
            token = VerificationToken.objects.get(token=token_str)
        except VerificationToken.DoesNotExist:
            return render(request, self.template_name, {'valido': False, 'expirado': False}, status=400)

        if token.is_expired:
            return render(request, self.template_name, {'valido': False, 'expirado': True}, status=400)

        usuario = token.usuario
        usuario.is_active = True
        usuario.is_verified = True
        usuario.save()

        token.delete()

        return render(request, self.template_name, {'valido': True})


# ─── Citas ────────────────────────────────────────────────────────────────────

class CitasListView(LoginRequiredMixin, RecepcionistaRequiredMixin, ListView):
    login_url = 'login'
    model = Citas
    template_name = 'citas/citas_list.html'
    context_object_name = 'citas'
    paginate_by = 10

    def get_queryset(self):
        return Citas.objects.select_related('mascota', 'doctor', 'dueno').order_by('-fecha_cita')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_citas'] = Citas.objects.count()
        context['citas_pendientes'] = Citas.objects.filter(estado='pendiente').count()
        context['citas_confirmadas'] = Citas.objects.filter(estado='confirmada').count()
        return context


class CitasDetailView(LoginRequiredMixin, RecepcionistaRequiredMixin, DetailView):
    login_url = 'login'
    model = Citas
    template_name = 'citas/citas_detail.html'
    context_object_name = 'cita'

    def get_queryset(self):
        return Citas.objects.select_related('mascota', 'doctor', 'dueno')


class CitasCreateView(LoginRequiredMixin, RecepcionistaRequiredMixin, CreateView):
    login_url = 'login'
    model = Citas
    form_class = CitasForm
    template_name = 'citas/citas_form.html'
    success_url = reverse_lazy('citas_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        cita = self.object
        
        try:
            EmailNotificationService.enviar_confirmacion_cita(cita)
            messages.success(self.request, 'Cita agendada exitosamente. Email de confirmación enviado.')
        except Exception:
            messages.success(self.request, 'Cita agendada exitosamente.')
        
        return response


class CitasUpdateView(LoginRequiredMixin, RecepcionistaRequiredMixin, UpdateView):
    login_url = 'login'
    model = Citas
    form_class = CitasForm
    template_name = 'citas/citas_form.html'
    success_url = reverse_lazy('citas_list')

    def form_valid(self, form):
        cita = self.get_object()
        estado_anterior = cita.estado
        
        response = super().form_valid(form)
        cita = self.object
        
        if cita.estado != estado_anterior:
            try:
                EmailNotificationService.enviar_cambio_estado_cita(cita, estado_anterior)
                messages.success(self.request, 'Cita actualizada exitosamente. Email de notificación enviado.')
            except Exception:
                messages.success(self.request, 'Cita actualizada exitosamente.')
        else:
            messages.success(self.request, 'Cita actualizada exitosamente.')
        
        return response


class CitasDeleteView(LoginRequiredMixin, RecepcionistaRequiredMixin, DeleteView):
    login_url = 'login'
    model = Citas
    template_name = 'citas/citas_delete.html'
    success_url = reverse_lazy('citas_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cita cancelada exitosamente.')
        return super().form_valid(form)


# ─── Reportes ─────────────────────────────────────────────────────────────────

class ReportesView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'reportes/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = ReportService.get_estadisticas_generales()
        context['citas_por_estado'] = ReportService.get_citas_por_estado()
        context['citas_por_doctor'] = ReportService.get_citas_por_doctor()
        context['top_mascotas'] = ReportService.get_top_mascotas_frecuentes()
        return context


class ReporteCitasPDFView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Citas
    template_name = None

    def get_queryset(self):
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        
        queryset = Citas.objects.select_related('mascota', 'doctor', 'dueno').order_by('-fecha_cita')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_cita__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_cita__lte=fecha_fin)
        
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        titulo = 'Reporte de Citas'
        
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            titulo = f'Citas del {fecha_inicio} al {fecha_fin}'
        
        pdf = ReportService.generar_pdf_citas(self.object_list, titulo)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_citas_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response


class ReporteEstadisticasPDFView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Citas
    template_name = None

    def get(self, request, *args, **kwargs):
        pdf = ReportService.generar_pdf_estadisticas()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="estadisticas_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response


class ReporteCitasCSVView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Citas
    template_name = None

    def get_queryset(self):
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        
        queryset = Citas.objects.select_related('mascota', 'doctor', 'dueno').order_by('-fecha_cita')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_cita__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_cita__lte=fecha_fin)
        
        return queryset

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        csv_data = ReportService.generar_csv_citas(self.object_list)
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="citas_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response


class ReporteMascotasCSVView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Mascotas
    template_name = None

    def get(self, request, *args, **kwargs):
        csv_data = ReportService.generar_csv_mascotas()
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="mascotas_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response


class ReporteDuenosCSVView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Duenos
    template_name = None

    def get(self, request, *args, **kwargs):
        csv_data = ReportService.generar_csv_duenos()
        
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="duenos_{datetime.now().strftime("%Y%m%d")}.csv"'
        return response