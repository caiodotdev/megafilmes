from django import forms
from django.forms import ModelForm, inlineformset_factory
from app.utils import generate_bootstrap_widgets_for_all_fields

from . import (
    models
)

class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # field.widget.attrs['class'] = 'form-control'
            if field_name == 'phone' or field_name == 'telefone':
                field.widget.attrs['class'] = 'form-control telefone phone'
            if field_name == 'cep' or field_name == 'postalcode':
                field.widget.attrs['class'] = 'form-control cep'


class MovieForm(BaseForm, ModelForm):
    class Meta:
        model = models.Movie
        fields = ("id", "title", "year", "rating", "image", "url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Movie)

    def __init__(self, *args, **kwargs):
        super(MovieForm, self).__init__(*args, **kwargs)


class MovieFormToInline(BaseForm, ModelForm):
    class Meta:
        model = models.Movie
        fields = ("id", "title", "year", "rating", "image", "url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Movie)

    def __init__(self, *args, **kwargs):
        super(MovieFormToInline, self).__init__(*args, **kwargs)



class SerieForm(BaseForm, ModelForm):
    class Meta:
        model = models.Serie
        fields = ("id", "title", "year", "rating", "image", "url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Serie)

    def __init__(self, *args, **kwargs):
        super(SerieForm, self).__init__(*args, **kwargs)


class SerieFormToInline(BaseForm, ModelForm):
    class Meta:
        model = models.Serie
        fields = ("id", "title", "year", "rating", "image", "url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Serie)

    def __init__(self, *args, **kwargs):
        super(SerieFormToInline, self).__init__(*args, **kwargs)



class ChannelForm(BaseForm, ModelForm):
    class Meta:
        model = models.Channel
        fields = ("id", "title", "image", "url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Channel)

    def __init__(self, *args, **kwargs):
        super(ChannelForm, self).__init__(*args, **kwargs)


class ChannelFormToInline(BaseForm, ModelForm):
    class Meta:
        model = models.Channel
        fields = ("id", "title", "image", "url")
        widgets = generate_bootstrap_widgets_for_all_fields(models.Channel)

    def __init__(self, *args, **kwargs):
        super(ChannelFormToInline, self).__init__(*args, **kwargs)

