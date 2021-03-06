# -*- coding: utf-8 -*-
# Import django tools
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
# Import opennews models
from opennews.models import Member, Article, Comment


class login_form(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur'}), label="")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}), required=True, label="")



class add_rss_feed_form(forms.Form):
    rss_feed = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Rss feed url'}), label="")

    def clean(self):
        cleaned_data = super(add_rss_feed_form, self).clean()
        cc_rss_feed = cleaned_data.get("rss_feed")

        if cc_rss_feed:
            # Only do something if both fields are valid so far.
            cc_rss_feed = cc_rss_feed.split("://")
            if cc_rss_feed[0] not in ["http", "https", "feed"]:
                raise forms.ValidationError("Veuillez entrez une URL valide.")

        # Always return the full collection of cleaned data.
        return cleaned_data




class user_create_form(UserCreationForm):
    # Make the email field required
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email'}), label="")

    class Meta:
        # Use the user model to create the formular but only with username, email and passowrds fields
        model = User
        username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur'}), label="")
        password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}), required=True, label="")
        password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirmation du mot de passe'}), required=True, label="")

        fields = ("username", "email", "password1", "password2")

    # Override the save method
    def save(self, commit=True):
        # Create user from the forms datas and set the email field manually, but DON'T commit
        user = super(user_create_form, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        
        # When we want to commit (everytimes), 
        # save the user, create, link and saveth member.
        if commit:
            user.save()
            member = Member()
            member.user = user
            member.save()
        return user


class comment_form(ModelForm):
    class Meta:
        # Use the comment model to create the formular but without memberId, articleId and date fields
        model = Comment
        exclude = ('memberId','articleId', 'date')



class article_form(ModelForm):
    class Meta:
        # Use the article model to create the formular but without memberId, quality, validate and tags fields
        model = Article
        exclude = ('memberId','quality', 'validate', 'tags')

    # Override the save method   
    def save(self, m_member, coord=None, commit=True):
        # Create article from the forms datas and set the memberId field manually, but DON'T commit
        article = super(article_form, self).save(commit=False)
        article.memberId = m_member
        # Add coordinates if author agree
        if coord is not None:
            article.coord = coord
        article.save()
        return article


class user_preferences_form(ModelForm):
    class Meta:
        # Use the member model to create the formular but without user field
        model = Member
        exclude = ('user',)

    # Override the save method   
    def save(self, m_user, commit=True):
        if m_user.member is not None:
            # If m_user is defined, use his member and override the values
            member = m_user.member
            member.twitter = self.cleaned_data['twitter']
            member.facebook = self.cleaned_data['facebook']
            member.gplus = self.cleaned_data['gplus']
            member.geoloc = self.cleaned_data['geoloc']
            member.pays = self.cleaned_data['pays']
            member.ville = self.cleaned_data['ville']
            member.autoShare = self.cleaned_data['autoShare']
            member.preferedCategoryIDs = self.cleaned_data['preferedCategoryIDs']
            member.maxArticle = self.cleaned_data['maxArticle']
        else:    
            # Else, create and empty member and save it without commit         
            member = super(user_preferences_form, self).save(commit=False)
        
        # When we want to commit (everytimes), 
        # link the user and save the member
        if commit:
            member.user = m_user
            member.save()
        return member

# Create a search formular
class search_form(forms.Form):
    searchWords = forms.CharField(required=True)
