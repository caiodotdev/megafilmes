import string

from django.db.models import ManyToOneRel, ManyToManyField, ManyToManyRel, ForeignKey, \
    CharField, URLField, FileField, ImageField, TextField


def get_label_html(attr):
    """
    This method generate an label html for attribute.
    """
    LABEL_TAG = '<label>{}:</label> \n'
    return LABEL_TAG.format(str(attr).capitalize())


def get_form_html(attr):
    """
    This create a {{ form.attr }} for an attribute. This is most used into Create or Update template.
    """
    dic = {'attribute': attr}
    form = string.Template('{{ form.${attribute} }} \n').safe_substitute(**dic)
    return form


def get_readonly_form_html(attr):
    """
    This create a readonly code for an attribute like: {{ object.attr }}. This is most used into DetailView template.
    """
    dic = {'attribute': attr}
    form = string.Template('\n{{ object.${attribute} }} \n').safe_substitute(**dic)
    return form


def make_group_form_html(attr):
    """
    This create a div form group for an attribute editable. This is most used into Create or Update template.
    """
    block = get_label_html(attr) + get_form_html(attr)
    dic = {'block': block}
    group = string.Template('<div class="form-group"> \n ${block} </div>').safe_substitute(**dic)
    return group


def make_group_readonly_form_html(attr):
    """
    This create a div form group for an attribute readonly. This is most used into DetailView template.
    """
    block = get_label_html(attr) + get_readonly_form_html(attr)
    dic = {'block': block}
    group = string.Template('<div class="form-group"> \n ${block} </div>').safe_substitute(**dic)
    return group


def make_column_form(attr, length_col=12):
    """
    This create a div columns for an attribute block. This is most used into Create or Update template.
    """
    form_group_attr = make_group_form_html(attr)
    length_col = 'col-xs-' + str(length_col)
    dic = {'block': form_group_attr}
    column = string.Template('<div class="' + length_col + '"> \n ${block} \n </div> \n').safe_substitute(**dic)
    return column


def make_readonly_column_form(attr, length_col=4):
    """
    This create a div column for an attribute block. This is most used into DetailView template.
    """
    form_group_attr = make_group_readonly_form_html(attr)
    length_col = 'col-xs-' + str(length_col)
    dic = {'block': form_group_attr}
    column = string.Template('<div class="' + length_col + '"> \n ${block} \n </div> \n').safe_substitute(**dic)
    return column


def get_block_readonly_form(model):
    """
    This method get all attributes for show in DetailView template, except ID or PK.
    """
    attributes_model = [make_readonly_column_form(str(f.name)) for f in model._meta.get_fields() if
                        f.editable and str(f.name).lower() != 'id']
    block_form = "".join(map(str, attributes_model))
    return block_form


def get_related_script(model):
    """
    This method get an attributes array of model, including related attributes (by related_model).
    """
    arr = []
    attributes = get_attributes_filter_model(model=model)
    for f in attributes:
        field = f.__dict__
        if 'related_model' in field:
            related_model = f.related_model
            arr.append(f.name)
    return arr


def get_block_form(model):
    """
    This method get all attributes of model for create a block for Update or Create View template. (except ID or PK).
    """
    attributes_model = [make_column_form(str(f.name)) for f in model._meta.get_fields() if
                        f.editable and str(f.name).lower() != 'id']
    block_form = "".join(map(str, attributes_model))
    return block_form


def get_attributes_model(model):
    """
    This method get all attributes of model, but all related fields are excluded, that is, [ManyToOneRel, ManyToManyField, ManyToManyRel, FileField, ImageField, TextField].
    """
    return [f for f in model._meta.get_fields() if
            f.editable and type(f) not in [ManyToOneRel, ManyToManyField, ManyToManyRel, FileField, ImageField,
                                           TextField]]


def get_attributes_related(model):
    """
    This method get all attributes ForeignKey's of model for create Inlines.
    """
    return [get_related_name(str(f.related_model)) for f in model._meta.get_fields() if
            f.editable and type(f) == ForeignKey]


def get_attributes_display(model, format_type='({})'):
    """
    This get all attributes of model in format to display: (attr1, attr2, ... ).
    """
    attributes_model = ['"' + str(f.name) + '"' for f in get_attributes_model(model)]
    list_str = ', '.join(map(str, attributes_model))
    format_type = format_type.format(list_str)
    return format_type


def get_list_display_form(model, format_type='({})'):
    """
    This get all attributes of model in format to display to InlineForm : (attr1, attr2, ... ).
    """
    attributes_model = ['"' + str(f.name) + '"' for f in get_attributes_filter_model(model)]
    list_str = ', '.join(map(str, attributes_model))
    format_type = format_type.format(list_str)
    return format_type


def get_attr_filter_display(model, format_type='[{}]'):
    """
    This get all attributes with related fields of model in format to display: [attr1, attr2__name, ... ].
    """
    attributes_model = get_attributes_filtered_with_relationship(model)
    list_str = ', '.join(map(str, attributes_model))
    format_type = format_type.format(list_str)
    return format_type


def get_attributes_filtered_with_relationship(model):
    """
    This method get all attributes of model and include all related fields with  your representation like: [att1, attr2__name,..]
    """
    attributes_model = []
    for f in get_attributes_filter_model(model):
        if type(f) in [FileField, ImageField, TextField]:
            continue
        field = f.__dict__
        if 'related_model' in field:
            related_model = f.related_model.__dict__
            for key in related_model:
                if not key.startswith('_'):
                    if 'field' in related_model[key].__dict__:
                        key_selected = related_model[key].__dict__
                        if type(key_selected['field']) == CharField or type(key_selected['field']) == URLField:
                            attributes_model.append('"' + str(f.name) + '__' + str(key_selected['field'].name) + '"')
                            break
                        else:
                            attributes_model.append('"' + str(f.name) + '__id' + '"')
                            break
        else:
            attributes_model.append('"' + str(f.name) + '"')
    return attributes_model


def get_search_general_attr(model):
    """
    This method create Q filters to add in search general for Filters or ListJsonDataTables.
    """
    attrs = [attr.replace('"', '') for attr in get_attributes_filtered_with_relationship(model)]
    searchs = []
    for attr in attrs:
        searchs.append('Q({}__icontains=search)'.format(attr))
    return '| '.join(map(str, searchs))


def get_attributes_filter_model(model):
    """
    This method get all attrs of model and all related fields are excluded like [ManyToOneRel, ManyToManyField, ManyToManyRel].
    """
    arr = [f for f in model._meta.get_fields() if
           f.editable and type(f) not in [ManyToOneRel, ManyToManyField, ManyToManyRel]]
    return arr


def get_code_upload_file(model):
    """
   This method get attrs like File or Image.
   """
    code = ''
    fields = model._meta.get_fields()
    arr_image = [f for f in fields if f.editable and type(f) == ImageField]
    arr_file = [f for f in fields if f.editable and type(f) == FileField]
    if arr_image:
        for attr_image in arr_image:
            code += '\n#url_' + str(attr_image.name) + ' = upload_image(self.request, "' + str(attr_image.name) + '")\n'
            code += '\n#self.object.'+str(attr_image.name)+' = url_'+str(attr_image.name)
            code += '\n#self.object.save()'
    if arr_file:
        for attr_file in arr_file:
            code += '\n#url_' + str(attr_file.name) + ' = upload_file(self.request, "' + str(attr_file.name) + '")\n'
            code += '\n#self.object.' + str(attr_file.name) + ' = url_' + str(attr_file.name)
            code += '\n#self.object.save()'
    return code


def valid_name_field(item):
    """
    This method get a valid name for an attribute, where '+' (plus) isn't be in.
    """
    return '+' not in str(item.name)


def get_inlines_from_model(model):
    """
    This method get all inlines for a model by related model, that is, field is ManyToOneRel.
    """
    return [get_related_name(str(item.related_model)) for item in
            model._meta.get_fields(include_hidden=True) if
            type(item) == ManyToOneRel and valid_name_field(item)]


def get_list_inlines(model):
    """
    This method make an array of inlines of model.
    """
    list_attributes_rel = get_inlines_from_model(model)
    list_inlines = ['{}Inline'.format(attribute) for attribute in list_attributes_rel]
    return list_inlines


def get_inline_classes(model):
    """
    This method make an array of inlines to insert into View Template.
    """
    list_inlines = get_list_inlines(model)
    list_inlines = ', '.join(map(str, list_inlines))
    list_inlines = '[{}]'.format(list_inlines)
    return list_inlines


def get_related_name(word):
    if 'django.' in word:
        return word[word.index('django.contrib.auth.models.') + len('django.contrib.auth.models.'):word.index("'>")]
    return word[word.index('app.models.') + len('app.models.'):word.index("'>")]


def get_formsets(model):
    inlines = ["{inline}{model}FormSet".format(model=model.__name__, inline=inline) for inline in
               get_inlines_from_model(model)]
    inlines = ', '.join(map(str, inlines))
    inlines = '[{}]'.format(inlines)
    return inlines


def get_formsets_import(model):
    inlines = ["{inline}{model}FormSet".format(model=model.__name__, inline=inline) for inline in
               get_inlines_from_model(model)]
    inlines = ', '.join(map(str, inlines))
    if len(inlines) >= 1:
        return ', {}'.format(inlines)
    else:
        return ''
