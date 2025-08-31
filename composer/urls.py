from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('backgrounds/', views.backgrounds, name='backgrounds'),
    path('characters/', views.characters, name='characters'),
    path('create-scene/', views.create_scene, name='create_scene'),
    path('scene/<int:scene_id>/', views.scene_result, name='scene_result'),
    path('my-scenes/', views.my_scenes, name='my_scenes'),
    path('delete-background/<int:bg_id>/', views.delete_background, name='delete_background'),
    path('delete-character/<int:char_id>/', views.delete_character, name='delete_character'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]
