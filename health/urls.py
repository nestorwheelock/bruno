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

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),

    # CBPI (Canine Brief Pain Inventory)
    path('cbpi/', views.cbpi_view, name='cbpi'),
    path('cbpi/save/', views.save_cbpi, name='save_cbpi'),

    # CORQ (Canine Owner-Reported QoL)
    path('corq/', views.corq_view, name='corq'),
    path('corq/save/', views.save_corq, name='save_corq'),

    # Treatments
    path('treatments/', views.treatments_view, name='treatments'),
    path('treatments/save/', views.save_treatment, name='save_treatment'),

    # Adverse Events (VCOG-CTCAE)
    path('events/', views.events_view, name='events'),
    path('events/save/', views.save_event, name='save_event'),

    # Language
    path('set-language/', views.set_language, name='set_language'),

    # Nutrition Tracking
    path('nutrition/', views.nutrition_view, name='nutrition'),
    path('nutrition/meal/save/', views.save_meal, name='save_meal'),
    path('nutrition/supplement/save/', views.save_supplement, name='save_supplement'),
    path('nutrition/weight/update/', views.update_weight, name='update_weight'),
    path('nutrition/foods/', views.food_database, name='food_database'),
    path('nutrition/planning/', views.meal_planning_view, name='meal_planning'),
    path('api/foods/', views.api_foods, name='api_foods'),
    path('api/nutrition/', views.api_nutrition_summary, name='api_nutrition_summary'),

    # Medical Records
    path('records/', views.records_view, name='records'),
    path('records/upload/', views.upload_record, name='upload_record'),
    path('records/<int:record_id>/', views.record_detail, name='record_detail'),
    path('records/<int:record_id>/edit/', views.edit_record, name='edit_record'),
    path('records/<int:record_id>/delete/', views.delete_record, name='delete_record'),
    path('api/lab-values/', views.api_lab_values, name='api_lab_values'),

    # Timeline (Case Journal)
    path('timeline/', views.timeline_view, name='timeline'),
    path('timeline/new/', views.timeline_create, name='timeline_create'),
    path('timeline/<int:entry_id>/', views.timeline_detail, name='timeline_detail'),
    path('timeline/<int:entry_id>/edit/', views.timeline_edit, name='timeline_edit'),
    path('timeline/<int:entry_id>/delete/', views.timeline_delete, name='timeline_delete'),
    path('timeline/attachment/<int:attachment_id>/delete/', views.timeline_delete_attachment, name='timeline_delete_attachment'),

    # Providers
    path('providers/', views.provider_list, name='provider_list'),
    path('providers/new/', views.provider_create, name='provider_create'),

    # Calendar Views
    path('calendar/', views.calendar_month_view, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar_month_view, name='calendar_month'),
    path('calendar/week/', views.calendar_week_view, name='calendar_week'),
    path('calendar/week/<int:year>/<int:week>/', views.calendar_week_view, name='calendar_week_detail'),
]
