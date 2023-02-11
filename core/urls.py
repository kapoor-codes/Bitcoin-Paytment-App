"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from payments import views
from django_email_verification import urls as mail_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('create/<pk>', views.create_payment, name='create'),
    path('invoice/<pk>',views.track_invoice, name='track'),
    path('receive/', views.receive_payment, name='receive'),
    path('final/<invoice_id>', views.final_payment, name='final'),
    path('register/', views.register, name='register'),
    path('email/', include(mail_urls)),
    path('logout/', views.logoutuser, name = 'logout'),
    path('validate/', views.validate, name = 'validate'),
]

urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)