from django.test import TestCase

from django.contrib.auth.models import User


class OwnerPortalView(TestCase):

    def test_login_uses_login_template(self):
        response = self.client.get('/login/')
        self.assertTemplateUsed(response, 'rvi/login.html')

    def test_nonowner_cannot_login(self):
        nonowner = User.objects.create_user(username='dthiriez',
                                            password='rvi')
        response = self.client.post(
            '/login/', 
            data={'username': 'dthiriez', 'password': 'rvi'}
        )
        
        self.assertContains(response, "You must be a vehicle owner to log in")

    def test_admin_cannot_log_in(self):
        admin = User.objects.create_user(username='admin',
                                            password='rvi')
        response = self.client.post(
            '/login/', 
            data={'username': 'admin', 'password': 'rvi'}
        )
        
        self.assertContains(response, "You must be a vehicle owner to log in")

    def test_nonuser_cannot_log_in(self):
        response = self.client.post(
            '/login/', 
            data={'username': 'noaccount', 'password': 'rvi'}
        )
        
        self.assertContains(response, "Your username and/or password were incorrect")

    def test_inactive_cannot_log_in(self):
        inactive = User.objects.create_user(username='dthiriez',
                                            password='rvi'
        )
        inactive.is_active = False
        inactive.save()

        response = self.client.post(
            '/login/', 
            data={'username': 'dthiriez', 'password': 'rvi'}
        )
        
        self.assertContains(response, "Your account is not active, please contact the site admin.")

