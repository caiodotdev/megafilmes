import os

from django.apps import apps

from django_crud_generator.conf import VIEW_CLASSES
from django_crud_generator.core import get_args, generic_insert_with_folder, inject_modules, copy_account_templates, \
    copy_template_tags, copy_static_theme, copy_templates_default, copy_dependencies, \
    create_templates_model, add_urls_in_project, insert_menu_link, add_utils_in_project, create_form_inlines
from django_crud_generator.utils import check_class_in_file, sanity_check


def has_templates_default(app_name):
    return os.path.isfile(os.path.join(app_name, 'templates', 'menu.html'))


def generate_all_models(app_name, project_name, type='dashboard'):
    models = apps.get_app_config(app_name).get_models()
    if not has_templates_default(app_name):
        add_urls_in_project({'project_name': project_name})
        add_utils_in_project({'app_name': app_name})
        generate_default_templates(app_name, type)
    for model in models:
        generate_for_model(app_name, model.__name__, project_name, type)


# TODO: Bug ao rodar generate 2x.
def generate_for_model(app_name, model, project_name, type='dashboard'):
    model = apps.get_model(app_name, model)
    args = get_args(app_name, model, project_name, type)
    models_file_path = os.path.join(args['app_name'], 'models.py')
    if check_class_in_file(models_file_path, str(model.__name__)):
        sanity_check(args)
        generic_insert_with_folder("views", args["simplified_view_file_name"], "view.py.tmpl", VIEW_CLASSES, args)
        permission_class_name = "{}Permission".format(args["model_name"])
        flag = generic_insert_with_folder("tests", "test_{}".format(args["simplified_view_file_name"]), "tests.py.tmpl",
                                          [permission_class_name], args)
        if flag != 0:
            create_templates_model(args)
            insert_menu_link(args)
            inject_modules(model, args)
            create_form_inlines(model, args)


def generate_default_templates(app_name, type='dashboard'):
    args = {'type': type, 'app_name': app_name}
    copy_static_theme()
    copy_templates_default(args)
    copy_account_templates(args)
    copy_template_tags(args)


def copy_deps(app_name):
    copy_dependencies(app_name)
