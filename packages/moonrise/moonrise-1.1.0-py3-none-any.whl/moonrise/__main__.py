import os
import sys
from moonrise.Base_Test import BaseTest
from moonrise import Moonrise
from colorama import Fore, Style

def run_cli(args=None):
    """Method for running command line interface

       Arguments:
       - args: arguments from the command line specifying the python module or folder, the tests to run, and/or the suites to run.
    """
    if args is None:
        args = sys.argv[1:]
    
    def import_modules(filepath):
        """Add relevant modules to path and to modules to examine for Moonrise tests and suites.
        """

        if ":" in filepath:
            dir_name = filepath
        else:
            dir_name = os.getcwd() + "/" + filepath

        if os.path.isfile(dir_name):
            sys.path.append(os.path.abspath(os.path.join(dir_name, os.pardir)))
            module = os.path.basename(dir_name[:-3])
            modules.append(__import__(module))
        elif os.path.isdir(dir_name):
            sys.path.append(dir_name)
            for name in os.listdir(dir_name):
                if name.endswith(".py"):
                    module = name[:-3]    
                    modules.append(__import__(module))

    modules = []
    suites = []
    tests = []

    for arg in args:
        if arg.startswith("suite"):
            suites.append(arg.split(":")[1])
        elif arg.startswith("test"):
            tests.append(arg.split(":")[1])
        else:
            import_modules(arg)

    tests = tuple(tests)

    if not modules:
        print(f"{Fore.LIGHTRED_EX}moonrise Error: No valid file or directory given{Style.RESET_ALL}")
        return
    
    tests_were_run = False

    for module in modules:
        for clazz in module.__dict__.values():
            if BaseTest.__name__ in str(clazz.__init__) and clazz.__name__ != Moonrise.__name__:
                if suites:
                    if clazz.__name__ in suites:
                        tests_were_run = True
                        clazz(tests)
                else:
                    tests_were_run = True
                    clazz(tests)

    if not tests_were_run:
        print(f"{Fore.LIGHTRED_EX}moonrise Error: No tests were run. Were the tests or suites labeled correctly?{Style.RESET_ALL}")
        return


if __name__ == "__main__":
    run_cli(sys.argv[1:])