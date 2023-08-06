import os
import traceback
from colorama import Fore, Style, init
import datetime
import shutil
init(convert=True)

class BaseTest:
    """Creates the structure for test suites written using the Moonrise framework
    """

    # The dictionary to be referenced when evaluating what tests to run
    tests = {}


    def __init__(self, test_cases=()):
        """Evaluates whether to run tests within the current test suite based on user input and creates report folder and file structures.

           Arguments:
           - `test_cases`: Test Case names to be executed. If none specified, will execute all test cases under the current test suite.
        """

        self.suite_tests = self.tests.get(f"{self.__module__}.{self.__class__.__name__}")
        self.video_folder = None

        # If the condition is present where there are no tests in a suite or the user-requested tests cases do not match the current suite,
        # do not proceed.
        if self.suite_tests is None or (test_cases != () and len(set(test_cases).intersection(self.suite_tests)) == 0):
            # Add an extra note if test cases were specified but do not exist in the current suite.
            if test_cases and self.suite_tests:
                print(f'Skipping test suite "{self.__class__.__name__}" in module "{self.__module__}" because no tests matching {test_cases} were found.')
            return
        
        if test_cases:
            test_cases = set(test_cases).intersection(self.suite_tests)
        else:
            test_cases = self.suite_tests

        self.passes = 0
        self.failures = 0
        self.totals = 0

        self.colors = {
        "pass": Fore.LIGHTGREEN_EX,
        "fail": Fore.LIGHTRED_EX,
        "header": Fore.LIGHTCYAN_EX,
        "info": ""
        }

        if not os.path.exists(str(f"{os.getcwd()}/reports/{self.__module__}/{self.__class__.__name__}")):
            os.makedirs(str(f"{os.getcwd()}/reports/{self.__module__}/{self.__class__.__name__}"))
        self.reports_folder = str(f"{os.getcwd()}/reports/{self.__module__}/{self.__class__.__name__}")

        if not os.path.exists(str(f"{self.reports_folder}/video")):
            os.makedirs(str(f"{self.reports_folder}/video"))
        self.video_folder = self.reports_folder + "/video"

        self.report_file = open(f"{self.reports_folder}/{self.__class__.__name__}.log", "w")

        self.run_tests(test_cases)

        shutil.rmtree(self.video_folder)

    def run_tests(self, test_cases):
        """Method to call the requested tests.

           Arguments:
           - `test_cases`: Test Case names to be executed.
        """
        if self.video_thread:
            self.video_thread.video_folder = self.video_folder
        
        self.log_to_report(f"----------------- Beginning Suite: {self.__class__.__name__} -----------------", log_type="header")
        # Perform suite setup actions before any tests are executed.
        self.suite_setup()
        
        self.totals += len(test_cases)
        
        for tc in test_cases:
            self.log_to_report(f"--- Starting test: {tc} ---", log_type="header")
            self.suite_tests.get(tc)(self)

        self.log_to_report(f"----------------- Ending Suite: {self.__class__.__name__} -----------------", log_type="header")
        # Perform suite teardown actions after all tests are executed.
        self.suite_teardown()

        if self.failures > 0:
            end_string = f"{self.colors.get('pass')}{self.passes} tests passing, {self.colors.get('fail')}{self.failures} tests failing, {self.colors.get('header')}{self.totals} tests total"
        else:
            end_string = f"{self.colors.get('pass')}{self.passes} tests passing, {self.colors.get('header')}{self.totals} tests total"

        self.log_to_report(end_string, log_type="header")

        # Create video from screenshots if video_thread was created.
        if self.video_thread:
            self.video_thread.create_video_from_pngs(f"{self.reports_folder}/{self.__class__.__name__}.mp4")
            self.video_thread.stop()

    def log_to_report(cls, message, log_type = "info"):
        """Log information with a timestamp to the console and to the report file.

           Arguments:
           - message: The text to log.
           - log_type: The color of the text as it will appear in the console. Consult the colors variable in this class for specifics.
        """
        timestamp = datetime.datetime.now()
        print(f"\n{cls.colors.get(log_type)}{timestamp} | {message}{Style.RESET_ALL}")
        for color in cls.colors.values():
            message = message.replace(color, "")
        cls.report_file.write(f"\n\n{timestamp} | {message}")

    def suite_setup(self):
        """Default suite setup method to be called before any tests are executed.
        """
        pass

    def suite_teardown(self):
        """Default suite teardown method to be called after all tests are executed.
        """
        pass

    def test_teardown(self):
        """Default test teardown method to be called after every test is executed.
        """
        pass

    def test_setup(self):
        """Default test setup method to be called before every tests is executed.
        """
        pass

    @classmethod
    def test(cls, test_case):
        """Decorator method to hang on every method that is to be classified as a test case.
           Adds test case methods to the tests variable in this class. 
           These tests will be referenced upon attempting to run their test suites.

           Arguments:
           - test_case: The name of the method to add as a test case.
        """

        def test_executor(self):
            """Executes the current test case, performing test setup actions, handling failures, and finally calling test teardown actions.
            """
            try:
                self.test_setup()
                test_case(self)
                self.log_to_report(f"{test_case.__name__} PASS", log_type = "pass")
                self.passes += 1
            except Exception:
                self.log_to_report(f"{traceback.format_exc()}")
                if self.moon_driver:
                    self.moon_driver.save_screenshot(f"{self.reports_folder}/{test_case.__name__}.png")
                self.log_to_report(f"{test_case.__name__} FAIL", log_type = "fail")
                self.failures += 1
            finally:
                self.test_teardown()

        mod_and_suite = f"{test_case.__module__}.{test_case.__qualname__.split('.')[0]}"
        cls.tests.setdefault(mod_and_suite, {})
        cls.tests[mod_and_suite][test_case.__name__] = test_executor
        return test_executor