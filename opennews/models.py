# -*- coding: utf-8 -*-
# import django libs
from django.template.defaultfilters import slugify
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# improt tastypie tools
from tastypie.utils.timezone import now
from tastypie.models import create_api_key


# Each time a user is create, create an api key
models.signals.post_save.connect(create_api_key, sender=User)



class Member(models.Model):
	twitter = models.CharField(max_length=100, blank=True)
	facebook = models.CharField(max_length=255, blank=True)
	gplus = models.CharField(max_length=255, blank=True)
	preferedCategoryIDs = models.ManyToManyField("Category", blank=True)
	autoShare = models.BooleanField(default=False)
	geoloc = models.BooleanField(default=False)
	pays = models.CharField(max_length=3, blank=True)
	ville = models.CharField(max_length=255, blank=True)
	maxArticle = models.IntegerField(default = 10)
	user = models.OneToOneField(User)
	
	def __unicode__(self):
		return self.user.username
		
class Category(models.Model):
	name = models.CharField(max_length=255)
	url = models.CharField(max_length=255)
	memberId = models.ForeignKey(Member, blank=True, null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
		return self.name

class Tag(models.Model):
	tag = models.CharField(max_length=30)

	def __unicode__(self):
		return self.tag

class Article(models.Model):
	title = models.CharField(max_length=255)
	text = models.TextField();
	date = models.DateTimeField(auto_now_add=True)
	published = models.BooleanField(default=True)
	validate = models.BooleanField()
	quality = models.IntegerField(null=True, blank=True)
	tags = models.ManyToManyField("Tag", null=True, blank=True)
	memberId = models.ForeignKey(Member)
	category = models.ForeignKey(Category)
	coord = models.CharField(max_length=20, blank=True)
	media = models.FileField(upload_to="articles_media", blank=True)

	def __unicode__(self):
		return self.title



class Comment(models.Model):
	text = models.CharField(max_length=255)
	articleId = models.ForeignKey(Article)
	memberId = models.ForeignKey(Member)

	def __unicode__(self):
		if len(self.text) > 20:
			return self.text[:19] + "..."
		else:
			return selft.text


