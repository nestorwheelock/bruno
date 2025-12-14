from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    path('', views.tracker_view, name='tracker'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save/', views.save_daily_entry, name='save_entry'),
    path('medications/', views.medications_view, name='medications'),
    path('medications/add/', views.add_medication, name='add_medication'),
    path('medications/<int:med_id>/dose/', views.record_dose, name='record_dose'),
    path('nodes/', views.nodes_view, name='nodes'),
    path('nodes/save/', views.save_node_measurement, name='save_nodes'),
    path('history/', views.history_view, name='history'),
]
