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

from django import forms
from django.contrib.auth.models import *
from django.core.exceptions import ValidationError

def validate_username(value):
	user_check_uname = User.objects.filter(username__iexact=value).all()
	if user_check_uname:
		raise ValidationError(u'%s is already in use. Please try a different one.' % value)

def validate_email(value):
	user_check_email = User.objects.filter(email__iexact=value).all()
	if user_check_email:
		raise ValidationError(u'%s is already in use. Try resetting your password.' % value)

class SignupForm(forms.Form):
	first_name = forms.CharField()
	last_name = forms.CharField()
	username = forms.CharField(validators=[validate_username])
	email_address = forms.EmailField(validators=[validate_email])
	password = forms.CharField(widget=forms.PasswordInput)
	confirm_password = forms.CharField(widget=forms.PasswordInput)