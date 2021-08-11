from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import generics, permissions

from django.db import models
from .models import Movie, Actor
from .serializers import (
    MovieListSerializer,
    MovieDetailSerialiser,
    ReviewCreateSerializer,
    CreateRatingSerializer,
    ActorListSerializer,
    ActorDetailSerializer,
)

from .service import get_client_ip, MovieFilter

class MovieListView(generics.ListAPIView):

    """Вывод списка фильмов"""
    queryset = Movie.objects.all()
    serializer_class = MovieListSerializer
    filter_backend = (DjangoFilterBackend, )
    filterset_class = MovieFilter
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings",
                                     filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return movies

    # def get(self, request):
    #     movies = Movie.objects.filter(draft=False).annotate(
    #         rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(request)))
    #     ).annotate(
    #         middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
    #     )
    #     serializer = MovieListSerializer(movies, many=True)
    #     return Response(serializer.data)

# class MovieListView(APIView):
#     def get(self, request):
#         movies = Movie.objects.filter(draft=False)
#         serializer = MovieListSerialiser(movies, many=True)
#         return Response(serializer.data)

class MovieDetailView(APIView):
    def get(self, request, pk):
        movie = Movie.objects.get(id=pk, draft=False)
        serializer = MovieDetailSerialiser(movie)
        return Response(serializer.data)

class ReviewCreateView(generics.CreateAPIView):
    """Добавление отзыва к фильму"""
    serializer_class = ReviewCreateSerializer

class AddStarRatingView(generics.CreateAPIView):
    """Добавление рейтинга фильму"""

    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class ActorListView(generics.ListAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorListSerializer


class ActorDetailView(generics.RetrieveAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer