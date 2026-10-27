from django.contrib import admin
from .models import Subject, Student, Score, AccessToken

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['code', 'cohort', 'owner']
    search_fields = ['code', 'cohort']

admin.site.register(Subject)
admin.site.register(Score)
@admin.register(AccessToken)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'expires_at', 'revoked']
    fields = ['name', 'owner', 'expires_at', 'revoked']
    def has_add_permission(self, request): return False
