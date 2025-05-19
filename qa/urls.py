from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    path('create/', views.create_question_answer, name='create_question_answer'),
]