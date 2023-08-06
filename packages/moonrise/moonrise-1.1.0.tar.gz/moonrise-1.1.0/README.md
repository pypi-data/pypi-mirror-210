# Moonrise

- [Moonrise](#moonrise)
  - [Introduction](#introduction)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Example Test Suites](#example-test-suites)
    - [CLI Commands](#cli-commands)
  - [Why the Name "Moonrise"?](#why-the-name-moonrise)

## Introduction
Moonrise is a test suite creation toolset with additional quality of life upgrades for using the [selenium](https://www.selenium.dev/) test framework.

Notable features:
- Test Suite and Test Case organization
- Browser session generation with selenium
- Web element lookup methods with built-in dynamic waits for elements to become available
- Test report generation

## Dependencies
Moonrise only has two dependencies: [selenium](https://pypi.org/project/selenium/) and [colorama](https://pypi.org/project/colorama/). Both of these dependencies are automatically installed with moonrise.

## Installation
Recommend using pypi to install moonrise, `pip install moonrise`. You may also retrieve the latest version from [github](https://github.com/Worakow1138/Moonrise).

## Usage
Moonrise is designed for ultimate ease of use while still giving access to the power of the selenium framework. By simply extending the Moonrise class, any Python class becomes a test suite, capable of executing automated test cases and generating test reports.

    from moonrise import Moonrise

    class ExampleSuite(Moonrise):
        
        @Moonrise.test
        def example_test(self):
            self.log_to_report("this is a test")

### Example Test Suites
Below are two example test suites created to be used with Moonrise. Copy this example code into a python module and then consult the [CLI Commands](#cli-commands).

    from moonrise import Moonrise

    ### Classes represent test suites ###
    class ExampleSuite(Moonrise):

        ### Default methods for test and suite setup and teardown are provided ###
        def suite_setup(self):
            self.log_to_report("this is the beginning of the test suite.")
        
        def suite_teardown(self):
            self.log_to_report("this is the end of the test suite.")
        
        def test_setup(self):
            self.log_to_report("this is the beginning of the test case.")
        
        def test_teardown(self):
            self.log_to_report("this is the end of the test case.")
        
        ### Tag test cases with @Moonrise.test decorator ###
        @Moonrise.test
        def example_test(self):
            ### Use log_to_report() for detailed reporting ###
            self.log_to_report("this is a test")
        
        @Moonrise.test
        def test_failure(self):
            self.log_to_report("this test should fail")
            assert 1 == 2, "this failure is intentional"

        @Moonrise.test
        def test_success(self):
            self.log_to_report("this test should pass")
            assert 1 == 1

    class SeleniumExamples(Moonrise):
        
        ### Set the default time to search for web elements ###
        Moonrise.default_timeout = 10
        
        def test_setup(self):
            ### Settings the persist argument to True allows for persistent browser sessions that will remain open and available for reuse with the self.use_current_browser() method ###
            self.open_browser("chrome", persist=True)
            ### moon_driver is the webdriver created with open_browser and can be directly controlled from the test case.
            self.moon_driver.maximize_window()
        
        def test_teardown(self):
            self.cleanup_browser()

        @Moonrise.test
        def retrieve_hello_world(self):
            self.navigate_to_page("the-internet.herokuapp.com/dynamic_loading/2")
            self.click_element("#start button")
            self.log_to_report(self.get_text("#finish"))

        @Moonrise.test
        def fail_to_retrieve_hello_world_in_time(self):
            self.navigate_to_page("the-internet.herokuapp.com/dynamic_loading/2")
            self.click_element("#start button")
            ### Waiting for elements to be present can be set on individual keywords ###
            self.log_to_report(self.get_text("#finish", timeout=2))

### CLI Commands
The easiest way to use Moonrise is through the command line. The CLI offers a broad range of filtering options:

- Use `moonrise (a folder containing python modules)` to execute all Moonrise tests and suites within that folder.
- Use `moonrise (a python file)` to target a specific file that may contain Moonrise tests and suites.
- Use `test:(test name)` to target specific tests. This keyword may be used more than once in a command and can apply to similarly named tests across multiple suites and python files.
- Use `suite:(suite name)` to target specific test suites. This keyword may be used more than once in a command and can apply to similarly named suites across mulitple python files.

With the [above example](#example-test-suites), run only the `ExampleSuite` by typing `moonrise (path to file or containing folder) suite:ExampleSuite`.

Next, target the failing test by adding `test:test_failure` to the command.

To include the `SeleniumExamples` test suite in the run, remove the filters entirely and execute `moonrise (path to file or containing folder)`.

After each test run, reports and screenshots (upon test failure) are generated at the location from where the tests are run.

## Why the Name "Moonrise"?
Since [selenium](https://www.selenium.dev/) is named after the element [Selenium](https://en.wikipedia.org/wiki/Selenium), which is named after [Selene](https://en.wikipedia.org/wiki/Selene), the ancient Greek goddess of the Moon, it only seemed fitting to have a name that incorporated a lunar theme!