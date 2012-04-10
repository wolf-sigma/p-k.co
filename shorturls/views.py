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

from shorturls.utils import *
from shorturls import models
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from chartit import PivotChart, PivotDataPool
from django.db.models import Count
from forms import *
import datetime
import simplejson


@csrf_exempt
def visit_url(request, base64):
	url = get_url(request,base64)
	if url:
		return HttpResponseRedirect(url)
	else:
		raise Http404

@csrf_exempt
def qr_code(request, base64):
	link_all = Link.objects.filter(base64=base64)
	if link_all:
		link=link_all[0]
		template = get_template('qr_code.html')
		return HttpResponse(template.render(Context({'qr_code':link.qrcode()})))
	else:
		raise Http404

@csrf_exempt
def url_info(request, base64):
	link_all = Link.objects.filter(base64=base64)
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	if link_all:
		link=link_all[0]
		if not link.user == request.user:
			four_oh_three = get_template('403.html')
			context = Context({})
			return HttpResponse(four_oh_three.render(context))
		raw_device_select_data = {"d": "DATE (date_time)"}
		raw_device_data = LinkClick.objects.filter(link=link).extra(select=raw_device_select_data).all()
		device_data = PivotDataPool(
			series=[
				{
					'options':{
						'source':raw_device_data,
						'categories': 'date',
						'legend_by': 'browser'
					},
					'terms':{
						'clicks': Count('id')
					}
				}
			]
		)
		device_chart = PivotChart(
			datasource=device_data,
			series_options=[
				{
					'options':{
						'type':'column',
						'stacking': True
					},
					'terms':['clicks']
				}
			],
			chart_options={
				'yAxis':{
					'title':{'text':'clicks'}
				},
				'title':{'text': 'Devices'}
			}
		)
		max_char_length = 55
		dict_context = {
			'base_64': base64,
			'device_chart': device_chart,
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
			'short_link':link.short_link(),
			'qr_code':link.qrcode(),
			'link_id': link.pk
		}
		return render_to_response('url_info.html', locals(), context_instance = RequestContext(request=request, dict=dict_context))
	else:
		raise Http404
	
def links(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	else:
		form = AddLinkForm()
		context_r = {'form':form}
		return render_to_response('links.html', locals(), context_instance = RequestContext(request=request, dict=context_r))

@csrf_exempt
def create_link(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/')
	if request.method == 'POST':
		form = AddLinkForm(request.POST)
		if form.is_valid():
			clean_data = form.cleaned_data
			name = clean_data['name']
			long_url_default = clean_data['long_url_default']
			long_url_iphone = clean_data['long_url_iphone']
			long_url_ipad = clean_data['long_url_ipad']
			long_url_android = clean_data['long_url_android']
			long_url_windows_mobile = clean_data['long_url_windows_mobile']
			long_url_blackberry = clean_data['long_url_blackberry']
			long_url_pc = clean_data['long_url_pc']
			long_url_mac = clean_data['long_url_mac']
			description = clean_data['description']
			#TODO: Add Public to add form
			#public = clean_data['public']
			link = Link(name=name, long_url_iphone=long_url_iphone, long_url_ipad=long_url_ipad,
						long_url_default=long_url_default, long_url_android=long_url_android,
						long_url_windows_mobile=long_url_windows_mobile,long_url_blackberry=long_url_blackberry,
						long_url_pc=long_url_pc,long_url_mac=long_url_mac,description=description, user=request.user)
			link.save()
			template = get_template('ajax/create_link.json')
			context = Context({
				'success': 'true',
				'error_message': '',
				'redirect_url': '/links/'
			})
			return HttpResponse(template.render(context), mimetype='application/json')
		else:
			template = get_template('ajax/create_link.json')
			form_errors = form.errors
			errors = []
			for form_error in form_errors:
				to_add_error = {
					"field": form_error,
					"error": form_errors[form_error][0]
				}
				errors.append(to_add_error)
			context = Context({
				'success': 'false',
				'errors': errors,
				'redirect_url': ''
			})
			toReturn = template.render(context)
			return HttpResponse(toReturn, mimetype='application/json')
	else:
		return HttpResponseRedirect('/')