from pyexpat.errors import messages
from django.views.generic import CreateView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario
from .forms import UsuarioForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from .models import Mascotas,Duenos,Doctores,Raza,Usuario
from .forms import *
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages




# Create your views here.
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Ejemplo de uso
class UsuarioCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    login_url = 'login'
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mascotas'] = Mascotas.objects.count()
        context['total_duenos'] = Duenos.objects.count()
        context['total_doctores'] = Doctores.objects.count()
        context['total_historias'] = Historias.objects.count()
        context['historias_recientes'] = Historias.objects.order_by('-Fecha')[:5]
        context['doctores'] = Doctores.objects.all()[:5]
        context['total_razas'] = Raza.objects.count()
        return context
    

def mi_vista(request):
    return render(request, 'aplicacion/index.html', context={})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión exitosamente')
        return super().dispatch(request, *args, **kwargs)

    

class MascotaListView(ListView):
    login_url = 'login'
    model = Mascotas
    template_name = 'mascotas/mascotas_list.html'
    context_object_name = 'mascotas'
    paginate_by = 8  
    
    

class MascotaCreateView(LoginRequiredMixin,CreateView):
    model = Mascotas
    form_class = MascotasForm
    template_name = 'mascotas/mascotas_form.html'
    success_url = reverse_lazy('mascotas_list')
    def form_valid(self, form):
        messages.success(self.request, 'Mascota creada exitosamente.')
        return super().form_valid(form)

    

class MascotaUpdateView(LoginRequiredMixin,UpdateView):
    login_url = 'login'
    model = Mascotas
    form_class = MascotasForm
    template_name = 'mascotas/mascotas_form.html'
    success_url = '/mascotas/'


class MascotaDeleteView(LoginRequiredMixin,DeleteView):
    login_url = 'login'
    model = Mascotas
    success_url = '/mascotas/'
    template_name = 'mascotas/mascotas_delete.html'

    #Dueños

class DuenosListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model = Duenos
    template_name = 'duenos/duenos_list.html'
    context_object_name = 'duenos'
    ordering = ['Nombre', 'Apellido']
    paginate_by = 8  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_duenos'] = self.get_queryset().count()
        return context
    
    def get_queryset(self):
        return Duenos.objects.filter(id__isnull=False)  

class DuenosCreateView(LoginRequiredMixin,CreateView):
    login_url = 'login'
    model = Duenos
    form_class = DuenosForm
    template_name = 'duenos/duenos_create.html'
    success_url = '/duenos/duenos_list.html'

    def form_valid(self, form):
        # Guarda el formulario y muestra un mensaje de éxito
        response = super().form_valid(form)
        messages.success(self.request, 'Dueño registrado exitosamente.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al registrar el dueño. Por favor, revise los datos.')
        return super().form_invalid(form)

    

class DuenosUpdateView(LoginRequiredMixin,UpdateView):
    login_url = 'login'
    model = Duenos
    form_class = DuenosForm
    template_name = 'duenos/duenos_form.html'
    success_url = '/duenos/'


class DuenosDeleteView(LoginRequiredMixin,DeleteView):
    login_url = 'login'
    model = Duenos
    success_url = '/Duenos/'
    template_name = 'duenos/duenos_delete.html'
   

    #RAZA

class RazasListView(ListView):
     model = Raza
     template_name ='razas/razas_list.html'
     context_object_name = 'razas'
     paginate_by = 5  

class RazasCreateView(LoginRequiredMixin,CreateView):
    login_url = 'login'
    model = Raza
    form_class = RazaForm
    template_name = 'razas/razas_create.html'
    success_url = '/razas/'

    

class RazasUpdateView(LoginRequiredMixin,UpdateView):
    login_url = 'login'
    model = Raza
    form_class = RazaForm
    template_name = 'razas/razas_form.html'
    success_url = '/razas/'


class RazasDeleteView(LoginRequiredMixin,DeleteView):
    login_url = 'login'
    model = Raza
    success_url = '/razas/'
    template_name = 'razas/razas_delete.html'

    

    #DOCTORES


class DoctoresListView(LoginRequiredMixin, ListView):
    model = Doctores
    template_name = 'doctores/doctores_list.html'
    context_object_name = 'doctores'
    ordering = ['Nombre', 'Apellido']
    paginate_by = 6  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_doctores'] = self.get_queryset().count()
        return context




class DoctoresCreateView(LoginRequiredMixin,CreateView):
    login_url = 'login'
    model = Doctores
    form_class = DoctoresForm
    template_name = 'doctores/doctores_create.html'
    success_url = '/doctores/'


class DoctoresUpdateView(LoginRequiredMixin,UpdateView):
    login_url = 'login'
    model = Doctores
    form_class = DoctoresForm
    template_name = 'doctores/doctores_form.html'
    success_url = '/doctores/'


class DoctoresDeleteView(LoginRequiredMixin,DeleteView):
    login_url = 'login'
    model = Doctores
    success_url = '/doctores/'
    template_name = 'doctores/doctores_delete.html'

    #HISTORIAS
class HistoriaListView(ListView):
    model = Historias
    template_name = 'historias/historia_list.html'
    context_object_name = 'historias'
    ordering = ['-Fecha']  # Ordenar por fecha, las más recientes primero
    paginate_by = 5


class HistoriaDetailView(LoginRequiredMixin,DetailView):
    login_url = 'login'
    model = Historias
    template_name = 'historias/historia_detail.html'
    context_object_name = 'historia'

    def form_valid(self, form):  
        messages.success(self.request, 'Historia clínica creada exitosamente.')
        return super().form_valid(form)


class HistoriaCreateView(LoginRequiredMixin,CreateView):
    login_url = 'login'
    model = Historias
    form_class = HistoriasForm
    template_name = 'historias/historia_form.html'
    success_url = reverse_lazy('historia_list')

    def form_valid(self, form):
        messages.success(self.request, 'Historia clínica creada exitosamente.')
        return super().form_valid(form)

class HistoriaUpdateView(LoginRequiredMixin,UpdateView):
    login_url = 'login'
    model = Historias
    form_class = HistoriasForm
    template_name = 'historias/historia_form.html'
    success_url = reverse_lazy('historia_list')

    def form_valid(self, form):
        messages.success(self.request, 'Historia clínica actualizada exitosamente.')
        return super().form_valid(form)

class HistoriaDeleteView(LoginRequiredMixin,DeleteView):
    login_url = 'login'
    model = Historias
    template_name = 'historias/historia_delete.html'
    success_url = reverse_lazy('historia_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Historia clínica eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
    

