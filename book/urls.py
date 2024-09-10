from rest_framework.routers import DefaultRouter
from .views import BookViewSet,BookWiseImageViewSet,AuthorViewSet,CategoryViewSet,BookTransactionViewSet
from django.urls import path,include

routers = DefaultRouter()
routers.register(r'book', BookViewSet,basename='book')
routers.register(r'author',AuthorViewSet,basename='author')
routers.register(r'category',CategoryViewSet,basename='category')
routers.register(r'book_transaction',BookTransactionViewSet,basename='book transaction')
routers.register(r'book_wise_image/(?P<book_id>\d+)',BookWiseImageViewSet,basename='book_image')


# routers.register(r'category',CategoryViewSet,'category')
urlpatterns =  [
    path('', include(routers.urls,'')),
    
]
# urlpatterns = [
#     path('',BookListView.as_view(),name="book list"),
#     path('<int:pk>/',BookDetailsView.as_view(),name='book details'),
#     path('bookwise_image/<int:book_id>/<int:image_id>/',BookImageDetailView.as_view(),name='book image detail'),
#     path('bookwise_image/<int:book_id>/',BookWiseImageListView.as_view(),name="bookwise image"),
#     path('author/',AuthorListView.as_view(),name='author list'),
#     path('author/<int:pk>',AuthorDetailsView.as_view(),name='author details'),
# ]