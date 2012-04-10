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

from shorturls.models import *
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
import simplejson
from forms import *

def get_url(request, base64):
	"""
	Returns URL for a given Link given a request and logs it.
	"""
	if base64:
		links_all = Link.objects.filter(base64=base64)
		if links_all:
			link = links_all[0]
			newLinkClick = LinkClick(link=link)
			if 'HTTP_REFERER' in request.META:
				newLinkClick.directing_link = request.META['HTTP_REFERER'].lower()
			else:
				newLinkClick.directing_link = 'Direct'
			if 'HTTP_USER_AGENT' in request.META:
				newLinkClick.user_agent = request.META['HTTP_USER_AGENT']
				if 'iphone' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'iPhone'
					newLinkClick.save()
					if link.long_url_iphone:
						return link.long_url_iphone
					else:
						return link.long_url_default
				elif 'ipad' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'iPad'
					newLinkClick.save()
					if link.long_url_ipad:
						return link.long_url_ipad
					else:
						return link.long_url_default
				elif 'android' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'Android'
					newLinkClick.save()
					if link.long_url_android:
						return link.long_url_android
					else:
						return link.long_url_default
				elif 'blackberry' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'BlackBerry'
					newLinkClick.save()
					if link.long_url_blackberry:
						return link.long_url_blackberry
					else:
						return link.long_url_default
				elif 'rim' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'BlackBerry'
					newLinkClick.save()
					if link.long_url_blackberry:
						return link.long_url_blackberry
					else:
						return link.long_url_default
				elif 'windows' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'PC'
					newLinkClick.save()
					if link.long_url_pc:
						return link.long_url_pc
					else:
						return link.long_url_default
				elif 'macintosh' in request.META['HTTP_USER_AGENT'].lower():
					newLinkClick.browser = 'Mac'
					newLinkClick.save()
					if link.long_url_mac:
						return link.long_url_mac
					else:
						return link.long_url_default
				else:
					newLinkClick.browser = 'Unknown'
					newLinkClick.save()
					return link.long_url_default
			else:
				newLinkClick.user_agent = 'Unknown'
				newLinkClick.browser = 'Unknown'
				newLinkClick.save()
				return link.long_url_default
		return None
	return None

def get_devices(beginning_date, end_date, user, link=None):
	from django.db import connection
	cursor = connection.cursor()
	#	generate_series('%(beginning_date)s', '%(end_date)s', interval '1 day') ON generate_series = date(s.date_time)
	if not link:
		sql = '''
			SELECT
				COUNT(s.id),
				g.generate_series::date,
				s.browser
			FROM (
				SELECT c.id, c.date_time, c.browser
				FROM
					shorturls_linkclick c
				INNER JOIN
					shorturls_link l ON c.link_id = l.id
				WHERE
					l.user_id = %(user_pk)s) s
			RIGHT JOIN
						(
							SELECT
									DATE('%(beginning_date)s') + s.a as generate_series
								FROM
									generate_series(0,%(length)s,1) as s(a)
						)g
			ON
				generate_series = date(s.date_time)
			GROUP BY
				g.generate_series, s.browser
			ORDER BY
				g.generate_series;''' % {'beginning_date': beginning_date, 'end_date':end_date, 'length': (end_date - beginning_date).days , 'user_pk': user.pk}
	else:
		sql = '''
			SELECT
				COUNT(s.id),
				generate_series::date,
				s.browser
			FROM (
				SELECT c.id, c.date_time, c.browser
				FROM
					shorturls_linkclick c
				INNER JOIN
					shorturls_link l ON c.link_id = l.id
				WHERE
					l.user_id = %(user_pk)s
				AND
					l.id='%(link_id)s'
				) s
			RIGHT JOIN
						(
							SELECT
									DATE('%(beginning_date)s') + s.a as generate_series
								FROM
									generate_series(0,%(length)s,1) as s(a)
						)g
			ON
				generate_series = date(s.date_time)
			GROUP BY
				generate_series, s.browser
			ORDER BY
				generate_series;''' % {'beginning_date': beginning_date, 'end_date': end_date , 'user_pk': user.pk, 'length': (end_date - beginning_date).days ,'link_id':link.pk}
	cursor.execute(sql)
	rows = cursor.fetchall()

	return rows

def get_timeline(beginning_date, end_date, user, link=None):
	from django.db import connection
	cursor = connection.cursor()
	if not link:
		sql = '''
			SELECT
				COUNT(s.id),
				generate_series::date
			FROM (
				SELECT c.id, c.date_time
				FROM
					shorturls_linkclick c
				INNER JOIN
					shorturls_link l ON c.link_id = l.id
				WHERE
					l.user_id = %(user_pk)s
				) s
			RIGHT JOIN
						(
							SELECT
									DATE('%(beginning_date)s') + s.a as generate_series
								FROM
									generate_series(0,%(length)s,1) as s(a)
						)g
			ON
				generate_series = date(s.date_time)
			GROUP BY
				generate_series
			ORDER BY
				generate_series;''' % {'beginning_date': beginning_date, 'end_date': end_date , 'length': (end_date - beginning_date).days , 'user_pk': user.pk}
	else:
				sql = '''
			SELECT
				COUNT(s.id),
				generate_series::date
			FROM (
				SELECT c.id, c.date_time
				FROM
					shorturls_linkclick c
				INNER JOIN
					shorturls_link l ON c.link_id = l.id
				WHERE
					l.user_id = %(user_pk)s
				AND
					l.id='%(link_id)s'
				) s
			RIGHT JOIN
						(
							SELECT
									DATE('%(beginning_date)s') + s.a as generate_series
								FROM
									generate_series(0,%(length)s,1) as s(a)
						)g
			ON
				generate_series = date(s.date_time)
			GROUP BY
				generate_series
			ORDER BY
				generate_series;''' % {'beginning_date': beginning_date, 'end_date': end_date , 'user_pk': user.pk, 'length': (end_date - beginning_date).days , 'link_id':link.pk}
	cursor.execute(sql)
	rows = cursor.fetchall()

	return rows

def get_unique_devices(beginning_date, end_date, user, link=None):
	if not link:
		return LinkClick.objects.filter(date_time__range=[beginning_date, end_date], link__user=user).exclude(browser='').values_list('browser').distinct()
	else:
		return LinkClick.objects.filter(date_time__range=[beginning_date, end_date], link=link).exclude(browser='').values_list('browser').distinct()

def date_range(start, end):
	r = (end+datetime.timedelta(days=1)-start).days
	return [start+datetime.timedelta(days=i) for i in range(r)]

def get_unique_dates(beginning_date, end_date):
	dateList = date_range(beginning_date, end_date)
	dates = []
	for d in dateList:
		formatted_date = "%(month)s/%(day)s/%(year)s" % {'month':d.month, 'day':d.day, 'year': d.year}
		dates.append(formatted_date)
	return dates

def format_date(d):
	return "%(month)s/%(day)s/%(year)s" % {'month':d.month, 'day':d.day, 'year': d.year}
