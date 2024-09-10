from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from rest_framework.viewsets import ModelViewSet
from .models import Book,BookImage,Author,Category,BookTransaction
from .serializers import BookDetailsSerializer,BookCreateUpdateSerializer,BookImageSerializer,AuthorDetailsSerializer,CategoryDetailsSerializer,SingleBookDetailsSerializer,BookTransactionSerializer,BookTransactionBookDetailsSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .custom_permissions import BookReadWriteUpdatePermission
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from account.models import CustomUser
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated,IsAdminUser

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'



class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookDetailsSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [BookReadWriteUpdatePermission]

    def list(self,request):
        querySet = self.get_queryset()
        if self.request.user.groups.filter(name='USER').exists():
            filteredQuerySet =  querySet.filter(is_available=True)
        filteredQuerySet =  querySet
        paginatedResponse = self.paginate_queryset(filteredQuerySet)
        if paginatedResponse is not None:
            serializedResponse = self.get_serializer(paginatedResponse,many=True)
            return self.get_paginated_response(serializedResponse.data)
        
        message = "No Books found."
        return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)
    

    def get_serializer_class(self):
        if self.action == 'list':
            return BookDetailsSerializer
        elif self.action== 'retrieve':
            return SingleBookDetailsSerializer
        return BookCreateUpdateSerializer



class BookWiseImageViewSet(ModelViewSet):
    queryset = BookImage.objects.all()
    serializer_class = BookImageSerializer
    permission_classes = [BookReadWriteUpdatePermission]
    

    def get_object(self):
        try:
            book_id = self.kwargs.get('book_id')
            book = Book.objects.get(id=book_id) 
            if self.kwargs.get('pk') is not None:
                image_id = self.kwargs.get('pk')
                return BookImage.objects.get(book=book,id=image_id) 
            return book        
        except Book.DoesNotExist:
            raise Http404(f'Book with id {book_id} does not exits.')
        except BookImage.DoesNotExist:
                raise Http404(f'Image with id {image_id} does not exits.')
            

    def list(self,request,book_id):
        book = self.get_object()
        bookImage =  self.get_queryset().filter(book=book)
        serializedData =  self.get_serializer(bookImage,many=True,context = {'request':request})
        return Response({"images":serializedData.data})
    
    def create(self,request,book_id):
        book = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(book=book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

         
class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorDetailsSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [BookReadWriteUpdatePermission]


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailsSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [BookReadWriteUpdatePermission]


class BookTransactionViewSet(ModelViewSet):
    queryset = BookTransaction.objects.all()
    serializer_class = BookTransactionBookDetailsSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated,IsAdminUser]


    def get_queryset(self):
        querySet = self.queryset
        if(self.request.user.is_authenticated and self.request.user.role == CustomUser.ROLE.USER):
            return querySet.filter(user = self.request.user)
        return querySet

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return BookTransactionSerializer
        return BookTransactionBookDetailsSerializer
    

    def create(self,request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user= request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as err:
            return Response({"detail":("").join(err.messages)}, status=status.HTTP_403_FORBIDDEN)
    
    
        
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.role == CustomUser.ROLE.ADMIN or request.user.role == CustomUser.ROLE.ADMISTRATIVEADMIN or instance.user == self.request.user:
                serializer = self.get_serializer(instance,data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                self.permission_denied(request=request, message='You can only update your own transactions.')
                return
        except ValidationError as err:
            return Response({"detail":("").join(err.messages)}, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.role == CustomUser.ROLE.ADMIN or request.user.role == CustomUser.ROLE.ADMISTRATIVEADMIN or instance.user == self.request.user:
                serializer = self.get_serializer(instance,data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                self.permission_denied(request=request, message='You can only update your own transactions.')
                return
        except ValidationError as err:
            return Response({"detail":("").join(err.messages)}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self,request, pk=None):
        try:
            instance = self.get_object()
            if request.user.role == CustomUser.ROLE.ADMIN or request.user.role == CustomUser.ROLE.ADMISTRATIVEADMIN or instance.user == self.request.user:
                instance.delete()
                return Response({"details":f"Book transaction with id {pk} deleted successfully"},status=status.HTTP_204_NO_CONTENT)
            else:
                self.permission_denied(request=request, message='You can only delete your own transactions.')
                return
        except ValidationError as err:
            return Response({"detail":("").join(err.messages)}, status=status.HTTP_403_FORBIDDEN)



    
    





    

# class BookViewSet(ModelViewSet):
#     queryset = Book.objects.all()
#     serializer_class = BookDetailsSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [BookReadWriteUpdatePermission]

#     def list(self,request):
#         querySet = self.get_queryset()
#         if self.request.user.groups.filter(name='USER').exists():
#             filteredQuerySet =  querySet.filter(is_available=True)
#         filteredQuerySet =  querySet
#         paginatedResponse = self.paginate_queryset(filteredQuerySet)
#         if paginatedResponse is not None:
#             serializedResponse = self.get_serializer(paginatedResponse,many=True)
#             return self.get_paginated_response(serializedResponse.data)
        
#         message = "No Books found."
#         return Response({"message": message}, status=status.HTTP_204_NO_CONTENT)
    

#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return BookDetailsSerializer
#         return BookCreateUpdateSerializer

# class BookDetailsView(RetrieveUpdateDestroyAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookDetailsSerializer
#     permission_classes = [BookReadWriteUpdatePermission]


# class BookWiseImageListView(ListCreateAPIView):
#     queryset = BookImage.objects.all()
#     serializer_class = BookImageSerializer
#     permission_classes = [BookReadWriteUpdatePermission]

#     def get_object(self, book_id):
#         try:
#             return Book.objects.get(id=book_id)        
#         except Book.DoesNotExist:
#            raise Http404(f'Book with id {book_id} does not exits.')

#     def list(self,request,book_id,format=None):
#         book = self.get_object(book_id)
#         bookImage =  self.get_queryset().filter(book=book)
#         serializedData =  self.get_serializer(bookImage,many=True,context = {'request':request})
#         return Response({"images":serializedData.data})
    
#     def create(self,request,book_id,format=None):
#         book = self.get_object(book_id)
        
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(book=book)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
# class BookImageDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = BookImage.objects.all()
#     serializer_class = BookImageSerializer
#     permission_classes = [BookReadWriteUpdatePermission]

#     def get_object(self):
#         try:
#             book_id =  self.kwargs.get('book_id')
#             image_id = self.kwargs.get('image_id')
#             book = Book.objects.get(id=book_id)
#             return BookImage.objects.get(book=book,id=image_id)     
#         except Book.DoesNotExist:
#            raise Http404(f'Book with id {book_id} does not exits.')
#         except BookImage.DoesNotExist:
#            raise Http404(f'Image with id {image_id} does not exits.')
        

# class AuthorListView(ListCreateAPIView):
#     queryset = Author.objects.all()
#     serializer_class = AuthorSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [BookReadWriteUpdatePermission]


# class AuthorDetailsView(RetrieveUpdateDestroyAPIView):
#     queryset = Author.objects.all()
#     serializer_class = AuthorSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [BookReadWriteUpdatePermission]


    
    

        






     



