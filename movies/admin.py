from django.contrib import admin
from .models import Movie, Review

# Registra los modelos para que aparezcan en el panel de administración
admin.site.register(Movie)
admin.site.register(Review)