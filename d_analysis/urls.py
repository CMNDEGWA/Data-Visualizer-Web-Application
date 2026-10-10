from django.urls import path
from d_analysis import views

urlpatterns = [
    path('', views.upload_view, name='upload_view'),
    path('uploads/<uuid:upload_id>/delete/', views.delete_upload_view, name='delete_upload_view'),
    path('dashboard/<uuid:upload_id>/', views.dashboard_view, name='dashboard_view'),
]