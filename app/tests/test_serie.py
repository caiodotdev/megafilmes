from django.test import (
    TestCase,
    Client
)
try:
    from django.core.urlresolvers import reverse_lazy
except ImportError:
    from django.urls import reverse_lazy
from django.contrib.auth import (
    get_user_model,
    models as auth_models
)

from .. import (
    conf,
    models
)


class SeriePermission(TestCase):
    
    @staticmethod
    def perform_create():
        return models.Serie.objects.create(
            name="delete_me"
        )

    def args_for_reverse_lazy(self):
        return {
            "pk": self.object.pk
        }

    def setUp(self):
        self.unauthorized_client = Client()
        self.client = Client()
        self.user = get_user_model().objects.create_user('user', password='password')
        self.client.login(username='user', password='password')
        self.object = self.perform_create()

    def test_unauthenticated_users_cant_create(self):
        response = self.unauthorized_client.get(reverse_lazy(conf.SERIE_CREATE_URL_NAME))
        self.assertNotEqual(response.status_code, 200)

    def test_unauthenticated_users_cant_update(self):
        response = self.unauthorized_client.get(
            reverse_lazy(
                conf.SERIE_UPDATE_URL_NAME,
                kwargs=self.args_for_reverse_lazy()
            )
        )
        self.assertNotEqual(response.status_code, 200)

    def test_unauthenticated_users_cant_delete(self):
        response = self.unauthorized_client.get(
            reverse_lazy(
                conf.SERIE_DELETE_URL_NAME,
                kwargs=self.args_for_reverse_lazy()
            )
        )
        self.assertNotEqual(response.status_code, 200)

    def test_unauthorized_users_cant_create(self):
        response = self.client.get(reverse_lazy(conf.SERIE_CREATE_URL_NAME))
        self.assertNotEqual(response.status_code, 200)

    def test_unauthorized_users_cant_update(self):
        response = self.client.get(
            reverse_lazy(
                conf.SERIE_UPDATE_URL_NAME,
                kwargs=self.args_for_reverse_lazy()
            )
        )
        self.assertNotEqual(response.status_code, 200)

    def test_unauthorized_users_cant_delete(self):
        response = self.client.get(
            reverse_lazy(
                conf.SERIE_DELETE_URL_NAME,
                kwargs=self.args_for_reverse_lazy()
            )
        )
        self.assertNotEqual(response.status_code, 200)

    def test_authorized_users_can_create(self):
        create_permission = auth_models.Permission.objects.get(codename="add_serie")
        self.user.user_permissions.add(create_permission)
        response = self.client.get(reverse_lazy(conf.SERIE_CREATE_URL_NAME))
        self.assertEqual(response.status_code, 200)

    def test_authorized_users_can_update(self):
        change_permission = auth_models.Permission.objects.get(codename="change_serie")
        self.user.user_permissions.add(change_permission)
        response = self.client.get(
            reverse_lazy(
                conf.SERIE_UPDATE_URL_NAME,
                kwargs=self.args_for_reverse_lazy()
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_authorized_users_can_delete(self):
        delete_permission = auth_models.Permission.objects.get(codename="delete_serie")
        self.user.user_permissions.add(delete_permission)
        response = self.client.get(
            reverse_lazy(
                conf.SERIE_DELETE_URL_NAME,
                kwargs=self.args_for_reverse_lazy()
            )
        )
        self.assertEqual(response.status_code, 200)
