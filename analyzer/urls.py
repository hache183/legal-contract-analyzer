from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_contract, name='upload_contract'),
    path('contracts/', views.ContractListView.as_view(), name='contract_list'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/reanalyze/', views.reanalyze_contract, name='reanalyze_contract'),
]