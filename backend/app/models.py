from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
# Create your models here.

class Paciente(models.Model):
    Nome = models.CharField(max_length=100, blank=False, null=True)
    Email = models.CharField(max_length=100, blank=False, null=True)
    Data_cadastro = models.DateField(blank=False, null=True)
    Data_Nascimento = models.DateField(blank=False, null=True)
    Estado_civil = models.CharField(max_length=100, blank=False, null=True)
    Grupo = models.CharField(max_length=100, blank=False, null=True)
    Situacao_atual = models.CharField(max_length=100, blank=False, null=True)
    observacoes= models.CharField(max_length=256, blank=False, null=True)
    genero = models.CharField(max_length=100, blank=False, null=True)
    celular = models.CharField(max_length=20, blank=False, null=True)
    clinica = models.CharField(max_length=100, blank=False, null=True)
    local_nascimento = models.CharField(max_length=100, blank=False, null=True)
    CPF = models.CharField(max_length=100, blank=False, null=True)
    RG = models.CharField(max_length=100, blank=False, null=True)
    Orgao_emissor = models.CharField(max_length=100, blank=False, null=True)
    Convenio = models.CharField(max_length=100, blank=False, null=True)
    Plano = models.CharField(max_length=100, blank=False, null=True)
    Data_adesao = models.DateField(blank=False, null=True)
    Nome_pai = models.CharField(max_length=100, blank=True, null=True)
    CPF_pai = models.CharField(max_length=100, blank=True, null=True)
    RG_pai = models.CharField(max_length=100, blank=True, null=True)
    Telefone_pai = models.CharField(max_length=100, blank=True, null=True)
    Nome_mae = models.CharField(max_length=100, blank=True, null=True)
    Cpf_mae = models.CharField(max_length=100, blank=True, null=True)
    Rg_mae = models.CharField(max_length=100, blank=True, null=True)
    Telefone_mae=models.CharField(max_length=100, blank=True, null=True)
    CEP=models.IntegerField(blank=False, null=True)
    Endereco = models.CharField(max_length=100, blank=False, null=True)
    Numero = models.IntegerField(blank=False, null=True)
    Complemento = models.CharField(max_length=100, blank=False, null=True)
    Bairro = models.CharField(max_length=100, blank=False, null=True)
    Cidade = models.CharField(max_length=100, blank=False, null=True)
    Estado = models.CharField(max_length=100, blank=False, null=True)
    def __str__(self):
        return '{}'.format(self.Nome, self.id)
    
class Block(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    id_bloco = models.IntegerField()
    color = models.CharField(max_length=7, default='#cccccc')
    clicks = models.PositiveIntegerField(default=0)

class Cadeira(models.Model):
    nome=models.CharField(max_length=100, blank=True, null=True)
class Agendar(models.Model):
    horario=models.DateTimeField()
    paciente=models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    duracao=models.IntegerField(blank=True, null=True)
    dentista=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cadeira=models.ForeignKey(Cadeira, on_delete=models.SET_NULL, null=True)
    confirmacao=models.CharField(max_length=100, blank=True, null=True)

class EventAbstract(models.Model):
    """ Event abstract model """

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
class EventManager(models.Manager):
    """ Event manager """

    def get_all_events(self, user):
        events = Event.objects.filter(user=user, is_active=True, is_deleted=False)
        return events

    def get_running_events(self, user):
        running_events = Event.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False,
            end_time__gte=datetime.now().date(),
        ).order_by("start_time")
        return running_events


class Event(EventAbstract):
    """ Event model """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="events", blank=True, null=True)

    objects = EventManager()
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("calendarapp:event-detail", args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse("calendarapp:event-detail", args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
    
class EventMember(EventAbstract):
    """ Event member model """

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="events")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_members"
    )

    class Meta:
        unique_together = ["event", "user"]

    def __str__(self):
        return str(self.user)
    
class EventAbstract(models.Model):
    """ Event abstract model """

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Anotacao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='anotacoes')
    texto = models.TextField()
    data_criacao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Anotação de {self.paciente.nome} - {self.data_criacao}'
    
class Odontograma(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/img', blank=True, null=True)

    def __str__(self):
        return f"Odontograma de {self.paciente.nome}"
    
class Financeiro(models.Model):
    descricao=models.CharField(max_length=200)
    paciente=models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True)
    valor=models.DecimalField(max_digits=10, decimal_places=2)
    tipo=models.CharField(max_length=8)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_de_cobranca=models.DateField(default=timezone.now)
    parcelas = models.IntegerField(null=True, blank=True)
    numero_parcela = models.PositiveIntegerField()
    status=models.CharField(max_length=20, default='Pendente')
    codigo_receita = models.CharField(max_length=4, default='1708')  # Exemplo: IRPJ
    
    def __str__(self):
        return f"{self.descricao}"

class PDFUpload(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='pdfs/')  # Armazena PDFs na pasta 'pdfs'
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paciente.nome} - {self.pdf_file.name}"
    
