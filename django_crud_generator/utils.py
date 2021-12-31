import ast
import json
import os
import re
import sys
from base64 import b64encode

import pyimgur
import requests
from django.db.models import (
    CharField,
    TextField,
    IntegerField,
    FloatField,
    EmailField,
    ForeignKey,
    FileField,
    DateTimeField,
    DateField,
    AutoField,
    BooleanField,
    ManyToManyField, ImageField
)
from django.forms.widgets import (
    Textarea,
    NumberInput,
    EmailInput,
    Input,
    Select,
    TextInput,
    FileInput,
    DateTimeInput,
    DateInput,
    HiddenInput,
    CheckboxInput,
    CheckboxSelectMultiple,
)

import random
import string
import csv


def generate_random_string(n):
    """
    Generates a random string of length n
    :param n: Length of string
    :return: Random string
    """
    return ''.join(random.choices(string.ascii_lowercase, k=n))


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    """
    CSV reader for UTF-8 documents
    :param unicode_csv_data: Data of CSV
    :param dialect: Dialect of CSV
    :param kwargs: Other args
    :return:
    """
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [str(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    """
    UTF-8 Encoder
    :param unicode_csv_data:
    :return: Generator of UTF-8 encoding
    """
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def field_to_widget(field):
    if type(field) is CharField:
        if field.choices:
            return Select(attrs={"class": "form-control"})
        return TextInput(attrs={"class": "form-control", "rows": 1})
    if type(field) is TextField:
        return Textarea(attrs={"class": "form-control", "rows": 5})
    if type(field) is AutoField:
        return HiddenInput(attrs={"class": "form-control", "rows": 1})
    if type(field) is IntegerField or type(field) is FloatField:
        return NumberInput(attrs={"class": "form-control"})
    if type(field) is EmailField:
        return EmailInput(attrs={"class": "form-control"})
    if type(field) is ForeignKey:
        return Select(attrs={"class": "form-control"})
    if type(field) is ManyToManyField:
        return CheckboxSelectMultiple(attrs={"class": ""},
                                      choices=((model.id, model) for model in field.related_model.objects.all()))
    if type(field) is BooleanField:
        return CheckboxInput(attrs={"class": ""})
    if type(field) is FileField:
        return TextInput(attrs={"class": "form-control fileinput", "type": "file"})
    if type(field) is ImageField:
        return TextInput(
            attrs={"class": "form-control imageinput", "type": "file", "accept": ".jpg, .jpeg, .png, .ico"})
    if type(field) is DateField:
        return TextInput(attrs={"class": "form-control datepicker date", "type": "date"})
    if type(field) is DateTimeField:
        return TextInput(attrs={"class": "form-control datetimepicker datetime", "type": "date"})
    if field.one_to_one:
        return Select(attrs={"class": "form-control"},
                      choices=((model.id, model) for model in field.related_model.objects.all()))

    return TextInput(attrs={"class": "form-control", "rows": 1})


def generate_bootstrap_widgets_for_all_fields(model):
    return {x.name: field_to_widget(x) for x in model._meta.get_fields()}


def convert(name):
    """
    This function converts a Camel Case word to a underscore word
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def check_class_in_file(file_path, class_name):
    try:
        file_to_scan = open(file_path)
        content = file_to_scan.read()
        parsed_tree = ast.parse(content)
        model_exists = False
        for node in ast.walk(parsed_tree):
            if isinstance(node, ast.ClassDef):
                if node.name == class_name:
                    model_exists = True
        return model_exists
    except IOError:
        print("File {} can't be open".format(file_path))
        sys.exit(1)


def sanity_check(args):
    """
    Verify if the work folder is a django app.
    A valid django app always must have a models.py file
    :return: None
    """
    if not os.path.isfile(os.path.join(args['app_name'], 'models.py')):
        print("app_name is not a Django application folder")
        sys.exit(1)
    models_file_path = os.path.join(args['app_name'], 'models.py')
    if not check_class_in_file(models_file_path, args["model_name"]):
        print("Model does not exists")
        sys.exit(1)


def upload_image(request, attribute='file'):
    """
    This method has upload file.
    """
    try:
        CLIENT_ID = "cdadf801dc167ab"
        data = b64encode(request.FILES[attribute].read())
        client = pyimgur.Imgur(CLIENT_ID)
        r = client._send_request('https://api.imgur.com/3/image', method='POST', params={'image': data})
        return r['link']
    except (Exception,):
        return 'http://placehold.it/1024x800'


def upload_file(request, attribute='file'):
    try:
        url_upload = "https://content.dropboxapi.com/2/files/upload"
        name = "/" + str(request.FILES[attribute].name)
        headers_upload = {
            "Authorization": "Bearer M6iN1nYzh_YAAAAAAACHm34PsRKmgPWvVI6uSALYMTqZxGUcopC4pr7K7OkfFfaZ",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": "{\"path\":\"" + name + "\"}"
        }
        data_upload = b64encode(request.FILES[attribute].read())
        response = requests.post(url_upload, headers=headers_upload, data=data_upload)
        print(response.json())
        if response.status_code == 200 or response.status_code == 201:
            url_link = "https://api.dropboxapi.com/2/sharing/create_shared_link"
            headers_link = {
                "Authorization": "Bearer M6iN1nYzh_YAAAAAAACHmqe-TsJhb-Dur_EB09HNKaguknUwnq2a_PprLOwiSS3W",
                "Content-Type": "application/json"
            }
            data_link = {
                "path": "/Apps/pagseguroarquivos" + name,
                "short_url": False
            }
            response_link = requests.post(url_link, headers=headers_link, data=json.dumps(data_link))
            return response_link.json()['url']
        return 'http://placehold.it/1024x800'
    except (Exception,):
        return 'http://placehold.it/1024x800'
