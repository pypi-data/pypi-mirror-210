from moonrise.Moon_Browser import MoonBrowser
from moonrise.Moon_Methods import MoonMethods
from moonrise.Base_Test import BaseTest

class Moonrise(MoonBrowser, MoonMethods, BaseTest):
    """Moonrise is a test suite creation toolset with additional quality of life upgrades for using the [selenium](https://www.selenium.dev/) test framework.

       Notable features:
       - Test Suite and Test Case organization
       - Browser session generation with selenium
       - Web element lookup methods with built-in dynamic waits for elements to become available
       - Test report generation

       Moonrise is designed for ultimate ease of use while still giving access to the power of the selenium framework. 
       By simply extending the Moonrise class, any Python class becomes a test suite, capable of executing automated test cases and generating test reports.

       ### Example ###
        from moonrise import Moonrise

        class ExampleSuite(Moonrise):

            @Moonrise.test
            def example_test(self):
                self.log_to_report("this is a test")

            
       The easiest way to use Moonrise is through the command line. The CLI offers a broad range of filtering options:

       - Use `moonrise (a folder containing python modules)` to execute all Moonrise tests and suites within that folder.
       - Use `moonrise (a python file)` to target a specific file that may contain Moonrise tests and suites.
       - Use `test:(test name)` to target specific tests. This keyword may be used more than once in a command and can apply to similarly named tests across multiple suites and python files.
       - Use `suite:(suite name)` to target specific test suites. This keyword may be used more than once in a command and can apply to similarly named suites across multiple python files.
    """