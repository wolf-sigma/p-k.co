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

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import redirect_to
import shorturls

admin.autodiscover()

urlpatterns = patterns('',
	#url(r'^admin', redirect_to, {'url': '/admin/'}),
	url(r'^$', 'views.home', name='home'),
	url(r'^license', 'views.license', name='license'),
	url(r'^privacy', 'views.privacy', name='privacy'),
	url(r'^signup', 'views.signup', name='signup'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^ajax/', include('ajax.urls')),
	url(r'^create_link/', 'shorturls.views.create_link', name='createlink'),
	url(
        regex = '^links',
        view  = 'shorturls.views.links',
		name = 'links'
    ),
	url(
        regex = '^login',
        view  = 'django.contrib.auth.views.login',
		name = 'login'
    ),
	url(
        regex = '^logout',
        view  = 'views.logout',
		name = 'logout'
    ),
	url(
        regex = '^(?P<base64>\w+).qr',
        view  = 'shorturls.views.qr_code'
    ),
	url(
        regex = '^(?P<base64>\w+).info',
        view  = 'shorturls.views.url_info'
    ),
 	url(
        regex = '^(?P<base64>\w+)$',
        view  = 'shorturls.views.visit_url'
    ),
)

if settings.STATIC_DEBUG:
	urlpatterns += patterns('',
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
		'document_root': './static',
	})
)