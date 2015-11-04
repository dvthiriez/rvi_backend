from unittest import skip
from .base import FunctionalTest
from common.util.rvi_setup import RVIModelSetup
from common.util.rvi_invoke import RVICalls
from server.rviserver import RVIServer


## TODO complete test on desktop environment for web browser support
@skip
class WebPortalTest(FunctionalTest):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

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

        # David returns to the web site to check the owner portal
        self.fail('Finish the test!')


class RviTest(FunctionalTest):
    
    def test_data_setup(self):
        # TODO test is currently failing, RVIServer instance is not launching
        # Need to figure out how to instantiate RVIServer s.t. test database is used
        # pid_file= '/var/run/rviserver.pid'
        # rvi_server = RVIServer(pid_file)
        # rvi_server.start()

        rvi_model = RVIModelSetup()
        owner = rvi_model.setup_user(username='dthiriez')
        owner_key = rvi_model.setup_key(owner)
        vehicle = rvi_model.setup_vehicle(owner, owner_key)

        guest = rvi_model.setup_user(username='guest')
        guest_key = rvi_model.setup_key(guest)
        guest_device = rvi_model.setup_device(guest, guest_key)
        guest_remote = rvi_model.setup_remote(guest, guest_device, vehicle)

        rvi_call = RVICalls()
        rvi_call.cert_create(guest, vehicle)
        # rvi_server.stop()

    def test_can_send_remote(self):
        # David proceeds to set up an account, security key, device, and 
        # vehicle in order to be able to send a remote
        
        # Simulating the smart phone app, David triggers a 'cert_create' to
        # RVI Service hosted by the backend.

        # He checks the backend data to confirm the 'cert_create' call
        # registered and updated the database with the new Remote

        # Next he confirm that the rvi server logs show the new Remote
        # was passed on to rvi_core.

        # The Remote should now be queued up by rvi_core and ready to be
        # sent as soon as the device comes online

        # David then simulates the device coming online by hosting its
        # 'cert_provision' service available on the rvi network

        # To confirm the data was received, he check that the Remote he
        # sent was received by the 'cert_provision' service
        self.fail('Finish the test!')

    def test_can_receive_service_history_record(self):
        self.fail('Finish the test')
    
