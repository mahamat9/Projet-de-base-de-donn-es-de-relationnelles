"""Leprojet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from appli_visualisation import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('appli_visualisation/', include('appli_visualisation.urls')),
    path('', views.home, name='home'),
    path('recherche_employes/', views.search_employees, name='search_employees'),
    path('potato/', views.potato, name='potato'),
    path('employes_par_nbr/', views.employes_par_nbr, name = 'employes_par_nbr'),
    path('employee_communication/', views.employee_communication, name='employee_communication'),
    path('couples_communication/', views.couples_communication, name='couples_communication'),
    path('jours_plus_echanges/', views.jours_plus_echanges, name='jours_plus_echanges'),
    path('mots_cles/', views.mots_cles, name='mots_cles'),
    path('contenu_conversations/', views.messages_by_subject_view, name='contenu_conversations'),
    path('message/<int:message_id>/', views.message_detail_view, name='message_detail'),
]