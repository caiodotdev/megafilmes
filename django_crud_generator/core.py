import codecs
import functools
import operator
import os
import shutil
import string

from django_crud_generator.conf import VIEW_CLASSES, MODULES_TO_INJECT, BASE_TEMPLATES_DIR, ACCOUNTS_LIST_TEMPLATES, \
    LIST_TEMPLATE_TAGS, LIST_THEME_DEFAULT_TEMPLATES
from django_crud_generator.html_manager.form_manager import get_attributes_display, get_block_form, get_inline_classes, \
    get_list_inlines, get_block_readonly_form, get_inlines_from_model, get_formsets, get_formsets_import, \
    get_attributes_related, get_attr_filter_display, get_attributes_filtered_with_relationship, get_search_general_attr, \
    get_list_display_form, get_code_upload_file
from django_crud_generator.html_manager.table_manager import get_header_table, get_body_table
from django_crud_generator.utils import convert, check_class_in_file


def render_file_by_template(path_to, path_initial_tmpl, path_body_tmpl, args):
    file = create_or_open(path_to,
                          path_initial_tmpl,
                          args)
    render_template_with_args_in_file(file,
                                      path_body_tmpl,
                                      **args)
    file.close()


def get_args(app, model, project_name, type):
    args = {'model_name': str(model.__name__), 'type': str(type),
            'model_prefix': str(model.__name__).upper(),
            'app_name': app, 'url_pattern': str(model.__name__).lower(),
            'project_name': str(project_name)}
    simplified_file_name = convert(str(model.__name__).strip())
    args['simplified_view_file_name'] = simplified_file_name
    args['model_name_lower'] = args['model_name'].lower()
    args['view_file'] = args['simplified_view_file_name']
    args['application_name'] = args['app_name'].split("/")[-1]
    args['list_display'] = get_attributes_display(model=model)
    args['list_display_form'] = get_list_display_form(model=model)
    args['code_upload'] = get_code_upload_file(model=model)
    args['list_filter_display'] = get_attr_filter_display(model=model)
    args['header_table'] = get_header_table(model=model, args=args)
    args['body_table'] = get_body_table(model=model, args=args)
    args['block_form'] = get_block_form(model=model) + get_block_html_inlines(model=model, args=args)
    args['block_select_script'] = get_block_select_script(model=model)
    args['search_general_attr'] = get_search_general_attr(model=model)
    args['formsets'] = get_formsets(model=model)
    args['formsets_import'] = get_formsets_import(model=model)
    args['block_readonly_form'] = get_block_readonly_form(model=model)
    args['list_inline_classes'] = get_inline_classes(model=model)
    return args


def create_templates_model(args):
    templates_crudl = VIEW_CLASSES.copy()
    templates_crudl.append('list_full')
    path_templates_model = os.path.join(args['app_name'], 'templates',
                                        convert(args['model_name'].strip().lower()))
    if not os.path.isdir(path_templates_model):
        os.mkdir(path_templates_model)
    for type_view in templates_crudl:
        template_path_type = os.path.join(args['app_name'], 'templates', convert(args['model_name'].strip().lower()),
                                          convert(type_view.strip().lower() + '.html'))
        body_path_template_tmpl = os.path.join('django_crud_generator', 'base_django', 'templates',
                                               args['type'], 'tmpl', convert(type_view.strip().lower() + '.html.tmpl'))
        render_file_by_template(
            template_path_type,
            None,
            body_path_template_tmpl,
            args
        )


def inject_modules(model, args):
    for module in MODULES_TO_INJECT:
        generic_insert_module(model, module, args)


def add_urls_in_project(args):
    print('-- Creating urls in project')
    render_file_by_template(
        os.path.join(args['project_name'], 'urls.py'),
        None,
        os.path.join(BASE_TEMPLATES_DIR, 'project_urls.py.tmpl'),
        args
    )


def add_utils_in_project(args):
    print('-- Adding Utils')
    render_file_by_template(
        os.path.join(args['app_name'], 'utils.py'),
        os.path.join(BASE_TEMPLATES_DIR, 'utils_initial.py.tmpl'),
        os.path.join(BASE_TEMPLATES_DIR, 'utils.py.tmpl'),
        args
    )


def copy_account_templates(args):
    if not os.path.isdir(os.path.join(args['app_name'], 'templates', 'account')):
        os.mkdir(os.path.join(args['app_name'], 'templates', 'account'))
    for basic in ACCOUNTS_LIST_TEMPLATES:
        original = os.path.join('django_crud_generator', 'base_django', 'templates', args['type'], 'account', basic)
        target = os.path.join(args['app_name'], 'templates', 'account')
        shutil.copy(original, target)


# DEPRECATED (IS NOT BEING USED)
def copy_templates_model(args):
    for type_view in VIEW_CLASSES:
        if not os.path.isdir(os.path.join(args['app_name'], 'templates',
                                          convert(args['model_name'].strip().lower()))):
            os.mkdir(os.path.join(args['app_name'], 'templates',
                                  convert(args['model_name'].strip().lower())))
        original = os.path.join('django_crud_generator', 'base_django', 'templates',
                                args['type'], 'model', convert(type_view.strip().lower() + '.html'))
        target = os.path.join(args['app_name'], 'templates', convert(args['model_name'].strip().lower()),
                              convert(type_view.strip().lower() + '.html'))
        shutil.copy(original, target)


def copy_templates_default(args):
    list_templates_default = LIST_THEME_DEFAULT_TEMPLATES
    for template_item in list_templates_default:
        original = os.path.join('django_crud_generator', 'base_django', 'templates', args['type'],
                                template_item)
        target = os.path.join(args['app_name'], 'templates', template_item)
        shutil.copy(original, target)


def copy_static_theme():
    original = os.path.join('django_crud_generator', 'static', 'default')
    target = os.path.join('static', 'default')
    if not os.path.isdir('static'):
        os.mkdir('static')
    try:
        shutil.copytree(original, target)
    except (FileExistsError,):
        print('-- Theme already exists in STATIC folder.')


def copy_template_tags(args):
    for item in LIST_TEMPLATE_TAGS:
        original = os.path.join('django_crud_generator', 'base_django', 'templatetags', item)
        target = os.path.join(args['app_name'], 'templatetags', item)
        if not os.path.isdir(os.path.join(args['app_name'], 'templatetags')):
            os.mkdir(os.path.join(args['app_name'], 'templatetags'))
            init_file = codecs.open(os.path.join(args['app_name'], 'templatetags', '__init__.py'), 'w+')
            init_file.close()
        shutil.copy(original, target)


def render_template_with_args_in_file(file, template_file_name, **kwargs):
    """
    Get a file and render the content of the template_file_name with kwargs in a file
    :param file: A File Stream to write
    :param template_file_name: path to route with template name
    :param **kwargs: Args to be rendered in template
    """
    template_file_content = "".join(codecs.open(template_file_name, encoding='UTF-8').readlines())
    template_rendered = string.Template(template_file_content).safe_substitute(**kwargs)
    file.write(template_rendered)


def create_or_open(file_name, initial_template_file_name, args):
    """
    Creates a file or open the file with file_name name
    :param file_name: String with a filename
    :param initial_template_file_name: String with path to initial template
    :param args: from console to determine path to save the files
    """
    if not os.path.isfile(file_name):
        file = codecs.open(file_name, 'w+', encoding='UTF-8')
        print("-- Creating {}".format(file_name))
        if initial_template_file_name:
            render_template_with_args_in_file(file, initial_template_file_name, **args)
    else:
        file = codecs.open(file_name, 'a+', encoding='UTF-8')
    return file


def generic_insert_module(model, module_name, args):
    """
    In general we have a initial template and then insert new data, so we dont repeat the schema for each module
    :param module_name: String with module name
    :paran **kwargs: Args to be rendered in template
    """
    if module_name == 'admin':
        create_inlines_into_admin(model, args)
    render_file_by_template(
        os.path.join(args['app_name'], '{}.py'.format(module_name)),
        os.path.join(BASE_TEMPLATES_DIR, '{}_initial.py.tmpl'.format(module_name)),
        os.path.join(BASE_TEMPLATES_DIR, '{}.py.tmpl'.format(module_name)),
        args
    )


def generic_insert_with_folder(folder_name, file_name, template_name, checking_classes, args):
    """
    In general if we need to put a file on a folder, we use this method
    """
    # First we make sure views are a package instead a file
    if not os.path.isdir(os.path.join(args['app_name'], folder_name)):
        os.mkdir(os.path.join(args['app_name'], folder_name))
        codecs.open(os.path.join(args['app_name'], folder_name, '__init__.py'), 'w+')
    full_file_name = os.path.join(args['app_name'], folder_name, '{}.py'.format(file_name))
    view_file = create_or_open(full_file_name, '', args)
    if functools.reduce(operator.and_,
                        map(check_class_in_file, (full_file_name,) * len(VIEW_CLASSES), checking_classes)):
        print("-- All classes {} already on file {}".format(", ".join(checking_classes), file_name))
        return 0
    render_template_with_args_in_file(
        view_file,
        os.path.join(
            BASE_TEMPLATES_DIR,
            template_name
        ),
        **args
    )
    view_file.close()
    return 1


def generate_templates_model(args):
    print('-- Generating templates model: ', args['model_name'])
    copy_templates_model(args)


def copy_dependencies(app_name):
    for item in ['requirements.txt', 'Procfile', '.gitignore', 'django.gitlab-ci.yml']:
        original = os.path.join('django_crud_generator', item)
        target = os.path.join(item)
        shutil.copy(original, target)


def delete_all_unused_files():
    list_files = ['views.py', 'tests.py', 'urls.py', 'admin.py', 'forms.py', 'conf.py',
                  'mixins.py', 'serializers.py', 'viewsets.py', 'urls_api.py', 'utils.py']
    for file in list_files:
        path_to_file = os.path.join('app', file)
        if os.path.exists(path_to_file):
            os.remove(path_to_file)


def create_inlines_into_admin(model, args):
    inlines = get_list_inlines(model)
    for inline in inlines:
        args['inline'] = str(inline)
        args['model_inline'] = args['inline'][:args['inline'].index('Inline')]
        render_file_by_template(
            os.path.join(args['app_name'], 'admin.py'),
            os.path.join(BASE_TEMPLATES_DIR, 'admin_initial.py.tmpl'),
            os.path.join(BASE_TEMPLATES_DIR, 'admin_inline.py.tmpl'),
            args
        )


def insert_menu_link(args):
    render_file_by_template(
        os.path.join(args['app_name'], 'templates', 'menu.html'),
        None,
        os.path.join(BASE_TEMPLATES_DIR, 'menu_item.html.tmpl'),
        args
    )


def get_block_html_inlines(model, args):
    block_inline = ''
    for inline in get_inlines_from_model(model):
        args['model_inline_prefix'] = str(inline).lower()
        args['model_inline'] = str(inline)
        block_inline += get_block_html_inline(args)
    return block_inline


def get_block_html_inline(args):
    template_file_name = os.path.join('django_crud_generator', 'base_django', 'templates',
                                      args['type'], 'tmpl', 'block_inline_form.html.tmpl')
    template_file_content = "".join(codecs.open(template_file_name, encoding='UTF-8').readlines())
    template_rendered = string.Template(template_file_content).safe_substitute(**args)
    return template_rendered


def get_block_select_script(model):
    template = ''
    path_script_tmpl = os.path.join(BASE_TEMPLATES_DIR, 'script_select.tmpl')
    template_file_content = "".join(codecs.open(path_script_tmpl, encoding='UTF-8').readlines())
    fields_model = get_attributes_filtered_with_relationship(model=model)
    select_attributes = ['id_' + str(field.split('__')[0].replace('"', '')) for field in fields_model if '__' in field]
    attributes = [str(field.split('__')[0].replace('"', '')) for field in fields_model if '__' in field]
    attributes_query = [str(field.split('__')[1].replace('"', '')) for field in fields_model if '__' in field]
    for i in range(len(select_attributes)):
        dic = {}
        dic['select_attribute'] = select_attributes[i]
        dic['attribute'] = attributes[i]
        dic['attribute_query'] = attributes_query[i]
        template += string.Template(template_file_content).safe_substitute(**dic)
    return template


def create_form_inlines(model, args):
    for inline in get_attributes_related(model):
        args['model_inline'] = str(inline)
        forms_path = os.path.join(args['app_name'], 'forms.py')
        render_file_by_template(
            forms_path,
            None,
            os.path.join(BASE_TEMPLATES_DIR, 'formset.py.tmpl'),
            args
        )
