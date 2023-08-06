import os
import subprocess
import time
import unittest

import requests


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
    CWD = os.path.dirname(__file__)
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
            cwd=cls.CWD,
            stdout=subprocess.PIPE,
        )

        is_success = False
        for _ in range(10):
            try:
                requests.get(cls.BASE_URL)
                is_success = True
                break
            except Exception:
                time.sleep(1)

        if not is_success:
            raise Exception("Could not start Functions Framework process")

    @classmethod
    def tearDownClass(cls):
        if cls.process:
            cls.process.kill()
            cls.process.wait()
            cls.process = None
