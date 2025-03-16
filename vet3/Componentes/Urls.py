from django.contrib import admin
   
from django.urls import path

from . import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, DashboardView, CustomLogoutView
from django.contrib.auth import views as auth_views
from .views import (
    # Mascotas
    MascotaListView, MascotaCreateView, MascotaUpdateView, MascotaDeleteView,
    # Dueños
    DuenosListView, DuenosCreateView, DuenosUpdateView, DuenosDeleteView,
    # Razas
    RazasListView, RazasCreateView, RazasUpdateView, RazasDeleteView,
    # Doctores
    DoctoresListView, DoctoresCreateView, DoctoresUpdateView, DoctoresDeleteView,
  #Historias
    HistoriaCreateView, HistoriaDetailView, Historias, HistoriasForm, HistoriaUpdateView,HistoriaListView,HistoriaDeleteView
)

 
urlpatterns = [
     path('admin/', admin.site.urls),
     path('', DashboardView.as_view(), name='dashboard'),
     path('index/', CustomLogoutView.as_view(), name='index'),  
   
     path('login/', auth_views.LoginView.as_view(), name='login'),
     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('mascotas/', MascotaListView.as_view(), name='mascotas_list'),
    path('mascotas/crear/', views.MascotaCreateView.as_view(), name='mascotas_create'),
    path('mascotas/<int:pk>/editar/', views.MascotaUpdateView.as_view(), name='mascotas_form'),
    path('mascotas/<int:pk>/eliminar/', views.MascotaDeleteView.as_view(), name='mascotas_delete'),

      # URLs para Dueños
    path('duenos/', views.DuenosListView.as_view(), name='duenos_list'),
    path('duenos/crear/', views.DuenosCreateView.as_view(), name='duenos_create'),
    path('duenos/<int:pk>/editar/', views.DuenosUpdateView.as_view(), name='duenos_update'),
    path('duenos/<int:pk>/eliminar/', views.DuenosDeleteView.as_view(), name='duenos_delete'),

    # URLs para Raza
    path('razas/', views.RazasListView.as_view(), name='razas_list'),
    path('razas/crear/', views.RazasCreateView.as_view(), name='razas_create'),
    path('razas/<int:pk>/editar/', views.RazasUpdateView.as_view(), name='razas_form'),
    path('razas/<int:pk>/eliminar/', views.RazasDeleteView.as_view(), name='razas_delete'),

    # URLs para Doctores
    path('doctores/', views.DoctoresListView.as_view(), name='doctores_list'),
    path('doctores/crear/', views.DoctoresCreateView.as_view(), name='doctores_create'),
    path('doctores/<int:pk>/editar/', views.DoctoresUpdateView.as_view(), name='doctores_update'),
    path('doctores/<int:pk>/eliminar/', views.DoctoresDeleteView.as_view(), name='doctores_delete'),

    #urls Historias
    path('historias/', HistoriaListView.as_view(), name='historia_list'),
    path('historias/<int:pk>/', HistoriaDetailView.as_view(), name='historia_detail'),
    path('historias/crear/', HistoriaCreateView.as_view(), name='historia_form'),
    path('historias/<int:pk>/editar/', HistoriaUpdateView.as_view(), name='historia_update'),
    path('historias/<int:pk>/eliminar/', HistoriaDeleteView.as_view(), name='historia_delete'),

   
]
