from rest_framework import serializers
from .models import Book,Category,Publisher,Author,BookImage,BookTransaction
from account.serializers import UserSerializer

class AuthorShortSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields =['id','name','image',]

class AuthorDetailsSerializer(AuthorShortSerializer):
    book_count  = serializers.SerializerMethodField()

    class Meta(AuthorShortSerializer.Meta):
        fields = AuthorShortSerializer.Meta.fields + ['bio','date_of_birth','date_of_death','book_count']
    
    def get_book_count(self,obj):
        return obj.books.count()

class CategoryShortSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryDetailsSerializer(CategoryShortSerializer):
    book_count  = serializers.SerializerMethodField()

    class Meta(CategoryShortSerializer.Meta): 
        fields =CategoryShortSerializer.Meta.fields  +['book_count']
    
    def get_book_count(self,obj):
        return obj.books.count()

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'

class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['id','image']

class BookDetailsSerializer(serializers.ModelSerializer):
    author = AuthorShortSerializer(many=True,read_only=True)
    category = CategoryShortSerializer(many=True,read_only=True)
    image = BookImageSerializer(many=True,read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = '__all__'

class SingleBookDetailsSerializer(BookDetailsSerializer):
    related_books =  serializers.SerializerMethodField()

    def get_related_books(self,obj):
        related_books = Book.objects.filter(category__in=obj.category.all(),is_available=True).exclude(id=obj.id)
        return BookDetailsSerializer(related_books,many=True).data

class BookCreateUpdateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(many=True, queryset=Author.objects.all())
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    publisher = serializers.PrimaryKeyRelatedField(queryset=Publisher.objects.all(), allow_null=True, required=False)
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        authors = validated_data.pop('author')
        categories = validated_data.pop('category')
        images = validated_data.pop('images',[])
        book = Book.objects.create(**validated_data)
        book.author.set(authors)
        book.category.set(categories)

        for image in images:
            BookImage.objects.create(book=book, image=image)
        
        return book
    

class BookTransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BookTransaction 
        fields = '__all__'
        extra_kwargs = {'due_date': {'required': False},'user':{'required': False},'book':{'required': False}} 

class BookTransactionBookDetailsSerializer(BookTransactionSerializer):
    book = BookDetailsSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    


        
    


