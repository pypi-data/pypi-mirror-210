import os
import subprocess
import time
import unittest


class TestEndpointAPIIntegration(unittest.TestCase):
    """
    A test case class for integration testing the endpoint API. Start the functions framework as background process and kill it after the tests are done.

    Attributes:
        FILE (str): The filename of the events file, change it to your filename.
        BASE_URL (str): The base URL for the API endpoint.
        process (subprocess.Popen or None): The subprocess for the Functions Framework process.

    Methods:
        setUpClass(cls): Set up the test class by starting the Functions Framework process.
        tearDownClass(cls): Tear down the test class by killing the Functions Framework process.
    """

    FILE = 'events.py'
    BASE_URL = 'http://localhost:{}'.format(os.getenv('PORT', 8005))
    process = None

    @classmethod
    def setUpClass(cls):
        cls.port = os.getenv('PORT', 8005)
        cls.process = subprocess.Popen(
            [
                'functions-framework',
                '--target', 'main',
                '--source', cls.FILE,
                '--port', str(cls.port)
            ],
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
        )

        start_time = time.time()
        max_wait_time = 10
        while time.time() - start_time < max_wait_time:
            if cls.process.poll() is not None:
                # Process has started
                break
            time.sleep(1)
        else:
            print("Functions Framework process failed to start within the given time.")
            cls.process.terminate()
            return

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.kill()
            cls.process.wait()
            cls.process = None
