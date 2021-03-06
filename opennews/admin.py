# -*- coding: utf-8 -*-
from django.contrib import admin
from opennews.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import *
from django.contrib.sessions.models import Session
# Import imperavi rich editor
from imperavi.admin import ImperaviAdmin


class ArticleAdmin(ImperaviAdmin):
    list_display   = ('title','quality','fiability', 'id')
    list_filter    = ('category',)
    ordering       = ('date','title')
    search_fields  = ('title',)

admin.site.register(Category)
admin.site.register(RssFeed)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Member)
admin.site.register(AdminVote)
admin.site.register(FiabilityVote)
admin.site.register(QualityVote)


class SessionAdmin(admin.ModelAdmin): 
    def _session_data(self, obj): 
        return obj.get_decoded() 
    list_display = ['session_key', '_session_data', 'expire_date']

class MemberInline(admin.StackedInline):
    model = Member
    verbose_name_plural = 'profile'
    

class FeedEntryAdmin(admin.ModelAdmin):
    list_display   = ('title','rssfeed','date')
    list_filter    = ('rssfeed',)
    ordering       = ('date','title')
    search_fields  = ('title', 'rssfeed')

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (MemberInline, )	
    list_display   = ('username','email','is_staff')
    list_filter    = ('username', 'is_staff', 'is_active')
    ordering       = ('is_staff','is_active')
    search_fields  = ('username', 'email')
	
	
    # Configuration du formulaire d'édition
    fieldsets = (
    	# Fieldset 1 : Meta-info (titre, auteur...)
       ('Information', {
            'fields': ('username', 'email', 'password', 'is_staff')
        }),
    )

# Re-register UserAdmin
admin.site.register(Session, SessionAdmin)
admin.site.register(FeedEntry, FeedEntryAdmin)
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
