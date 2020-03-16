from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.loginUser, name='loginUser'),
    path('list', views.listModInstances, name='listModInstances'),
    path('view', views.viewAllRatings, name='viewAllRatings'),
    path('average/', views.averageRating, name='averageRating'),
    path('rate', views.rateProfessor, name='rateProfessor')
]
