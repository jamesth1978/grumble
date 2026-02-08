from django.contrib import admin
from .models import Creator, Work


@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'has_file', 'registered_at')
    list_filter = ('category', 'registered_at')
    search_fields = ('title', 'creator__name', 'description')
    readonly_fields = ('id', 'registered_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'creator', 'title', 'category')
        }),
        ('Details', {
            'fields': ('description', 'creation_date', 'work_file')
        }),
        ('Timestamps', {
            'fields': ('registered_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_file(self, obj):
        return bool(obj.work_file)
    has_file.boolean = True
    has_file.short_description = "Has Upload"
