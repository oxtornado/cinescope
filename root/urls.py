from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', include('movies.urls')),  # URLs de registro
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # URL de inicio de sesión
    path('movies/', include('movies.urls')),  # URLs de la aplicación movies
    path('', RedirectView.as_view(url='movies/')),  # Redirige la ruta raíz a la lista de películas
]