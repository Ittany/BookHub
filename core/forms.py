from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Autor, Categoria, Libro

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombres', max_length=150, required=True)
    last_name = forms.CharField(label='Apellidos', max_length=150, required=True)
    email = forms.EmailField(label='Correo electrónico', required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username','first_name','last_name','email','password1','password2')
    def clean_email(self):
        value = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return value

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo','autor','categoria','isbn','editorial','anio','descripcion','ejemplares','portada','activo']
        widgets = {'descripcion':forms.Textarea(attrs={'rows':4})}

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
