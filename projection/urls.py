from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'projection'
urlpatterns = [
    path('graph/', views.graph, name='graph'),
    path('graph/data', views.graph_data, name='graph_data'),
    path('csv/<parameter>', views.days_to_csv, name='csv_output')
]
