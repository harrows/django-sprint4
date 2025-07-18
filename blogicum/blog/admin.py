from django.contrib import admin
from .models import Category, Location, Post, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("id", "title", "slug")
    search_fields = ("title",)
    ordering = ("title",)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "pub_date", "category", "location")
    list_filter = ("pub_date", "category", "location")
    search_fields = ("title", "text")
    raw_id_fields = ("author", "category", "location")
    date_hierarchy = "pub_date"
    ordering = ("-pub_date",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at", "text")
    list_filter = ("created_at", "post")
    search_fields = ("text",)
    raw_id_fields = ("post", "author")
    ordering = ("-created_at",)
