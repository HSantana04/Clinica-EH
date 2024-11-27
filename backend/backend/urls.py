"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from app import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login, name="login"),
    path("login", views.login_incorreto, name="login_incorreto"),
    path("index", views.index, name="index"),
    path("cadastro", views.cadastro, name='cadastro'),
    path("calendario", views.CalendarViewNew.as_view(), name="calendario"),
    path("pacientes", views.pacientes, name="pacientes"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cadastrar_paciente', views.cadastrar_paciente, name='cadastrar_paciente'),
    path("pagina_usuario", views.pagina_usuario, name='pagina_usuario'),
    path("pagina_paciente/<int:paciente_id>/", views.pagina_paciente, name='pagina_paciente'),
    #path('deletar_pdf/<int:pdf_id>/', views.deletar_pdf, name='deletar_pdf'),
    path('atualizar-status/<int:item_id>/<int:paciente_id>/', views.atualizar_status_paciente, name='atualizar_status_paciente'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('paciente/<int:paciente_id>/delete/', views.delete_paciente, name='delete_paciente'),
    path('paciente/<int:paciente_id>/update/', views.editar_paciente, name='update_paciente'),
    path('financeiro/<int:item_id>/delete/', views.deletar_financeiro, name='deletar_financeiro'),
    path('financeiro/<int:item_id>/editar/', views.editar_financeiro, name='editar_financeiro'),
    path('financeiro/<int:item_id>/atualizar_status', views.atualizar_status, name='atualizar_status'),
    path("calenders/", views.CalendarView.as_view(), name="calendars"),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('next_week/<int:event_id>/', views.next_week, name='next_week'),
    path('next_day/<int:event_id>/', views.next_day, name='next_day'),
    path("event/new/", views.create_event, name="event_new"),
    path("event/edit/<int:pk>/", views.EventEdit.as_view(), name="event_edit"),
    path("event/<int:event_id>/details/", views.event_details, name="event-detail"),
    path(
        "add_eventmember/<int:event_id>", views.add_eventmember, name="add_eventmember"
    ),
    path(
        "event/<int:pk>/remove",
        views.EventMemberDeleteView.as_view(),
        name="remove_event",
    ),
    path("all-event-list/", views.AllEventsListView.as_view(), name="all_events"),
    path(
        "running-event-list/",
        views.RunningEventsListView.as_view(),
        name="running_events",
    ),
    path('salvar_desenho/<int:paciente_id>/', views.salvar_desenho, name='salvar_desenho'),
    path('financeiro', views.financeiro, name="financeiro"),
    path('pagina_paciente/<int:paciente_id>/delete/<int:anotacao_id>/', views.delete_anotacao, name='delete_anotacao'),
    path('pagina_paciente/<int:paciente_id>/delete_pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)