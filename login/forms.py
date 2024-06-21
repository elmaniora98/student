# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserAccount

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget


class UserForm(UserCreationForm):

	contact = PhoneNumberField(required=True, label="Numero de Telephone", widget=PhoneNumberPrefixWidget())

	class Meta:
		model = UserAccount
		fields = ['email', 'first_name', 'last_name', 'contact'] 


class FormulaireDeModificationDuMotDePasse(forms.Form):
    mot_de_passe = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputMot_de_passe','placeholder': 'Mot de passe'}), label="Mot de passe")
    nouveau_mot_de_passe = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputNouveau_mot_de_passe','placeholder': 'Nouveau mot de passe'}), label="Nouveau mot de passe")
    confirmation_du_nouveau_mot_de_passe = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputConfirmation_du_nouveau_mot_de_passe','placeholder': 'Nouveau mot de passe'}), label="Nouveau mot de passe")

class FormulaireMotDePasseOublie(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}), label="Email")
 