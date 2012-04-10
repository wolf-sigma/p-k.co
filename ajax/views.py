__author__ = 'Alex Breshears'

from shorturls.utils import *
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from chartit import PivotChart, PivotDataPool
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from forms import *
from django.shortcuts import render_to_response
import simplejson as json
import datetime
from django.conf import settings

def ajax_links(request):
	my_links = Link.objects.filter(user=request.user).all()
	template = get_template('ajax/links.html')
	links = []
	if my_links:
		max_char_length = 55
		for link in my_links:
			link_to_add = {
				'base_64': link.base64,
				'link_total_click': link.linkclick_set.count(),
				'short_default_url': link.long_url_default[:max_char_length] + (link.long_url_default[max_char_length:] and '...'),
				'short_iphone_url': link.long_url_iphone[:max_char_length] + (link.long_url_iphone[max_char_length:] and '...'),
				'short_ipad_url': link.long_url_ipad[:max_char_length] + (link.long_url_ipad[max_char_length:] and '...'),
				'short_android_url': link.long_url_android[:max_char_length] + (link.long_url_android[max_char_length:] and '...'),
				'short_blackberry_url': link.long_url_blackberry[:max_char_length] + (link.long_url_blackberry[max_char_length:] and '...'),
				'short_windows_mobile_url': link.long_url_windows_mobile[:max_char_length] + (link.long_url_windows_mobile[max_char_length:] and '...'),
				'short_mac_url': link.long_url_mac[:max_char_length] + (link.long_url_mac[max_char_length:] and '...'),
				'short_pc_url': link.long_url_pc[:max_char_length] + (link.long_url_pc[max_char_length:] and '...'),
				'default_url': link.long_url_default,
				'iphone_url': link.long_url_iphone,
				'ipad_url': link.long_url_ipad,
				'android_url': link.long_url_android,
				'blackberry_url': link.long_url_blackberry,
				'windows_mobile_url': link.long_url_windows_mobile,
				'mac_url': link.long_url_mac,
				'pc_url': link.long_url_pc,
				'category': link.category,
				'description': link.description,
				'name': link.name,
				'short_link':link.short_link() + '.info',
				'qr_code':link.qrcode()
			}
			links.append(link_to_add)
	context = {'links':links}
	return render_to_response('ajax/links.html', locals(), context_instance = RequestContext(request=request, dict=context))

def ajax_devices(request):
	if not request.user.is_authenticated():
		raise Http404
	link_all = Link.objects.filter(user=request.user)
	if link_all:
		template = get_template('ajax/devices.html')
		if request.GET.get('begin_date'):
			begin_date_string = request.GET.get('begin_date')
			begin_date = datetime.datetime.strptime(begin_date_string, '%m/%d/%Y').date()
		else:
			begin_date = datetime.date.today() - datetime.timedelta(45)
		if request.GET.get('end_date'):
			end_date_string = request.GET.get('end_date')
			end_date = datetime.datetime.strptime(end_date_string, '%m/%d/%Y').date()
		else:
			end_date = datetime.date.today()
		if request.GET.get('link_id'):
			link = Link.objects.get(pk=request.GET.get('link_id'))
		else:
			link=None
		raw_device_data = get_devices(begin_date, end_date, request.user, link)
		raw_timeline_data = get_timeline(begin_date, end_date, request.user, link)
		unique_devices = get_unique_devices(begin_date, end_date, request.user, link)
		categories = get_unique_dates(begin_date, end_date)
		series = []
		colors = settings.GRAPH_COLORS

		#Devices Lines
		for index, d in enumerate(unique_devices):
			data = []
			found_one = False
			for c in date_range(begin_date, end_date):
				for s in raw_device_data:
					if s[2] == d[0] and c == s[1]:
						data.append(s[0])
						found_one = True
				if not found_one:
					data.append(0)
				found_one = False
			try:
				color = colors[index]
				new_series = {
					'name': d,
					'data': data,
					'color': color
				}
			except Exception:
				new_series = {
					'name': d,
					'data': data
				}
			series.append(new_series)

			#Pie Chart
			pie_data = []
			if not link:
				aggregate_device_data = LinkClick.objects.filter(date_time__range=[begin_date,end_date]).exclude(browser='').values('browser').annotate(Count('browser'))
			else:
				aggregate_device_data = LinkClick.objects.filter(date_time__range=[begin_date,end_date], link=link).exclude(browser='').values('browser').annotate(Count('browser'))
			for index, a in enumerate(aggregate_device_data):
				new_pie_data = {
					'name': a['browser'],
					'y': a['browser__count']
				}
				try:
					color = colors[index]
					new_pie_data['color'] = color
				finally :
					pie_data.append(new_pie_data)
			pie_series = {
				'type': 'pie',
				'name': 'Device Breakout',
				'data': pie_data,
				'center': [100, 80],
				'size': 100,
				'showInLegend': False,
				'dataLabels': {
					'enabled': False
				}
			}
			series.append(pie_series)

		#Total Line
		found_one = False
		data = []
		for c in date_range(begin_date, end_date):
			for s in raw_timeline_data:
				if c == s[1]:
					data.append(s[0])
					found_one = True
			if not found_one:
				data.append(0)
			found_one = False
		try:
			color = colors[len(unique_devices)]
			new_series = {
				'name': 'Total',
				'data': data,
				'color': color
			}
		except Exception:
			new_series = {
				'name': 'Total',
				'data': data
			}
		series.append(new_series)
		cont_dict = {
			'series': json.dumps(series),
			'categories': json.dumps(categories),
			'tick_interval': int(round(len(categories) / 4, 0)),
			'begin_date': format_date(begin_date),
			'end_date': format_date(end_date)
			}
		if link:
			cont_dict['link_id'] = link.pk
		context = Context(cont_dict, autoescape=False)
		return HttpResponse(template.render(context))
	return HttpResponse("You don't have any links. Create some to see the analytics!")

def ajax_locations(request):
	return HttpResponse("This feature isn't implemented yet. Stay tuned.")