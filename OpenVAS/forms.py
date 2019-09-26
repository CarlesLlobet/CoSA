# -*- coding: utf-8 -*-
import re

from bootstrap3_datetime.widgets import DateTimePicker
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, EmailValidator, validate_email
from django.utils.translation import ugettext_lazy as _
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

ScanConfigs = (
    ('Discovery', 'Discovery'),
    ('Full and fast', 'Full and fast'),
    ('Full and fast ultimate', 'Full and fast ultimate'),
    ('Full and very deep', 'Full and very deep'),
    ('Full and very deep ultimate', 'Full and very deep ultimate'))


def can_network(user):
    return user.has_perm('OpenVAS.openvas_wholenetwork')

def can_ultimate(user):
    return user.has_perm('OpenVAS.openvas_ultimate')

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

class OpenVASForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OpenVASForm, self).__init__(*args, **kwargs)

    def validate_urls(value):
        url = value.replace(" ", "").split(",")
        for u in url:
            i = full_domain_validator(u)
            if i == -1:
                raise ValidationError(_(my_default_errors_URL['out_of_range']))
            elif i == -2:
                raise ValidationError(_(my_default_errors_URL['invalid']))

    def validate_config(value):
        if value != "Discovery" and value != "Full and fast" and value != "Full and fast ultimate" and value != "Full and very deep" and value != "Full and very deep ultimate":
            raise ValidationError(_(u'Scanning type is not valid'))

    def validate_ips(value):
        if value != "":
            ip = value.replace(" ", "").split(",")
            print("IP is not null")
            for i in ip:
                try:
                    IPNetwork(i)
                except:
                        raise ValidationError(_(my_default_errors_IP['invalid']))
                else:
                    b = False
                    for d in valid_domains:
                        print("Testing if IP is in a valid domain " + d)
                        if IPNetwork(i).ip in IPNetwork(d):
                            print("The ip " + i + "is from network" + d)
                            b = True
                    if not b:
                        print("IP is not from any valid domain")
                        raise ValidationError(_(my_default_errors_IP['domain']))

    urls = forms.CharField(widget=forms.TextInput(attrs={"label": 'URLs:', "class": "form-control",
                    "placeholder": 'Example format: client.com,subdomain.client.com[, ...]'}),
                    error_messages=my_default_errors_URL, required=False, validators=[validate_urls])

    name = forms.CharField(widget=forms.TextInput(attrs={"label": 'Name:', "max_length": 100, "class": "form-control",
                                                         "placeholder": 'Test name'}),error_messages=my_default_errors_Name)

    ips = forms.CharField(widget=forms.TextInput(
        attrs={"label": 'IPs:', "class": "form-control",
               "placeholder": 'Example format: 147.83.74.3,147.83.13.2[, ...]'}),
                error_messages=my_default_errors_IP, required=False, validators=[validate_ips])

    config = forms.ChoiceField(widget=forms.Select(attrs={"label": 'Charset:'}), choices=ScanConfigs,
                                validators=[validate_config])

    mail = forms.BooleanField(label='mail',initial=False, required=False)

    mail_field = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}), required=False, validators=[validate_email])

    def clean(self):
        cleaned_data = super(OpenVASForm, self).clean()
        urls = cleaned_data.get("urls")
        ips = cleaned_data.get("ips")
        config = cleaned_data.get("config")

        if (config == "Full and fast ultimate" or config == "Full and very deep ultimate")and (not can_ultimate(self.user)):
            raise forms.ValidationError(
                 _("You are not allowed to scan in Ultimate mode, please contact your administrator if you need this permission. "))

        if urls=="" and ips=="":
            raise forms.ValidationError(_("Please specify at least 1 target, by URL, by IP or both"))

        if (ips is not None):
            ip = ips.replace(" ", "").split(",")
            for i in ip:
                if i != "":
                    try:
                        validate_ipv4_address(i)
                    except:
                        if not can_network(self.user):
                            raise ValidationError(_((my_default_errors_IP['network'])))



