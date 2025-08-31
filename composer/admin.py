from django.contrib import admin
from .models import Background, Character, Scene

@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description']

@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ['title', 'background', 'character', 'character_position', 'created_by', 'created_at']
    list_filter = ['character_position', 'created_at', 'created_by']
    search_fields = ['title', 'action_description']
