from django.urls import path
from appli_visualisation import views

urlpatterns = [
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
