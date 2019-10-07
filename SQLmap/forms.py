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

DBMSs = (
    ('mysql', 'MySQL'),
    ('oracle', 'Oracle'),
    ('sqlserver', 'Microsoft SQL Server'),
    ('postgre', 'PostgreSQL')
)

CharSets = (
    ('UTF-8', 'UTF-8'),
    ('US-ASCII', 'US-ASCII'),
    ('UTF-16BE', 'UTF-16BE'),
    ('UTF-16LE', 'UTF-16LE'),
    ('UTF-16', 'UTF-16')
)


def can_risk(user):
    return user.has_perm('SQLmap.sqlmap_highrisk')


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


class SQLmapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SQLmapForm, self).__init__(*args, **kwargs)

    def validate_dbms(value):
        if value != "mysql" and value != "oracle" and value != "sqlserver" and value != "postgre":
            raise ValidationError(_(u'DBMS not valid'))

    def validate_charset(value):
        if value != "UTF-8" and value != "US-ASCII" and value != "UTF-16BE" and value != "UTF-16LE" and value != "UTF-16":
            raise ValidationError(_(u'Charset not valid'))

    def validate_url(value):
        # Treient https://
        parts = value.split('/')
        for p in parts:
            print(p)
        if parts[0] == "http:" or parts[0] == "https:":
            domain = parts[2]
        else:
            domain = parts[0]

        # Treient port
        parts = domain.split(':')
        domain = parts[0]

        i = full_domain_validator(domain)
        if i == -1:
            raise ValidationError(_(my_default_errors_URL['out_of_range']))
        elif i == -2:
            raise ValidationError(_(my_default_errors_URL['domain']))
        elif i == -3:
            raise ValidationError(_(my_default_errors_URL['invalid']))

    def validate_ip(value):
        try:
            validate_ipv4_address(value)
        except:
            raise ValidationError(_(my_default_errors_IP['invalid']))
        else:
            b = False
            for d in valid_domains:
                if value in IPNetwork(d):
                    b = True
            if not b:
                raise ValidationError(_(my_default_errors_IP['domain']))

    def validate_port(value):
        print(value)
        if value < 1024 or value > 65535:
            raise ValidationError(_(u'Port no vàlid'))


    url = forms.URLField(widget=forms.TextInput(attrs={"label": 'URL:', "max_length": 100, "class": "form-control",
                                                       "placeholder": 'http(s)://targeturl[:port]/[...]'}),
                         required=False, error_messages=my_default_errors_URL, validators=[validate_url])

    dbms = forms.ChoiceField(widget=forms.Select(attrs={"label": 'DBMS:'}), choices=DBMSs, required=False,
                             validators=[validate_dbms])

    name = forms.CharField(widget=forms.TextInput(attrs={"label": 'Name:', "max_length": 100, "class": "form-control",
                                                         "placeholder": 'Task Name'}),
                           error_messages=my_default_errors_Name)

    user = forms.CharField(widget=forms.TextInput(attrs={"label": 'User:', "max_length": 100, "class": "form-control",
                                                         "placeholder": "Username"}), required=False)

    password = forms.CharField(widget=forms.PasswordInput(attrs={"label": 'Password:', "max_length": 100,
                                                                 "class": "form-control", "placeholder": 'Password'}),
                               required=False)

    ip = forms.CharField(widget=forms.TextInput(attrs={"label": 'IP:', "max_length": 15, "class": "form-control",
                                                       "placeholder": 'Example format: 147.83.74.0'}),
                         required=False,
                         validators=[validate_ip])

    port = forms.IntegerField(widget=forms.TextInput(attrs={"label": 'Port:', "max_length": 5, "class": "form-control",
                                                            "placeholder": 'Example format: 5432'}), required=False,
                              validators=[validate_port])

    db_name = forms.CharField(widget=forms.TextInput(attrs={"label": 'Database Name:', "max_length": 100,
                                                            "class": "form-control",
                                                            "placeholder": 'Example format: myDB'}), required=False)

    charset = forms.ChoiceField(widget=forms.Select(attrs={"label": 'Charset:'}), choices=CharSets,
                                validators=[validate_charset])

    verbosity = forms.IntegerField(label='verbosity')
    level = forms.IntegerField(label='level')
    risk = forms.IntegerField(label='risk')
    depth = forms.IntegerField(label='depth')
    mail = forms.BooleanField(label='mail', initial=False, required=False)
    mail_field = forms.CharField(widget=forms.TextInput(attrs={"max_length": 100, "class": "form-control"}), required=False, validators=[validate_email])

    def clean(self):
        cleaned_data = super(SQLmapForm, self).clean()
        url = cleaned_data.get("url")
        user = cleaned_data.get("user")
        password = cleaned_data.get("password")
        ip = cleaned_data.get("ip")
        port = cleaned_data.get("port")
        db_name = cleaned_data.get("db_name")
        verbosity = cleaned_data.get("verbosity")
        level = cleaned_data.get("level")
        risk = cleaned_data.get("risk")
        depth = cleaned_data.get("depth")

        print(port)
        if risk == 3 and (not can_risk(self.user)):
            raise forms.ValidationError(
                _("You are not allowed to put this risk, please contact your administrator if you need this permission. "))
        if url == "" and user == "" and password == "" and ip == "" and port == None and db_name == "":
            raise forms.ValidationError(
                _("Please specify at least 1 target, by URL, by IP or direct connection to the Database"))
        if url == "" and user == "" and (password != "" or ip != "" or port != None or db_name != ""):
            self.add_error('user', (_("Specify a username")))
        if url == "" and password == "" and (user != "" or ip != "" or port != None or db_name != ""):
            self.add_error('password', (_("Specify a password")))
        if url == "" and ip == "" and (password != "" or user != "" or port != None or db_name != ""):
            self.add_error('ip', (_("Specify an IP address")))
        if url == "" and port == None and (password != "" or ip != "" or user != "" or db_name != ""):
            self.add_error('port', (_("Specify a port")))
        if url == "" and db_name == "" and (password != "" or ip != "" or port != None or user != ""):
            self.add_error('db_name', (_("Specify a Database name")))
        if verbosity < 0 or verbosity > 6 or level < 1 or level > 5 or risk < 1 or risk > 3 or depth < 0 or depth > 10:
            print(str(verbosity) + ", " + str(level) + ", " + str(risk) + ", " + str(depth))
            raise forms.ValidationError(
                _("Fields level, verbosity, risk and depth can not have values outside of the slider"))
