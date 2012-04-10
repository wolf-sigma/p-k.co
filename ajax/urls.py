__author__ = 'Perrimark'

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('ajax.views',
	url(r'^links/', 'ajax_links'),
	url(r'^devices/', 'ajax_devices'),
	url(r'^locations', 'ajax_locations')
)