# -*- coding: utf-8 -*-

#Import django libs
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q

# Import tools
from itertools import chain
import datetime
import mimetypes

# Import tastypie ApiKey
from tastypie.models import ApiKey

#import openNews datas
from forms import *
from models import *


#Define your views here

def home(request):
	"""The default view"""
	#articles = Article.objects.filter(tag in tags)
	foo = datetime.datetime.now()
	user = request.user
	return render(request, "index.html", locals())


def login_user(request):
	"""The view for login user"""
	# Already logged In ? => go Home
	if request.user.is_authenticated():
		return HttpResponseRedirect("/")

	# If you come from login required page, get the page url in "next"
	next = request.GET.get('next')

	# If form had been send
	if len(request.POST) > 0:
		# make a login form with the POST values
		form = login_form(request.POST)
		
		if form.is_valid():
			# If form is valid, try to authenticate the user with the POST datas
			s_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])

			if s_user is not None:
				# If the user exist, log him
				login(request, s_user)
				if next is not None:
					# If you come from a login required page, redirect to it
					return HttpResponseRedirect(next)
				else:
					# Else go Home
					return HttpResponseRedirect("/")
			else:
				# If user does not exist, return to the login page & send the next params et the formular
				return render_to_response("login.html", {'form': form, 'next':next})
		else:
			# If form is not valid, return to the login page & send the next params et the formular
			return render_to_response("login.html", {'form': form, 'next':next})
	else:
		# If form is not send, it's the first visit.
		# Make an empty login form and send it to login template
		form = login_form()
		return render_to_response("login.html", {'form': form, 'next':next})


def logout_user(request):
	"""The view for logout user"""
	logout(request)
	return HttpResponseRedirect('/')


def register(request):
	"""The views for register new user"""
	# If form had been send
	if len(request.POST) > 0:
		# make a user registration form with the POST values
		form = user_create_form(request.POST)
		
		if form.is_valid():
			# If form is valid, create and try to authenticate the user with the POST datas
			user = form.save()
			# Get the password from the POST values
			pwd = form.cleaned_data['password1']
			# Try to authenticate the user
			s_user = authenticate(username=user.username, password=pwd)
			if s_user is not None:
				# If user exist, log him and go to his account management panel
				login(request, s_user)
				return HttpResponseRedirect('preferences')
			else:
				# if he does not exist, return to user registration page with form filled by the POST values
				return render_to_response("register.html", {'form': form})
		else:
			# if form is not valid, return to registration page
			return render_to_response("register.html", {'form': form})
	else:
		# if its you first visit, make an empty user registration form and send it
		form = user_create_form()
		return render_to_response("register.html", {'form': form})



@login_required(login_url='/login/') # You need to be logged for this page
def preferences(request):
	"""The view where logged user can modify their property"""
	# Get the user's api key
	api_key = ApiKey.objects.filter(user=request.user)
	
	# If form had been send
	if len(request.POST) > 0:
		# make a user preference form with the POST values
		form = user_preferences_form(request.POST)
		
		if form.is_valid():
			# If form is valid, save the user preferences and go Home
			form.save(request.user)
			return HttpResponseRedirect('/')
		else:
			# If not, send the preference form with the api_key and the post datas
			return render_to_response("preferences.html", {'form': form, 'api_key': api_key[0].key})
	else:
		# if the form is not send try to find the member from the logged user
		try:
			member = request.user.member
		except Member.DoesNotExist:
			member = None
		
		if member is not None:
			# if member is not none, create preference form with user's datas
			form = user_preferences_form(instance=request.user.member)
			return render_to_response("preferences.html", {'form': form, 'api_key': api_key[0].key})
		else:
			# If member does not exist, send an empty form
			form = user_preferences_form()
			return render_to_response("preferences.html", {'form': form})	



def get_profile(request, userId):
	"""Show the public profile of a user. Get it by his id"""
	user = User.objects.filter(id=userId)[0]
	return render_to_response("public_profile.html", {'user': user})



def read_article(request, IDarticle):
	"""The view for reading an article"""
	# Get the article from the IDarticle params
	article = Article.objects.get(id=IDarticle)
	# Get the tags of the article
	tags = article.tags.all()
	if article.media:
		# If there is a media linked to the article, get the mime of it and the type of media
		mime = mimetypes.guess_type(article.media.url)[0]
		mediaType = mime[0:3]
	else:
		# If there is not, set False to mime et mediaType
		mime = False
		mediaType = False
	return render_to_response("article.html", {'article': article, 'mediaType': mediaType, 'mime': mime, 'tags': tags})


@login_required(login_url='/login/') # You need to be logged for this page
def write_article(request):
	"""The view for writing an article"""
	# Get the member from the request user
	member = Member.objects.get(user=request.user)

	# If form had been send
	if len(request.POST) > 0:
		# make a article form with the POST values
		form = article_form(request.POST, request.FILES)
		if form.is_valid():
			# If the form is correctly filled, check the geoloc status of the author
			if member.geoloc is not False:
				# Get coord from POST (an hidden input from template, filled by js)
				coordonnee = request.POST['coordonnee']
				# Save the article with the coord
				article = form.save(m_member=member, coord=coordonnee)
			else:
				# Save the article without the coord
				article = form.save(m_member=member)
			return HttpResponseRedirect('/categories')
		else:
			# If it's not valid, send the form with POST datas
			return render_to_response("write.html", {'form': form, 'member':member})
	else:
		# If it's not valid, send an empty form
		form = article_form()
		return render_to_response("write.html", {'form': form, 'member':member})



def list_article(request, categorie):
	"""The view for listing the articles, depends on categorie"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat.name)
	
	# Filter articles by category name
	if categorie == "all":
		articles = Article.objects.all()
	else:
		articles = Article.objects.filter(category=Category.objects.filter(name=categorie.title())) # Here, .title() is to put the first letter in upperCase

	# Return the articles list, the categories list and the active categorie
	return render_to_response("liste.html", {'articles': articles, 'categories': categories, 'catActive': categorie.title()})



def search(request, words, categorie):
	"""The search view"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat.name)

	# If form had been send
	if len(request.POST) > 0:
		# Make a search form with POST datas
		form = search_form(request.POST)
		if form.is_valid():
			# If form is correctly filled, get the words and  
			words = form.cleaned_data['searchWords'].split(' ')
		else:	
			return render_to_response("search.html", {'form': form, 'categories': categories, 'catActive': categorie.title()})
	else:
		# If is not, create an empty search form and split the view param "words"
		form = search_form()
		words = words.split('_')

	# Create an articles list
	articles = []


	if categorie == "all":
		for word in words:
			# Chains the query set of the search request for all category
			articles = list(chain(articles, Article.objects.filter(Q(title__contains = word) | Q(text__contains = word))))
			# Get the article related to a tag
			tmp = Tag.objects.filter(tag = word )
			if len(tmp) is not 0:
				articles += tmp[0].article_set.all()

	else:
		for word in words:
			# Chains the query set of the search request for th requested category
			articles = list(chain(articles, Article.objects.filter(Q(category=Category.objects.filter(name=categorie.title())) & (Q(title__contains = word) | Q(text__contains = word)) )))
			# Get the article related to a tag
			tmp = Tag.objects.filter(tag = word)
			if len(tmp) is not 0:
				articles += tmp[0].article_set.all()
			
	# Return the article list
	return render_to_response("search.html", {'form': form, 'words': words, 'articles': list(set(articles)), 'categories': categories, 'catActive': categorie.title()})

