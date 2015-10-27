# WARNING: Code sourced from python3 implementation

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from django.contrib.auth.models import User
from security.models import JSONWebKey
from vehicles.models import Vehicle


class FunctionalTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
            super().setUpClass()
            cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def setup_mock_key(self, username):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        valid_from = datetime.now()
        valid_to = valid_from.replace(valid_from.year + 1)
        
        key = JSONWebKey.objects.create(
            key_name='key_' + username,
            key_valid_from=valid_from,
            key_valid_to=valid_to,
            key_pem=pem
        )
        key.save()
        return key    
    
    def setup_mock_data(self):
        owner = User.objects.create_user(username='dthiriez',
                                            password='rvi')
        owner_key = setup_mock_key(owner.username)

        vehicle = Vehicle.objects.create(
            veh_name='vehicle_test',
            veh_key=owner_key,
            account=owner
        )
        vehicle.save()

        guest = User.objects.create_user(
            username='arodriguez',
            password='rvi'
        )
        
        guest_key = setup_mock_key(guest.username)

        guest_device = Device.objects.create(
            dev_name='device_arodriguez',
            dev_owner='arodriguez',
            dev_uuid='1234',
            dev_key=guest_key,
            dev_rvibasename='jlr.com'
        )

        valid_from = datetime.now()
        valid_to = valid_from.replace(valid_from.year + 1)
        guest_remote = Remote(
            rem_name='remote_arodriguez',
            rem_vehicle=vehicle,
            rem_device=guest_device,
            rem_validfrom=valid_from,
            rem_validto=valid_to
        )


    def test_can_access_and_setup_rvi_services(self):
        # David has has heard about a cool new open source telematics project.
        # Intruigued, he goes to download the applicable repositories to set up
        # his own instance of rvi_backend.

        # Once the server is installed and running, he checks that the website
        # is up
        self.browser.get(self.server_url)

        # Satisfied that the web site is up, he proceeds to check if the rvi  
        # services are also up and running

        # RVI services appear to up and functional

        # To start using rvi, David proceed to set up accounts, security keys, 
        # devices, remotes, and a vehicle for an owner and guest user
        self.setup_mock_data()

        # David returns to the web site to check the owner portal
        self.fail('Finish the test!')

        
