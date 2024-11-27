from django.forms import ModelForm, DateInput
from app.models import EventMember, Event, Paciente, Anotacao, Odontograma, Block, PDFUpload, Financeiro
from django import forms


class FinanceiroForm(forms.ModelForm):
    class Meta:
        model = Financeiro
        fields = ['descricao', 'paciente', 'valor', 'tipo', 'data_de_cobranca', 'parcelas']
        widgets = {
            'data_de_cobranca': forms.DateInput(attrs={'type': 'date'}),
        }
        
class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_time", "end_time", "paciente"]
        # datetime-local is a HTML5 input type
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Insira o titulo da consulta"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Insira a descrição da consulta",
                }
            ),
            "start_time": DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "paciente": forms.Select(
                attrs={"class": "form-control"}
            )
        }
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields["start_time"].input_formats = ("%Y-%m-%dT%H:%M",)
        self.fields["end_time"].input_formats = ("%Y-%m-%dT%H:%M",)


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = EventMember
        fields = ["user"]

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'  # Inclui todos os campos do modelo
        widgets = {
            'Data_cadastro': forms.DateInput(attrs={'type': 'date'}),
            'Data_Nascimento': forms.DateInput(attrs={'type': 'date'}),
            'Data_adesao': forms.DateInput(attrs={'type': 'date'}),
        }

class AnotacaoForm(forms.ModelForm):
    class Meta:
        model = Anotacao
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Digite sua anotação aqui...'}),
        }

class DenteForm(forms.ModelForm):
    OPCOES = [
        ('opcao1', 'Opção 1'),
        ('opcao2', 'Opção 2'),
        ('opcao3', 'Opção 3'),
        ('opcao4', 'Opção 4'),
        ('opcao5', 'Opção 5'),
    ]

    dente1 = forms.ChoiceField(choices=OPCOES, required=False)
    dente2 = forms.ChoiceField(choices=OPCOES, required=False)
    dente3 = forms.ChoiceField(choices=OPCOES, required=False)
    dente4 = forms.ChoiceField(choices=OPCOES, required=False)
    dente5 = forms.ChoiceField(choices=OPCOES, required=False)
    dente6 = forms.ChoiceField(choices=OPCOES, required=False)
    dente7 = forms.ChoiceField(choices=OPCOES, required=False)
    dente8 = forms.ChoiceField(choices=OPCOES, required=False)
    dente9 = forms.ChoiceField(choices=OPCOES, required=False)
    dente10 = forms.ChoiceField(choices=OPCOES, required=False)
    dente11 = forms.ChoiceField(choices=OPCOES, required=False)
    dente12 = forms.ChoiceField(choices=OPCOES, required=False)
    dente13 = forms.ChoiceField(choices=OPCOES, required=False)
    dente14 = forms.ChoiceField(choices=OPCOES, required=False)
    dente15 = forms.ChoiceField(choices=OPCOES, required=False)
    dente16 = forms.ChoiceField(choices=OPCOES, required=False)
    dente17 = forms.ChoiceField(choices=OPCOES, required=False)
    dente18 = forms.ChoiceField(choices=OPCOES, required=False)
    dente19 = forms.ChoiceField(choices=OPCOES, required=False)
    dente20 = forms.ChoiceField(choices=OPCOES, required=False)
    dente21 = forms.ChoiceField(choices=OPCOES, required=False)
    dente22 = forms.ChoiceField(choices=OPCOES, required=False)
    dente23 = forms.ChoiceField(choices=OPCOES, required=False)
    dente24 = forms.ChoiceField(choices=OPCOES, required=False)
    dente25 = forms.ChoiceField(choices=OPCOES, required=False)
    dente26 = forms.ChoiceField(choices=OPCOES, required=False)
    dente27 = forms.ChoiceField(choices=OPCOES, required=False)
    dente28 = forms.ChoiceField(choices=OPCOES, required=False)
    dente29 = forms.ChoiceField(choices=OPCOES, required=False)
    dente30 = forms.ChoiceField(choices=OPCOES, required=False)
    dente31 = forms.ChoiceField(choices=OPCOES, required=False)
    dente32 = forms.ChoiceField(choices=OPCOES, required=False)

    class Meta:
        model = Odontograma
        fields = '__all__'  # Inclui todos os campos do modelo  # Inclui todos os campos do modelo
        

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = []

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFUpload
        fields = ['pdf_file']