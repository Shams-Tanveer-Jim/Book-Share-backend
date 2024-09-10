from django.contrib import admin
from .models import Author,Publisher,Category,Book,BookTransaction,BookImage
from django.utils.html import format_html

class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    readonly_fields = ('display_image',)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        return ""
    display_image.short_description = 'Image'

class BookAdmin(admin.ModelAdmin):
    inlines = [BookImageInline]


class CategoryAdmin(admin.ModelAdmin):
    
    search_fields = ("name",)
    ordering = ("name",)
    list_display = ('name', 'book_count')

    def book_count(self, obj):
        return obj.books.count()

    book_count.short_description = 'Number of Books'


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)
    list_display = ('name', 'book_count')

    def book_count(self, obj):
        return obj.books.count()

    book_count.short_description = 'Number of Books'


class BookTransactionAdmin(admin.ModelAdmin):
    list_display = ('book_name','user_email')
    ordering = ("due_date",)
    search_fields = ("book__name",'user__email')

    def book_name(self,obj):
        return obj.book.name

    def user_email(self,obj):
        return obj.user.email



admin.site.register(Author,AuthorAdmin)
admin.site.register(Publisher)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Book,BookAdmin)
admin.site.register(BookImage)
admin.site.register(BookTransaction,BookTransactionAdmin)

