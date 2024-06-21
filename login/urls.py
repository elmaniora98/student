from django.urls import path

from .views import UserSignUpView, user_login, user_logout, modifier_vos_informations, mot_de_passe_oublie, modifier_votre_mot_de_passe, index

app_name = "login"

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', UserSignUpView.as_view(), name='register'),
    path('modifier_vos_informations/', modifier_vos_informations, name='modifinfos'),
    path('modifier-votre-mot-de-passe', modifier_votre_mot_de_passe, name='modifpasse'),
    path('mot-de-passe-oublie', mot_de_passe_oublie, name='passe_oublie'),
]