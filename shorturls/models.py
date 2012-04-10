__author__ = 'Alex Breshears'
__license__ = '''
Copyright (C) 2012 Alex Breshears

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from django.db import models
from django.contrib.admin.models import *
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django import template
from django.conf import settings
import urllib
import datetime

register = template.Library()

class Link(models.Model):
	"""
	Represents the URL Object with all 'standard' link types. Default is required.
	"""
	def __unicode__(self):
		return self.name
	name = models.CharField(max_length=1000)
	long_url_default = models.URLField()
	long_url_iphone = models.URLField(null=True, blank=True)
	long_url_android = models.URLField(null=True, blank=True)
	long_url_ipad = models.URLField(null=True, blank=True)
	long_url_windows_mobile = models.URLField(null=True, blank=True)
	long_url_blackberry = models.URLField(null=True, blank=True)
	long_url_pc = models.URLField(null=True, blank=True)
	long_url_mac = models.URLField(null=True, blank=True)
	category = models.CharField(max_length=255, blank=True, null=True)
	base64 = models.SlugField(max_length = 8, blank=True, null=True, unique=True)
	description = models.TextField(null=True, blank=True)
	created	=	models.DateTimeField(default=datetime.datetime.now())
	user = models.ForeignKey(User, null=True, blank=True)
	public = models.BooleanField(default=False)
	def short_link(self):
		return "http://" + settings.ROOT_URL + '/' + self.base64
	def qrcode(self):
		"""
		Returns a URL to a Google QR Code see:
		http://code.google.com/intl/fr-FR/apis/chart/infographics/docs/qr_codes.html
		"""
		url = "https://chart.googleapis.com/chart?chs=150x150&cht=qr&choe=UTF-&chl=http://" + settings.ROOT_URL + '/' + self.base64
		return url
	def save(self, *args, **kwargs):
		try:
			super(Link, self).save(*args, **kwargs)
			if not self.base64:
				length = 6
				from base64 import urlsafe_b64encode
				import hashlib
				hasher = hashlib.sha1()
				hasher.update(str(self.id))
				hashed = hasher.digest()
				encoded = urlsafe_b64encode( hashed ).replace('=','')
				for	i in range( length, len( encoded ) ):
					start = i - length
					end = i
					try:
						self.base64 = encoded[start:end]
						super(Link, self).save(*args, **kwargs)
						break
					except Exception:
						continue
		except Exception:
			pass

class LinkClick(models.Model):
	"""
	Captures the click for reporting
	"""
	link = models.ForeignKey(Link)
	date_time = models.DateTimeField(default=datetime.datetime.now())
	###TODO: Need to fix - double fields, but this is to support chartit
	date = models.DateField(default=datetime.datetime.now())
	###
	user_agent = models.CharField(max_length=1000, null=True, blank=True)
	#country = models.CharField(max_length=500, null=True, blank=True)
	browser = models.CharField(max_length=500, null=True, blank=True)
	directing_link = models.CharField(max_length=2000, null=True, blank=True)