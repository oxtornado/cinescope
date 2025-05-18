from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('', views.home, name='home'),  # Página de inicio
    path('movie_list', views.movie_list, name='movie_list'),  # Lista de películas
    path('add/', views.add_movie, name='add_movie'),  # Agregar película
    path('movie/<int:movie_id>/add_review/', views.add_review, name='add_review'),  # Agregar reseña
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),  # Eliminar reseña
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),  # Editar comentario
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),  # Eliminar comentario
    path('register/', views.register, name='register'),  # Registro de usuarios
    path('home/', views.home, name='home'),  # Página de inicio
    path('profile/', views.profile_view, name='profile_view'),  # Perfil del usuario
    path('profile/edit/', views.profile_edit, name='profile_edit'),  # Asegúrate de que esta línea existe
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Redirige a 'home' después del logout
    path('buscar-peliculas/', views.buscar_peliculas, name='buscar_peliculas'),
    path('buscar/', views.buscar_peliculas, name='buscar_peliculas'),
    path('add_to_watchlist/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/add_review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/add_comment/', views.add_comment, name='add_comment'),
    path('reviews/<int:review_id>/edit/', views.edit_review, name='edit_review'),  # Agregar esta ruta
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),  # Agregar esta ruta
]