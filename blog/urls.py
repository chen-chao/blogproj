from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('blog/', views.IndexView.as_view(), name='blog'),
    path('blog/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    # path('archive/<int:year>/', views.ArchiveView.as_view(), name='archives'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(),
         name='archives'),
    path('blog/<int:pk>/<str:imagename>/', views.ImageView, name='image'),
    path('tags/<int:pk>/', views.TagView.as_view(), name='tags'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('search/', views.search, name='search'),
]
