from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import MovieForm, ReviewForm, ProfileForm, ReviewCommentForm, ProfileEditForm # importamos
from .models import Movie, Review, Profile, ReviewComment, Watchlist
from django.contrib.auth.decorators import login_required
import requests
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
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view.html')
    else:
        form = ProfileEditForm(instance=profile)
    
    context = {
        'form': form,
    }
    return render(request, 'profile_edit.html', context)

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
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = movie.review_set.all()

    if request.method == 'POST':
        # Procesar el formulario de comentario
        comment_form = ReviewCommentForm(request.POST)
        if comment_form.is_valid():
            review_id = request.POST.get('review_id')
            review = get_object_or_404(Review, id=review_id)
            comment = comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
            return redirect('movie_detail', movie_id=movie.id)
    else:
        comment_form = ReviewCommentForm()

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'comment_form': comment_form,
    })
@login_required
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'movie_list.html', {'movies': movies})

@login_required
def add_review(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            return redirect('movie_detail', movie_id=movie.id)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'movie': movie})

@login_required
def delete_review(request, review_id):
    review = Review.objects.get(id=review_id)
    if request.user == review.user:
        review.delete()
    return redirect('movie_detail', movie_id=review.movie.id)

@login_required
def home(request):
    peliculas_paginadas, total_pages = buscar_peliculas(request)  # Obtener la página de películas y el total de páginas
    reviews = Review.objects.all().order_by('-created_at')[:5]  # Obtener las 5 reseñas más recientes
    movies = Movie.objects.all()

    # Recortar el resumen (overview) de cada película
    for pelicula in peliculas_paginadas.object_list:
        overview = pelicula.get("overview", "")
        palabras = overview.split()[:15]  # Tomar solo las primeras 15 palabras
        pelicula["overview"] = " ".join(palabras) + ("..." if len(palabras) == 15 else "")

    return render(request, 'home.html', {
        'reviews': reviews,
        'movies': movies,
        'peliculas': peliculas_paginadas,
        'total_pages': total_pages,
    })

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id)
    if request.user != comment.user:
        return redirect('movie_detail', movie_id=comment.review.movie.id)  # Solo el autor puede editar

    if request.method == 'POST':
        form = ReviewCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('movie_detail', movie_id=comment.review.movie.id)
    else:
        form = ReviewCommentForm(instance=comment)

    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id)
    if request.user != comment.user:
        return redirect('movie_detail', movie_id=comment.review.movie.id)  # Solo el autor puede eliminar

    comment.delete()
    return redirect('movie_detail', movie_id=comment.review.movie.id)

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
    api_key = 'b6f1fef99f002dae65b72f8d52ab7c0f'  # Reemplaza con tu API Key de TMDb
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

    return peliculas_paginadas, total_pages  # Devuelve los valores necesarios
@login_required
def add_to_watchlist(request, movie_id):
    if request.method == 'POST':
        api_key = 'b6f1fef99f002dae65b72f8d52ab7c0f'  # Reemplaza con tu API Key de TMDb
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