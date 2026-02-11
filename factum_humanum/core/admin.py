from django.contrib import admin
from django.utils import timezone
from .models import Creator, Work, Payment
from . import emails


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
    actions = ['grant_5_credits', 'grant_10_credits', 'grant_20_credits', 'reset_credits']
    
    def grant_5_credits(self, request, queryset):
        updated = queryset.update(credits=5)
        self.message_user(request, f"{updated} creator(s) now have 5 credits.")
    grant_5_credits.short_description = "Grant 5 credits"
    
    def grant_10_credits(self, request, queryset):
        updated = queryset.update(credits=10)
        self.message_user(request, f"{updated} creator(s) now have 10 credits.")
    grant_10_credits.short_description = "Grant 10 credits"
    
    def grant_20_credits(self, request, queryset):
        updated = queryset.update(credits=20)
        self.message_user(request, f"{updated} creator(s) now have 20 credits.")
    grant_20_credits.short_description = "Grant 20 credits"
    
    def reset_credits(self, request, queryset):
        updated = queryset.update(credits=0)
        self.message_user(request, f"{updated} creator(s) reset to 0 credits.")
    reset_credits.short_description = "Reset credits to 0"


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'status', 'has_file', 'registered_at', 'reviewed_at')
    list_filter = ('category', 'registered_at', 'status')
    search_fields = ('title', 'creator__name', 'description')
    readonly_fields = ('id', 'registered_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'creator', 'title', 'category')
        }),
        ('Details', {
            'fields': ('description', 'creation_date', 'work_file', 'reviewer_notes')
        }),
        ('Timestamps', {
            'fields': ('registered_at','reviewed_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_submissions', 'reject_submissions']
    
    def has_file(self, obj):
        return bool(obj.work_file)
    has_file.boolean = True
    has_file.short_description = "Has Upload"

    def approve_submissions(self, request, queryset):
        """Mark selected works as approved and send certificate email."""
        updated = 0
        for work in queryset:
            work.status = 'approved'
            work.reviewed_at = timezone.now()
            work.save()
            try:
                emails.send_certificate_approved_email(work)
            except Exception as e:
                print(f"Failed to send approval email for {work.id}: {e}")
            updated += 1
        self.message_user(request, f"{updated} submission(s) approved.")
    approve_submissions.short_description = "Approve selected submissions"

    def reject_submissions(self, request, queryset):
        """Mark selected works as rejected and send rejection email."""
        updated = 0
        for work in queryset:
            work.status = 'rejected'
            work.reviewed_at = timezone.now()
            # optionally retain existing reviewer_notes
            work.save()
            try:
                emails.send_certificate_rejected_email(work)
            except Exception as e:
                print(f"Failed to send rejection email for {work.id}: {e}")
            updated += 1
        self.message_user(request, f"{updated} submission(s) rejected.")
    reject_submissions.short_description = "Reject selected submissions"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_charge_id', 'email', 'creator', 'amount_cents', 'credits_granted', 'fulfilled', 'created_at')
    list_filter = ('fulfilled', 'currency', 'created_at')
    search_fields = ('email', 'stripe_charge_id', 'stripe_session_id', 'creator__email')
    readonly_fields = ('id', 'stripe_charge_id', 'stripe_session_id', 'created_at', 'fulfilled_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'email', 'creator', 'stripe_charge_id', 'stripe_session_id')
        }),
        ('Payment Details', {
            'fields': ('amount_cents', 'currency', 'credits_granted')
        }),
        ('Fulfillment', {
            'fields': ('fulfilled', 'fulfilled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
