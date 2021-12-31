#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
Global variables for base module
"""
import os

from django.utils.translation import ugettext_lazy as _
from django.conf import LazySettings

settings = LazySettings()


def get_from_settings_or_default(var_name, default):
    try:
        return settings.__getattr__(var_name)
    except AttributeError:
        return default


# Items by page on paginator views
ITEMS_BY_PAGE = 10

CREATE_SUFFIX = "_create"
LIST_SUFFIX = "_list"
DETAIL_SUFFIX = "_detail"
UPDATE_SUFFIX = "_update"
DELETE_SUFFIX = "_delete"

API_SUFFIX = "_api"

# Messages
OBJECT_CREATED_SUCCESSFULLY = _("Object created successfully")
OBJECT_UPDATED_SUCCESSFULLY = _("Object updated successfully")
OBJECT_DELETED_SUCCESSFULLY = _("Object deleted successfully")

BASE_MODELS_TRANSLATION_NAME = _("Name")
BASE_MODELS_TRANSLATION_DESCRIPTION = _("Description")
BASE_MODELS_TRANSLATION_SLUG = _("Slug")
BASE_MODELS_TRANSLATION_CREATED = _("Created")
BASE_MODELS_TRANSLATION_MODIFIED = _("Modified")
BASE_MODELS_TRANSLATION_ACTIVE = _("Active")

CONFIGURING_APPLICATION = _("Configuring application {}")
CREATING_PERMISSION_WITH_NAME = _("Creating Permission with name {}")
CREATING_GROUP_WITH_NAME = _("Creating Group with name {}")

BASE_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
VIEW_CLASSES = [
    "List",
    "Create",
    "Detail",
    "Update",
    "Delete"
]

MODULES_TO_INJECT = [
    'conf',
    'admin',
    'forms',
    'urls',
    'mixins',
    'serializers',
    'viewsets',
    'urls_api'
]

ACCOUNTS_LIST_TEMPLATES = ['login.html', 'password_change.html', 'password_reset.html', 'signup.html']
LIST_DASHBOARD_DEFAULT_TEMPLATES = ['404.html', '500.html', 'base.html', 'base_error.html', 'loading.html',
                                    'breadcrumb.html', 'menu.html']
LIST_APP_DEFAULT_TEMPLATES = ['404.html', '500.html', 'base.html', 'footer.html', 'header.html', 'nav.html', ]
LIST_TEMPLATE_TAGS = ['form_utils.py', 'input_checker.py', 'math_utils.py', 'type_utils.py', 'my_tags.py']
LIST_THEME_DEFAULT_TEMPLATES = ['404.html', '500.html', 'base.html', 'loading.html', 'menu.html']
