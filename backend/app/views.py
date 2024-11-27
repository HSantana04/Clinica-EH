from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as login_django
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.contrib.auth.decorators import login_required
from rolepermissions.roles import assign_role
from rolepermissions.decorators import has_role_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from app.models import Paciente, Event, EventMember
from django.http import JsonResponse 
from app.forms import EventForm
from django.views import generic
from datetime import timedelta, datetime, date
from django.views.generic import ListView
from app.utils import Calendar
from django.contrib import messages
import calendar
from django.shortcuts import render, redirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from app.models import EventMember, Event, Anotacao, Odontograma, Financeiro, PDFUpload
from app.utils import Calendar
from app.forms import EventForm, AddMemberForm, PacienteForm, AnotacaoForm, DenteForm, PDFUploadForm, FinanceiroForm
from django.db.models import Count
from django.db.models.functions import TruncDay
import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile
import json
@login_required(login_url="/")
def index(request):
    # Obtém a data e hora atual
    agora = timezone.now()

    # Filtra eventos que começam após a data e hora atual e ordena por data de início
    eventos_futuros = Event.objects.filter(start_time__gt=agora).order_by('start_time')

    # Obtém todos os pacientes
    pacientes = Paciente.objects.all()
    inicio_do_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_do_dia = agora.replace(hour=23, minute=59, second=59, microsecond=999999)
    # Obtém o ano e mês atual
    ano_atual = agora.year
    mes_atual = agora.month
    eventos_hoje = Event.objects.filter(start_time__range=(inicio_do_dia, fim_do_dia)).order_by('start_time')
    # Filtra pacientes cadastrados no ano atual
    pacientes_ano_atual = Paciente.objects.filter(Data_cadastro__year=ano_atual)
    # Conta o número de pacientes cadastrados no ano atual
    total_pacientes_ano_atual = pacientes_ano_atual.count()
    
    # Filtra pacientes cadastrados no mês atual
    pacientes_mes_atual = Paciente.objects.filter(Data_cadastro__year=ano_atual, Data_cadastro__month=mes_atual)
    # Conta o número de pacientes cadastrados no mês atual
    total_pacientes_mes_atual = pacientes_mes_atual.count()
    
    # Obtém o início e o fim do dia atual
    inicio_do_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_do_dia = agora.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Filtra consultas agendadas para o dia atual
    consultas_dia_atual = Event.objects.filter(start_time__range=(inicio_do_dia, fim_do_dia))
    # Conta o número de consultas agendadas para o dia atual
    total_consultas_dia_atual = consultas_dia_atual.count()
    ultimos_eventos = Event.objects.filter(start_time__lt=agora).order_by('-start_time')[:10]

    start_of_month = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timezone.timedelta(days=31)).replace(day=1) - timezone.timedelta(seconds=1)
    consultas_por_dia = Event.objects.filter(start_time__range=(start_of_month, end_of_month)) \
                                       .annotate(data=TruncDay('start_time')) \
                                       .values('data') \
                                       .annotate(total=Count('id')) \
                                       .order_by('data')

    # Formata os dados para o gráfico
    dias = [item['data'].strftime('%Y-%m-%d') for item in consultas_por_dia]
    total_consultas = [item['total'] for item in consultas_por_dia]
    
    context = {
        'eventos_futuros': eventos_futuros,
        'pacientes': pacientes,
        'total_pacientes_ano_atual': total_pacientes_ano_atual,
        'total_pacientes_mes_atual': total_pacientes_mes_atual,
        'total_consultas_dia_atual': total_consultas_dia_atual,
        'eventos_hoje': eventos_hoje,
        'ultimos_eventos':ultimos_eventos,
        'dias': dias,
        'total_consultas': total_consultas,
    }
    
    return render(request, 'frontend/index.html', context)

@has_role_decorator('administrador')
@login_required(login_url="/")
def financeiro(request):
    if request.method == "POST":
        # Obtém dados do formulário
        descricao = request.POST.get('descricao')
        valor = float(request.POST.get('valor'))
        tipo = request.POST.get('tipo')
       
        data_de_cobranca = request.POST.get('data_de_cobranca')
        paciente_id = request.POST.get('paciente')
        parcelas = int(request.POST.get('parcelas', 1))

        # Obtém a instância do paciente
        paciente_instance = get_object_or_404(Paciente, id=paciente_id)

        # Converte a data de cobrança para um objeto datetime
        data_cobranca = datetime.strptime(data_de_cobranca, "%Y-%m-%d")

        # Calcula o valor de cada parcela
        valor_parcela = valor / parcelas

        # Cria transações para cada parcela, com a data de cobrança avançando a cada mês
        for i in range(1, parcelas + 1):
            financeiro = Financeiro(
                descricao=descricao,
                valor=valor_parcela,
                tipo=tipo,
                data_de_cobranca=data_cobranca,  # Define a data ajustada
                paciente=paciente_instance,
                usuario=request.user,
                status='Pendente',
                numero_parcela=i
            )
            financeiro.save()

            # Avança a data de cobrança em 1 mês
            data_cobranca += relativedelta(months=1)

        return redirect('financeiro')

    else:
        usuario = request.user
        # Filtra os dados financeiros do usuário logado
        dados_financeiros = Financeiro.objects.filter().order_by('-data_de_cobranca')
        pacientes = Paciente.objects.all()

        # Calcula o saldo total apenas para transações pagas
        saldo_total = 0
        for item in dados_financeiros:
            if item.status == 'Pago':
                if item.tipo == 'Entrada':
                    saldo_total += item.valor
                elif item.tipo == 'Saída':
                    saldo_total -= item.valor

        return render(request, 'frontend/financeiro.html', {
            'financeiro': dados_financeiros,
            'usuario': usuario,
            'saldo_total': saldo_total, 
            'pacientes': pacientes,  # Passa o saldo total para o template
        })

@login_required(login_url="/")
def deletar_financeiro(request, item_id):
    item = get_object_or_404(Financeiro, id=item_id, usuario=request.user)
    if request.method == "POST":
        item.delete()
        return redirect('financeiro')
    return render(request, 'frontend/confirmar_excluir_transacao.html', {'item': item})

@login_required(login_url="/")
def atualizar_status(request, item_id):
    item = get_object_or_404(Financeiro, id=item_id, usuario=request.user)
    if request.method == "POST":
        novo_status = request.POST.get('status')
        item.status = novo_status
        item.save()
        return redirect('financeiro')
    return render(request, 'frontend/financeiro.html', {'financeiro': item})

@login_required(login_url="/")
def editar_financeiro(request, item_id):
    item = get_object_or_404(Financeiro, id=item_id)

    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        tipo = request.POST.get('tipo')
        data_de_cobranca=request.POST.get('data_pagamento')
        paciente = request.POST.get('paciente')

        # Atualiza os campos do item
        item.descricao = descricao
        item.valor = valor
        item.tipo = tipo
        item.data_de_cobranca = data_de_cobranca
        item.paciente = paciente
        item.save()

        # Redireciona para a página financeira após editar
        return redirect('financeiro')
    
    return render(request, 'frontend/editar_financeiro.html', {'item': item})
def login(request):
    if request.user.is_authenticated:
        # Se o usuário já estiver autenticado, redirecione para a página inicial
        return redirect('index')
    
    if request.method == "GET":
        return render(request, 'frontend/pages-login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(username=username, password=senha)
        if user:
            login_django(request, user)
            return redirect('index')
        return redirect('login_incorreto')
    
def login_incorreto(request):
    if request.user.is_authenticated:
        # Se o usuário já estiver autenticado, redirecione para a página inicial
        return redirect('index')
    
    if request.method == "GET":
        return render(request, 'frontend/pages-login-incorreto.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(username=username, password=senha)
        if user:
            login_django(request, user)
            return redirect('index')
        return render(request, 'frontend/pages-login-incorreto.html')

@login_required(login_url="/")
@has_role_decorator('administrador')
def cadastro(request):
    if request.method == "GET":
        users = User.objects.all()
        return render(request, 'frontend/cadastro.html', {'users': users})
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        grupo = request.POST.get('grupo')


        user = User.objects.filter(username=username).first()
        if user:
            return HttpResponse("Já existe um usuário com esse nome")

        # Cria o novo usuário
        user = User.objects.create_user(username=username, email=email, password=senha)

        # Verifica se o grupo existe, se não, cria-o

        # Adiciona o usuário ao grupo
        # Salva o usuário
        user.save()
        assign_role(user, grupo)
        users = User.objects.all()
        return render(request, 'frontend/cadastro.html', {'users': users})
@login_required(login_url="/")
def calendario(request):
    return render(request, 'frontend/calendario.html')
@login_required(login_url="/")
def pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'frontend/pacientes.html', {'pacientes': pacientes})
@login_required(login_url="/")
def cadastrar_paciente(request):
    if request.method == "GET":
        pacientes = Paciente.objects.all()
        return render(request, 'frontend/cadastrar_paciente.html', {'pacientes': pacientes})
    else:
        try:
            # Pegando os dados do formulário
            nome = request.POST.get('nome')
            genero = request.POST.get('genero')
            data_cadastro = request.POST.get('data_cadastro')
            data_nascimento = request.POST.get('data_nascimento')
            observacoes = request.POST.get('observaçoes')
            local_nascimento = request.POST.get('local_nascimento')
            estado_civil = request.POST.get('estado_civil')
            grupo = request.POST.get('grupo')
            situacao_atual = request.POST.get('situacao_atual')
            celular = request.POST.get('celular')
            email = request.POST.get('email')
            cep = request.POST.get('cep')
            endereco = request.POST.get('endereço')
            numero = request.POST.get('numero')
            complemento = request.POST.get('complemento')
            bairro = request.POST.get('bairro')
            cidade = request.POST.get('cidade')
            estado = request.POST.get('Estado')
            cpf = request.POST.get('cpf')
            rg = request.POST.get('rg')
            orgao_emissor = request.POST.get('orgao_emissor')
            convenio = request.POST.get('convénio')
            plano = request.POST.get('plano')
            data_adesao = request.POST.get('data_adesao')
            nome_pai = request.POST.get('nome_pai')
            cpf_pai = request.POST.get('cpf_pai')
            rg_pai = request.POST.get('rg_pai')
            telefone_pai = request.POST.get('telefone_pai')
            nome_mae = request.POST.get('nome_mae')
            cpf_mae = request.POST.get('cpf_mae')
            rg_mae = request.POST.get('rg_mae')
            telefone_mae = request.POST.get('telefone_mae')
            
            # Validando se o paciente já existe
            if Paciente.objects.filter(Nome=nome).exists():
                raise ValidationError(f"Paciente com o nome {nome} já existe.")

            # Criando o paciente
            paciente = Paciente(
                Nome=nome,
                genero=genero,
                Data_cadastro=data_cadastro,
                Data_Nascimento=data_nascimento,
                observacoes=observacoes,
                local_nascimento=local_nascimento,
                Estado_civil=estado_civil,
                Situacao_atual=situacao_atual,
                Email=email,
                celular=celular,
                Grupo=grupo,
                CPF=cpf,
                RG=rg,
                Orgao_emissor=orgao_emissor,
                Convenio=convenio,
                Plano=plano,
                Data_adesao=data_adesao,
                Nome_pai=nome_pai,
                CPF_pai=cpf_pai,
                RG_pai=rg_pai,
                Telefone_pai=telefone_pai,
                Nome_mae=nome_mae,
                Cpf_mae=cpf_mae,
                Rg_mae=rg_mae,
                Telefone_mae=telefone_mae,
                CEP=cep,
                Endereco=endereco,
                Numero=numero,
                Complemento=complemento,
                Bairro=bairro,
                Cidade=cidade,
                Estado=estado
            )
            paciente.save()
            
            # Mensagem de sucesso
            messages.success(request, "Paciente cadastrado com sucesso!")
            return redirect('cadastrar_paciente')  # Redirecionar para evitar reenvio do formulário

        except:
            return render(request, 'frontend/erro_validacao.html')

        
    
@has_role_decorator('administrador')
@login_required(login_url="/")
def delete_paciente(request, paciente_id):
    context={}
    paciente=get_object_or_404(Paciente, id=paciente_id)
    context['object']=paciente
    if request.method == "POST":
        paciente.delete()
        return redirect('pacientes')
    return render(request, 'frontend/confirmar_excluir_paciente.html', context)

@login_required(login_url="/")
def delete_anotacao(request, paciente_id, anotacao_id):
    context = {}
    anotacao = get_object_or_404(Anotacao, id=anotacao_id, paciente_id=paciente_id)
    context['object'] = anotacao
    if request.method == "POST":
        anotacao.delete()
        return redirect('pagina_paciente', paciente_id=paciente_id)
    return render(request, 'frontend/confirmar_excluir_anotacao.html', context)

@login_required(login_url="/")
def pagina_usuario(request):
    return render(request, 'frontend/users-profile.html')

@login_required(login_url="/")
def pagina_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    eventos = Event.objects.filter(paciente=paciente)
    anotacoes = Anotacao.objects.filter(paciente=paciente)
    odontograma, _ = Odontograma.objects.get_or_create(paciente=paciente)
    pdf_uploads = PDFUpload.objects.filter(paciente=paciente)
    transacoes = Financeiro.objects.filter(paciente=paciente)

    # Cálculo do saldo financeiro
    total_entrada = transacoes.filter(tipo='Entrada', status='Pago').aggregate(Sum('valor'))['valor__sum'] or 0
    total_saida = transacoes.filter(tipo='Saída', status='Pago').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo_total = total_entrada - total_saida

    # Inicializa os formulários
    form = AnotacaoForm()
    dente_form = DenteForm(instance=odontograma)
    pdf_form = PDFUploadForm()
    financeiro_form = FinanceiroForm(initial={'paciente': paciente})

    if request.method == 'POST':
        if 'descricao' in request.POST:  # Identifica se é o formulário financeiro
            financeiro_form = FinanceiroForm(request.POST)
            if financeiro_form.is_valid():
                financeiro_instance = financeiro_form.save(commit=False)
                financeiro_instance.usuario = request.user

                # Criação de múltiplas parcelas
                parcelas = financeiro_form.cleaned_data['parcelas']
                valor_total = financeiro_form.cleaned_data['valor']
                valor_parcela = valor_total / parcelas
                data_cobranca = financeiro_form.cleaned_data['data_de_cobranca']

                for i in range(1, parcelas + 1):
                    Financeiro.objects.create(
                        descricao=financeiro_instance.descricao,
                        paciente=financeiro_instance.paciente,
                        valor=valor_parcela,
                        tipo=financeiro_instance.tipo,
                        usuario=financeiro_instance.usuario,
                        data_de_cobranca=data_cobranca,
                        parcelas=parcelas,
                        numero_parcela=i,
                        status='Pendente',
                    )
                    data_cobranca += relativedelta(months=1)

                messages.success(request, "Transação financeira adicionada com sucesso.")
                return redirect('pagina_paciente', paciente_id=paciente.id)

        else:
            # Lógica para outros formulários
            form = AnotacaoForm(request.POST)
            dente_form = DenteForm(request.POST, instance=odontograma)
            pdf_form = PDFUploadForm(request.POST, request.FILES)

            if form.is_valid():
                anotacao = form.save(commit=False)
                anotacao.paciente = paciente
                anotacao.save()

            if dente_form.is_valid():
                dente_form.save()

            if pdf_form.is_valid():
                pdf_upload = pdf_form.save(commit=False)
                pdf_upload.paciente = paciente
                pdf_upload.save()

            return redirect('pagina_paciente', paciente_id=paciente.id)

    context = {
    "object": paciente,
    "eventos": eventos,
    "anotacoes": anotacoes,
    "form": form,
    "odontograma": odontograma,
    "dente": dente_form,
    "pdf_form": pdf_form,
    "pdf_uploads": pdf_uploads,
    "transacoes": transacoes,
    "total_entrada": total_entrada,
    "total_saida": total_saida,
    "saldo_total": saldo_total,
    "paciente": paciente,  # Certifique-se de que esta linha está presente
}
    return render(request, 'frontend/pagina_paciente.html', context)

@login_required(login_url="/")
def atualizar_status_paciente(request, item_id, paciente_id):
    # Obtém a instância do item Financeiro e do paciente
    item = get_object_or_404(Financeiro, id=item_id, usuario=request.user)
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == "POST":
        novo_status = request.POST.get('status')
        item.status = novo_status
        item.save()

        # Redireciona para a página do paciente
        return redirect('pagina_paciente', paciente_id=paciente.id)

    return render(request, 'frontend/financeiro.html', {'financeiro': item})

@login_required(login_url="/")
def delete_pdf(request, paciente_id, pdf_id):
    context = {}
    pdf = get_object_or_404(PDFUpload, id=pdf_id, paciente_id=paciente_id)
    context['object'] = pdf
    if request.method == "POST":
        pdf.delete()
        return redirect('pagina_paciente', paciente_id=paciente_id)
    return render(request, 'frontend/confirmar_excluir_pdf.html', context)



@login_required(login_url="/")
def salvar_desenho(request, paciente_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image')

        if image_data:
            # Decodifica a imagem em Base64
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = ContentFile(base64.b64decode(imgstr), name=f"odontograma_{paciente_id}.{ext}")

            # Salva a imagem no modelo Odontograma
            odontograma = Odontograma.objects.get(paciente_id=paciente_id)
            odontograma.image.save(f'odontograma_{paciente_id}.{ext}', img_data)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Imagem não encontrada'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=400)



@has_role_decorator('administrador')
@login_required(login_url="/")
def delete_user(request, user_id):
    context={}
    usuario=get_object_or_404(User, id=user_id)
    context['object']=usuario
    if request.method == "POST":
        usuario.delete()
        return redirect('cadastro')
    return render(request, 'frontend/confirmar_excluir.html', context)

@login_required(login_url="/")
def calendario(request):
    events = Event.objects.filter(user=request.user)
    pacientes = Paciente.objects.all()
    users = User.objects.all()
    return render(request, 'frontend/calendario.html', {
        'events': events,
        'pacientes': pacientes,
        'users': users,
    })



@login_required(login_url="/")
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


@login_required(login_url="/")
def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month

@login_required(login_url="/")
def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(LoginRequiredMixin, generic.ListView):
    login_url = "accounts:signin"
    model = Event
    template_name = "frontend/calendario.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context


@login_required(login_url="/")
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('success_url', {'form': form, 'pacientes': pacientes})  # Redirecionar para a página de sucesso
    else:
        form = EventForm()

    # Obter todos os pacientes
    pacientes = Paciente.objects.all()

    return render(request, 'template_name.html', {'form': form, 'pacientes': pacientes})


class EventEdit(generic.UpdateView):
    model = Event
    fields = ["title", "description", "start_time", "end_time"]
    template_name = "event.html"


@login_required(login_url="signup")
def event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    eventmember = EventMember.objects.filter(event=event)
    context = {"event": event, "eventmember": eventmember}
    return render(request, "frontend/calendario.html", context)


def add_eventmember(request, event_id):
    forms = AddMemberForm()
    if request.method == "POST":
        forms = AddMemberForm(request.POST)
        if forms.is_valid():
            member = EventMember.objects.filter(event=event_id)
            event = Event.objects.get(id=event_id)
            if member.count() <= 9:
                user = forms.cleaned_data["user"]
                EventMember.objects.create(event=event, user=user)
                return redirect("calendario")
            else:
                print("--------------User limit exceed!-----------------")
    context = {"form": forms}
    return render(request, "frontend/calendario.html", context)


class EventMemberDeleteView(generic.DeleteView):
    model = EventMember
    template_name = "frontend/calendario.html"
    success_url = reverse_lazy("calendario")

class CalendarViewNew(LoginRequiredMixin, generic.View):
    template_name = "frontend/calendario.html"
    form_class = EventForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return self._render_calendar(request, form)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            event = form.save(commit=False)

            # Pega o ID do usuário selecionado no formulário
            selected_user_id = request.POST.get('user')  # Obtém o ID do usuário selecionado
            selected_user = User.objects.filter(id=selected_user_id).first()

            if selected_user:
                event.user = selected_user  # Define o usuário selecionado como o responsável pelo evento
                event.save()
                return redirect('calendario')  # Redireciona para a página do calendário após salvar

        return self._render_calendar(request, form)

    def _render_calendar(self, request, form):
        # Lógica para verificar grupos e obter eventos
        is_recepcionista = request.user.groups.filter(name="recepcionista").exists()
        admin_users = User.objects.filter(groups__name="administrador")
        pacientes = Paciente.objects.all()

        selected_user_id = request.GET.get('user')
        selected_user = None

        if selected_user_id:
            selected_user = User.objects.filter(id=selected_user_id).first()
            events = Event.objects.filter(user=selected_user) if selected_user else Event.objects.none()
        elif is_recepcionista or not selected_user_id:
            events = Event.objects.all()
        else:
            events = Event.objects.filter(user=request.user)

        current_date = timezone.now()
        events_month = events.filter(
            start_time__year=current_date.year,
            start_time__month=current_date.month,
            start_time__gte=current_date
        ).order_by('start_time')

        event_list = [
            {
                "id": event.id,
                "title": event.title,
                "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "description": event.description,
                "user": event.user.username,
            }
            for event in events
        ]

        context = {
            "form": form,
            "events": event_list,
            "events_month": events_month,
            "admin_users": admin_users,
            "selected_user": selected_user,
            "pacientes": pacientes,
        }
        return render(request, self.template_name, context)
@login_required(login_url="/")
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'message': 'Consulta deletada!.'})
    else:
        return JsonResponse({'message': 'Erro!'}, status=400)

@login_required(login_url="/")
def next_week(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.start_time += timedelta(days=7)
        next.end_time += timedelta(days=7)
        next.save()
        return JsonResponse({'message': 'Reagendado para semana que vem'})
    else:
        return JsonResponse({'message': 'Erro!'}, status=400)

@login_required(login_url="/")
def next_day(request, event_id):

    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        next = event
        next.id = None
        next.start_time += timedelta(days=1)
        next.end_time += timedelta(days=1)
        next.save()
        return JsonResponse({'message': 'Reagendado para amanha'})
    else:
        return JsonResponse({'message': 'Erro!'}, status=400)

class AllEventsListView(ListView):
    """ All event list views """

    template_name = "frontend/calendario.html"
    model = Event
    @login_required(login_url="/")
    def get_queryset(self):
        return Event.objects.get_all_events(user=self.request.user)



class RunningEventsListView(ListView):
    """ Running events list view """

    template_name = "frontend/calendario.html"
    model = Event
    @login_required(login_url="/")
    def get_queryset(self):
        return Event.objects.get_running_events(user=self.request.user)

@login_required(login_url="/")
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('pacientes')  # Redireciona após a atualização
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'frontend/editar_paciente.html', {'form': form})