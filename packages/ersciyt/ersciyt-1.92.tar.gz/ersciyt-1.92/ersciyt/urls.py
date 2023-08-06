from django.urls import path
from . import views

urlpatterns = [
    path('', views.helping ),
    path('ytlink/', views.vid ),
    path('link/', views.vid ),
    path('vid/', views.vid ),
    path('youtube/', views.vid ),
    #path('mp3/<str:link>/', views.ytmp3 ),
    #path('ab/<str:time>/<str:link>/', views.abcut ),
    #path('<str:lang>/<str:link>/', views.sub ),
    path('shqr/', views.shqr ),
    path('mp4/<str:link>/', views.ytmp4 ),
    path('yt/<str:link>/', views.yt2mp4 ),
    path('nginx/', views.ngin ),
    path('<str:link>/', views.ytdwn ),
    
    
]
