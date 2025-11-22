from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Perfil

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu melhor email'})
    )
    password1 = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crie uma senha'}),
        help_text='Sua senha deve conter pelo menos 8 caracteres e não pode ser muito comum.'
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme sua senha'}),
        help_text='Digite a mesma senha novamente para verificação.'
    )

    class Meta:
        model = User
        fields = ('email', 'nome')
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome completo'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].required = True


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu email'})
    )
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'}),
    )
    
    error_messages = {
        'invalid_login': 'Email ou senha inválidos. Por favor, tente novamente.',
        'inactive': 'Esta conta está inativa.',
    }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'nome')
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = [
            'genero', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'telefone', 'telefone_whatsapp',
            'data_nascimento', 'foto_perfil'
        ]
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'data-mask': '00000-000'
            }),
            'logradouro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rua, avenida, etc.'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (opcional)'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'maxlength': 2,
                'style': 'text-transform: uppercase;'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'data-mask': '(00) 00000-0000'
            }),
            'telefone_whatsapp': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'data_nascimento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DD/MM/AAAA',
                'data-mask': '00/00/0000'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'genero': 'Gênero',
            'cep': 'CEP',
            'logradouro': 'Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado (UF)',
            'telefone': 'Telefone',
            'telefone_whatsapp': 'Este número tem WhatsApp?',
            'data_nascimento': 'Data de Nascimento',
            'foto_perfil': 'Foto de Perfil'
        }
        help_texts = {
            'foto_perfil': 'Envie uma imagem quadrada para melhor visualização.',
            'data_nascimento': 'Formato: DD/MM/AAAA',
            'telefone': 'Formato: (00) 00000-0000'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configura os formatos de data aceitos
        self.fields['data_nascimento'].input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']
        
        # Adiciona classes CSS adicionais
        for field_name, field in self.fields.items():
            if field_name != 'telefone_whatsapp' and field_name != 'foto_perfil':
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
                
    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')
        if not cep:
            return None  # Retorna None para campos vazios (null=True no modelo)
        
        cep = cep.replace('-', '').replace(' ', '').strip()
        if not cep:
            return None
        
        if not cep.isdigit():
            raise forms.ValidationError('CEP deve conter apenas números.')
        if len(cep) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos.')
        return cep
        
    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '')
        if not estado:
            return None  # Retorna None para campos vazios (null=True no modelo)
        
        estado = estado.strip().upper()
        if not estado:
            return None
        
        if len(estado) != 2:
            raise forms.ValidationError('O estado deve ter 2 caracteres (ex: SP, RJ).')
        return estado
        
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '')
        if not telefone:
            return None  # Retorna None para campos vazios (null=True no modelo)
        
        # Remove caracteres não numéricos
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
        
        if not telefone_limpo:
            return None  # Se não há dígitos, retorna None
        
        if len(telefone_limpo) not in [10, 11]:
            raise forms.ValidationError('Telefone deve ter 10 ou 11 dígitos (com DDD).')
        
        return telefone_limpo
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        
        # Se já é um objeto date, retorna direto
        if hasattr(data_nascimento, 'year'):
            return data_nascimento
        
        # Se é None ou string vazia, retorna None
        if not data_nascimento or (isinstance(data_nascimento, str) and not data_nascimento.strip()):
            return None
        
        # Se é uma string, tenta converter
        if isinstance(data_nascimento, str):
            from datetime import datetime
            data_str = data_nascimento.strip()
            
            if not data_str:
                return None
            
            # Tenta diferentes formatos
            formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y']
            for formato in formatos:
                try:
                    data_obj = datetime.strptime(data_str, formato).date()
                    return data_obj
                except (ValueError, AttributeError):
                    continue
            
            # Se nenhum formato funcionou, levanta erro
            raise forms.ValidationError('Formato de data inválido. Use DD/MM/AAAA.')
        
        return data_nascimento