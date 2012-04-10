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

class AddLinkForm(forms.Form):
	name = forms.CharField(required=True)
	long_url_default = forms.URLField(required=True)
	long_url_iphone = forms.URLField(required=False)
	long_url_android = forms.URLField(required=False)
	long_url_ipad = forms.URLField(required=False)
	long_url_windows_mobile = forms.URLField(required=False)
	long_url_blackberry = forms.URLField(required=False)
	long_url_pc = forms.URLField(required=False)
	long_url_mac = forms.URLField(required=False)
	#TODO: Add Category for reporting
	#category = forms.CharField(required=False)
	description = forms.CharField(required=False)
	public = forms.CheckboxInput()