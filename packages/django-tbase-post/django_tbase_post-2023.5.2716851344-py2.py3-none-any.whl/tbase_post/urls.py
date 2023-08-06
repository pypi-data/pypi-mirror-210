from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='detail_index'),
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail_view'),
    path('tag/<int:pk>/',
         views.TagListView.as_view(),
         name='article_list_by_tag'),
    # path('detail/<int:pk>', views.DetailView.as_view(), name='post_view'),
    # path('<int:pk>/', views.PostView.as_view(), name='post'),
]