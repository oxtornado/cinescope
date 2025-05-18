from .forms import MovieForm, ReviewForm, ProfileForm, ReviewCommentForm, ProfileEditForm # importamos
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Movie, Review, Profile, ReviewComment, Watchlist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import Http404
import requests
import os
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente después del registro
            return redirect('home')  # Redirige a la página de inicio (home)
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirige a la página principal después del login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {'form': form})

@login_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('movie_list')  # Redirige a la lista de películas
    else:
        form = MovieForm()
    return render(request, 'add_movie.html', {'form': form})

@login_required
def movie_detail(request, movie_id):
    try:
        # Buscar la película en la base de datos local
        movie = Movie.objects.get(id=movie_id)
        reviews = Review.objects.filter(movie=movie)
    except Movie.DoesNotExist:
        # Si no existe, obtener los detalles de la película desde la API de TMDB
        api_key = os.getenv('TMDB_API_KEY')
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=es-MX'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Crear una instancia de Movie con los datos de la API
            movie = Movie(
                id=data['id'],
                title=data['title'],
                release_year=data['release_date'].split('-')[0],
                description=data['overview']
            )
            # Guardar la película en la base de datos
            movie.save()
            # Obtener las reseñas
            reviews = Review.objects.filter(movie_id=movie_id)
        else:
            # Si la API falla, redirigir a la página principal
            return redirect('home')
    
    # Si llegamos aquí, tenemos la película y las reseñas
    return render(request, 'movie_detail.html', {
        'movie': movie,
        'reviews': reviews
    })

@login_required
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})

@login_required
def home(request):
    # Obtener el número de página de la API
    api_page = request.GET.get('api_page', 1)
    
    # Obtener películas populares desde la API
    api_key = os.getenv('TMDB_API_KEY')
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=es-MX&page={api_page}&per_page=6'  # Cambiar a 6 películas por página
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        movies = data.get('results', [])
        total_pages = data.get('total_pages', 1)
    except requests.exceptions.RequestException as e:
        movies = []
        total_pages = 1
        print(f"Error al conectar con la API de TMDb: {e}")
    
    # Obtener las 5 reseñas más recientes
    reviews = Review.objects.all().order_by('-created_at')[:5]
    
    # Obtener las 5 reseñas más recientes
    latest_reviews = Review.objects.all().order_by('-id')[:5]

    # Obtener las películas más recientes
    latest_movies = Movie.objects.all().order_by('-id')[:5]
    
    context = {
        'latest_reviews': latest_reviews,
        'latest_movies': latest_movies,
        'movies': movies,
        'reviews': reviews,
        'total_pages': total_pages,
        'current_page': api_page
    }
    return render(request, 'home.html', context)


@login_required
def profile_view(request):
    profile = request.user.profile
    if profile.profile_picture and profile.profile_picture.exists():
        profile_picture_url = profile.profile_picture.url
    else:
        profile_picture_url = "https://pfpmaker.com/images/landing/headshots/features-dual-gradient.svg"
    
    context = {
        'profile': profile,
        'profile_picture_url': profile_picture_url,
    }
    return render(request, 'profile_view.html', context)

def buscar_peliculas(request):
    api_key = os.getenv('TMDB_API_KEY')  # Reemplaza con tu API Key de TMDb
    query = request.GET.get('query', '')  # Obtener la consulta de búsqueda
    page_number = request.GET.get('page', 1)  # Obtener el número de página

    if query:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=es-MX&query={query}&page={page_number}'
    else:
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=es-MX&page={page_number}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        peliculas = data.get('results', [])
        total_pages = data.get('total_pages', 1)

        paginator = Paginator(peliculas, 4)  # 4 películas por página
        try:
            peliculas_paginadas = paginator.page(page_number)
        except PageNotAnInteger:
            peliculas_paginadas = paginator.page(1)
        except EmptyPage:
            peliculas_paginadas = paginator.page(paginator.num_pages)

    except requests.exceptions.RequestException as e:
        peliculas_paginadas = []
        total_pages = 1
        print(f"Error al conectar con la API de TMDb: {e}")

    return render(request, 'buscar_peliculas.html', {
        'peliculas': peliculas_paginadas,
        'total_pages': total_pages,
        'query': query,
    })



@login_required
def add_to_watchlist(request, movie_id):
    if request.method == 'POST':
        api_key = os.getenv('TMDB_API_KEY')  # Reemplaza con tu API Key de TMDb
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=es-MX'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            Watchlist.objects.create(
                user=request.user,
                movie_id=movie_id,
                title=data['title'],
                poster_path=data['poster_path'],
            )
            return redirect('watchlist')
    return redirect('home')

@login_required
def watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    return render(request, 'watchlist.html', {'watchlist_items': watchlist_items})

def obtener_peliculas_desde_api(query='', page_number=1):
    api_key = os.getenv('TMDB_API_KEY')  # Reemplaza con tu API Key de TMDb
    if query:
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=es-MX&query={query}&page={page_number}'
    else:
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=es-MX&page={page_number}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        peliculas = data.get('results', [])
        total_pages = data.get('total_pages', 1)

        paginator = Paginator(peliculas, 4)  # 4 películas por página
        try:
            peliculas_paginadas = paginator.page(page_number)
        except PageNotAnInteger:
            peliculas_paginadas = paginator.page(1)
        except EmptyPage:
            peliculas_paginadas = paginator.page(paginator.num_pages)

    except requests.exceptions.RequestException as e:
        peliculas_paginadas = []
        total_pages = 1
        print(f"Error al conectar con la API de TMDb: {e}")

    return peliculas_paginadas, total_pages

@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        form = ReviewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.review = review
            comment.save()
            return redirect('movie_detail', movie_id=review.movie.id)
    else:
        form = ReviewCommentForm()
    return render(request, 'add_comment.html', {'form': form, 'review': review})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movie_detail', movie_id=review.movie.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reseña actualizada exitosamente')
            return redirect('movie_detail', movie_id=review.movie.id)
    else:
        form = ReviewForm(instance=review)
    
    # Pasar el objeto review y el movie_id al contexto
    context = {
        'form': form,
        'review': review,
        'movie_id': review.movie.id,  # Agregar el movie_id al contexto
        'stars': range(1, 6)
    }
    
    return render(request, 'edit_review.html', context)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    movie_id = review.movie.id
    review.delete()
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.review = review
            comment.save()
            return redirect('movie_detail', movie_id=review.movie.id)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})


@login_required
def add_review(request, movie_id):
    try:
        # Buscar la película usando el id normal
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        # Si no existe, obtener datos de la API y crearla
        api_key = os.getenv('TMDB_API_KEY')
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=es-MX'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            movie = Movie.objects.create(
                id=data['id'],  # Usar el ID de TMDB como ID de Django
                title=data.get('title', ''),
                overview=data.get('overview', ''),
                release_year=data.get('release_date', '1900').split('-')[0],
                poster_path=data.get('poster_path', '')
            )
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la API: {e}")
            messages.error(request, 'Error al obtener datos de la película')
            return redirect('home')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            messages.success(request, 'Reseña agregada exitosamente')
            return redirect('movie_detail', movie_id=movie.id)
        else:
            messages.error(request, 'Error al guardar la reseña')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'movie': movie,
        'stars': range(1, 6)  # Para mostrar las estrellas en el template
    }
    
    return render(request, 'add_review.html', context)
    
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id)
    if request.user != comment.user:
        return redirect('movie_detail', movie_id=comment.review.movie.id)
    
    if request.method == 'POST':
        form = ReviewCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario actualizado exitosamente')
            return redirect('movie_detail', movie_id=comment.review.movie.id)
    else:
        form = ReviewCommentForm(instance=comment)
    
    return render(request, 'edit_comment.html', {'form': form})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id)
    if request.user != comment.user:
        return redirect('movie_detail', movie_id=comment.review.movie.id)
    
    movie_id = comment.review.movie.id
    comment.delete()
    messages.success(request, 'Comentario eliminado exitosamente')
    return redirect('movie_detail', movie_id=movie_id)