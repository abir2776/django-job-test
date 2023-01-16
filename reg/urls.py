from django.urls import path
from . import views
urlpatterns = [
    path('signup/',views.sign_up,name='signup'),
    path('login/',views.login_page,name='login'),
    path('logout/',views.logout_user,name='logout'),
    path('home/',views.home,name='home'),
    path('',views.home,name='home'),
]