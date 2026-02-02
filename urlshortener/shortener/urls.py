from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('create/', views.create_short_url, name='create'),
    path('edit/<int:pk>/', views.edit_short_url, name='edit_short_url'),
    path('delete/<int:pk>/', views.delete_short_url, name='delete'),
    path('<str:short_key>/', views.redirect_short_url, name='redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)