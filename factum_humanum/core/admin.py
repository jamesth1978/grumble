from django.contrib import admin
from .models import Creator, Work


@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'credits', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'email', 'credits')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['grant_1_credit', 'grant_5_credits', 'grant_10_credits', 'reset_credits']
    
    def grant_1_credit(self, request, queryset):
        updated = queryset.update(credits=1)
        self.message_user(request, f"{updated} creator(s) now have 1 credit.")
    grant_1_credit.short_description = "Grant 1 credit"
    
    def grant_5_credits(self, request, queryset):
        updated = queryset.update(credits=5)
        self.message_user(request, f"{updated} creator(s) now have 5 credits.")
    grant_5_credits.short_description = "Grant 5 credits"
    
    def grant_10_credits(self, request, queryset):
        updated = queryset.update(credits=10)
        self.message_user(request, f"{updated} creator(s) now have 10 credits.")
    grant_10_credits.short_description = "Grant 10 credits"
    
    def reset_credits(self, request, queryset):
        updated = queryset.update(credits=0)
        self.message_user(request, f"{updated} creator(s) reset to 0 credits.")
    reset_credits.short_description = "Reset credits to 0"


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
    has_file.short_description = 'Has File'
    has_file.boolean = True
