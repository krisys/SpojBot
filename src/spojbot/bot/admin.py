from django.contrib import admin
from models import *


class SpojUserAdmin(admin.ModelAdmin):
    pass


class SpojProblemAdmin(admin.ModelAdmin):
    list_display = ['problem', 'solved_by', 'category', 'is_tutorial', 'source', 'difficulty']
    search_fields = ['problem', 'category']
    list_filter = ['category', 'source', 'difficulty']
    list_editable = ['category', 'source', 'difficulty']


class GroupMemberAdmin(admin.TabularInline):
    model = GroupMember


class CodeGroupAdmin(admin.ModelAdmin):
    inlines = [GroupMemberAdmin]

admin.site.register(CodeGroup, CodeGroupAdmin)
admin.site.register(SpojProblem, SpojProblemAdmin)
admin.site.register(SpojUser, SpojUserAdmin)
