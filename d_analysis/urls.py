from django.urls import path
from d_analysis import views

urlpatterns = [
    path('', views.upload_view, name='upload_view'),
    path('dashboard/<uuid:upload_id>/', views.dashboard_view, name='dashboard_view'),
]