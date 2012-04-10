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

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as log_out
from django.contrib.auth import login as log_in
from django.contrib.auth import authenticate
from django.template import Context, Template, RequestContext
from django.template.loader import get_template


from forms import *

def home(request):
	return render_to_response('index.html', locals(), context_instance = RequestContext(request=request))

def license(request):
	return render_to_response('license.html', locals(), context_instance = RequestContext(request=request))

def privacy(request):
	return render_to_response('privacy.html', locals(), context_instance = RequestContext(request=request))

def login(request):
	if request.method == 'POST':
		form = AuthenticationForm(request.POST)
		if form.is_valid():
			log_in(request, request.user)
			return HttpResponseRedirect('/links/') # Redirect after POST
	else:
		form = AuthenticationForm() # An unbound form
	c  ={'form':form}
	return render(request,'login.html', c)

def logout(request):
	log_out(request)
	return HttpResponseRedirect('/login')

def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			clean_data = form.cleaned_data
			user = User.objects.create_user(clean_data['username'], clean_data['email_address'], clean_data['password'])
			user.first_name = clean_data['first_name']
			user.last_name = clean_data['last_name']
			user.save()
			template = get_template('ajax/signup.json')
			context = Context({
				'success': 'true',
				'error_message': '',
				'redirect_url': '/links/'
			})
			auth_user = authenticate(username=clean_data['username'], password=clean_data['password'])
			log_in(request, auth_user)
			return HttpResponse(template.render(context), mimetype='application/json')
		else:
			template = get_template('ajax/signup.json')
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