# -*- coding: utf-8 -*-
import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, EmailValidator, validate_email
from django.utils.translation import ugettext_lazy as _
from bootstrap3_datetime.widgets import DateTimePicker
from netaddr import IPNetwork

from AAPT.settings import valid_domains

my_default_errors_IP = {
    'invalid': _(u'Insert a valid IPs or Networks combination. '),
    'domain': _(u'Some of the IPs is not valid to be scanned. '),
    'network': _(u'You are not allowed to insert a full network, please contact your administrator if you need this permission. ')
}

my_default_errors_URL = {
    'invalid': _(u'Insert a valid domain combination. '),
    'out_of_range': _(u'The domain name can not exceed 255 characters. ')
}

my_default_errors_Name = {
    'required': _(u'Specify a task name. ')
}

Profiles = (('Fast Scan', 'Fast scan'), ('Full Audit', 'Full Audit'), ('OWASP Top 10', 'OWASP Scan'))
Target_OSs = (('unknown', 'unknown'), ('unix', 'unix'), ('windows', 'windows'))
Target_frameworks = (
    ('unknown', 'unknown'), ('php', 'php'), ('asp', 'asp'), ('asp.net', 'asp.net'), ('java', 'java'),
    ('jsp', 'jsp'), ('cfm', 'cfm'), ('ruby', 'ruby'), ('perl', 'perl'))

Methods = (('POST', 'POST'), ('GET', 'GET'))


def can_risk(user):
    return user.has_perm('w3af.w3af_highrisk')


def full_domain_validator(hostname):
    """
    Fully validates a domain name as compilant with the standard rules:
        - Composed of series of labels concatenated with dots, as are all domain names.
        - Each label must be between 1 and 63 characters long.
        - The entire hostname (including the delimiting dots) has a maximum of 255 characters.
        - Only characters 'a' through 'z' (in a case-insensitive manner), the digits '0' through '9'.
        - Labels can't start or end with a hyphen.
    """
    HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)
    if not hostname:
        return
    if len(hostname) > 255:
        return -1
    if hostname[-1:] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    for label in hostname.split("."):
        if not HOSTNAME_LABEL_PATTERN.match(label):
            return -2
    return 1


class w3afForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(w3afForm, self).__init__(*args, **kwargs)

    def validate_target_os(value):
        if value != "unknown" and value != "unix" and value != "windows":
            raise ValidationError(_(u'Target OS not valid'))

    def validate_target_framework(value):
        if value != "unknown" and value != "php" and value != "asp" and value != "asp.net" and value != "java" and value != "jsp" and value != "cfm" and value != "ruby" and value != "perl":
            raise ValidationError(_(u'Target framework not valid'))

    def validate_profile(value):
        if value != "Fast Scan" and value != "Full Audit" and value != "OWASP Top 10":
            raise ValidationError(_(u'Target framework not valid'))

    def validate_method(value):
        if value != "GET" and value != "POST":
            raise ValidationError(_(u'Method not valid'))

    def validate_url(value):
        #Treient https://
        parts = value.split('/')
        for p in parts:
            print(p)
        if parts[0] == "http:" or parts[0] == "https:":
            domain = parts[2]
        else:
            domain = parts[0]

        #Treient port
        parts = domain.split(':')
        domain = parts[0]

        i = full_domain_validator(domain)
        if i == -1:
            raise ValidationError(_(my_default_errors_URL['out_of_range']))
        elif i == -2:
            raise ValidationError(_(my_default_errors_URL['domain']))
        elif i == -3:
            raise ValidationError(_(my_default_errors_URL['invalid']))

    name = forms.CharField(widget=forms.TextInput(attrs={"label": 'Name:', "max_length": 100, "class": "form-control",
                                                         "placeholder": 'Task Name'}),
                           error_messages=my_default_errors_Name)

    target = forms.URLField(widget=forms.TextInput(attrs={"label": 'URL:', "max_length": 100, "class": "form-control",
                                                       "placeholder": 'http(s)://targeturl[:port]/[...]'}),
                            error_messages=my_default_errors_URL, validators=[validate_url])

    target_os = forms.ChoiceField(widget=forms.Select(attrs={"label": 'OS:'}), choices=Target_OSs,
                                validators=[validate_target_os])

    target_framework = forms.ChoiceField(widget=forms.Select(attrs={"label": 'Framework:'}), choices=Target_frameworks,
                                validators=[validate_target_framework])

    profile = forms.ChoiceField(widget=forms.Select(attrs={"label": 'Profile:'}), choices=Profiles,
                                         validators=[validate_profile])

    login_url = forms.URLField(widget=forms.TextInput(attrs={"label": 'URL:', "max_length": 100, "class": "form-control",
                                                       "placeholder": 'http(s)://loginurl[:port]/[...]'}),
                            error_messages=my_default_errors_URL, validators=[validate_url], required=False)

    login_username = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}), required=False)
    login_password = forms.CharField(widget=forms.PasswordInput(attrs={"max_length": 100, "class": "form-control"}), required=False)
    login_userfield = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}), required=False)
    login_passwordfield = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}), required=False)

    login_method = forms.ChoiceField(widget=forms.Select(attrs={"label": 'Method:'}), choices=Methods,
                                         validators=[validate_method])

    http_user = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}),
                                     required=False)
    http_password = forms.CharField(widget=forms.PasswordInput(attrs={"max_length": 100, "class": "form-control"}),
                                     required=False)
    http_domain = forms.URLField(
        widget=forms.TextInput(attrs={"label": 'Auth URL:', "max_length": 100, "class": "form-control",
                                      "placeholder": 'http(s)://authurl[:port]/[...]'}),
        error_messages=my_default_errors_URL, validators=[validate_url], required=False)

    mail = forms.BooleanField(label='mail', initial=False, required=False)
    mail_field = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}), required=False, validators=[validate_email])

    def clean(self):
        cleaned_data = super(w3afForm, self).clean()
        #url = cleaned_data.get("url")
