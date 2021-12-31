from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django_crud_generator.django_crud_generator import generate_for_model, generate_default_templates, \
    generate_all_models
import os


class Command(BaseCommand):
    help = 'Generate files by models'

    def add_arguments(self, parser):
        parser.add_argument('--app', action='store', type=str)
        parser.add_argument('--model', action='append', type=str)
        parser.add_argument('--default', action='store_true')
        parser.add_argument('--type', action='store', type=str)
        parser.add_argument('--all', action='store_true')

    def handle(self, *args, **kwargs):
        name_app = 'app'
        typer = 'default'
        project_name = os.path.basename(os.getcwd())
        if 'app' in kwargs:
            if kwargs['app'] is not None:
                name_app = kwargs['app']
        if 'type' in kwargs:
            if kwargs['type'] is not None:
                typer = kwargs['type']
        if kwargs['model']:
            for model in kwargs['model']:
                model_name = model
                print('-- Generating model: ', model_name)
                generate_for_model(name_app, model_name, project_name, typer)
        else:
            print('-- Generating all templates, files and models')
            generate_all_models(name_app, project_name, typer)
