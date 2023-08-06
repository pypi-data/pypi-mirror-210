from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

class MoonMethods:
    """Common-use methods when locating and interacting with web elements
    """
    
    # Default time to wait for elements to become visible.
    # Can be changed in a Moonrise Test Suite by setting Moonrise.default_timeout = (new timeout)
    default_timeout = 60

    def get_web_element(self, locator, timeout=None, get_multiples = False):
        """Locate a web element or elements via a given ``locator``.
           Throws a TimeoutException if the element(s) cannot be found within ``timeout`` or default_timeout

           Can perform a search in 3 main ways:
           - XPATH default: using the prefix '//' will automatically use XPATH to perform the search
           - CSS default: simply inputting an element locator will try to locate the element via CSS selector
           - By methods: specifying the lookup type will use the desired lookup method if it is available. Available methods include:
             - name:some_name
             - id:some_id
             - link:link_text
             - partial link text:partial_link_text
             - class:class_of_element
             - tag:element_tag
             - css:css_selector

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
           - ``get_multiples``: If get_web_element should return a list of elements that match the given locator. False by default.
        """

        # Timeout for element to be found may come from the timeout given to this method or the default_timeout.
        if timeout:
            time_to_wait = timeout
        else:
            time_to_wait = self.default_timeout

        location_methods = {
            "name": By.NAME,
            "id": By.ID,
            "link": By.LINK_TEXT,
            "xpath": By.XPATH,
            "partial link text": By.PARTIAL_LINK_TEXT,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "css": By.CSS_SELECTOR,
        }

        multi_element_return = {
            False: EC.visibility_of_element_located,
            True: EC.visibility_of_all_elements_located
        }

        wait = WebDriverWait(self.moon_driver, time_to_wait)

        try:
            if type(locator) is WebElement:
                return locator
            if locator.startswith("/"):
                return wait.until(multi_element_return.get(get_multiples)((By.XPATH, locator)))
            elif locator.split(":")[0] in location_methods:
                return wait.until(multi_element_return.get(get_multiples)((location_methods[locator.split(":")[0]], locator.split(":")[1])))
            else:
                return wait.until(multi_element_return.get(get_multiples)((By.CSS_SELECTOR, locator)))
        except TimeoutException:
            raise TimeoutException(f"Could not find '{locator}' after {time_to_wait} seconds.")

    def click_element(self, locator, timeout=None):
        """Click the element identified by ``locator``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        self.get_web_element(locator=locator, timeout=timeout).click()


    def input_text(self, locator, text, timeout=None):
        """Types the given ``text`` into the text field identified by ``locator``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        self.get_web_element(locator=locator, timeout=timeout).send_keys(text)

    def get_web_elements(self, locator, timeout=None):
        """Returns a list of WebElement objects matching the ``locator``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        return self.get_web_element(locator=locator, timeout=timeout, get_multiples=True)

    def select_from_list_by_value(self, locator, value, timeout=None):
        """Select option from selection list ``locator`` by ``value``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``value``: The value to select from the list.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        Select(self.get_web_element(locator=locator, timeout=timeout)).select_by_value(value)
        
    def select_from_list_by_label(self, locator, label, timeout=None):
        """Select option from selection list ``locator`` by ``label``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``label``: The label to select from the list.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        Select(self.get_web_element(locator=locator, timeout=timeout)).select_by_visible_text(label)

    def select_from_list_by_index(self, locator, index, timeout=None):
        """Select option from selection list ``locator`` by ``index``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``index``: The index to select from the list.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        Select(self.get_web_element(locator=locator, timeout=timeout)).select_by_index(index) 

    def get_text(self, locator, timeout=None):
        """Returns the text value of the element identified by ``locator``.

           Arguments:
           - ``locator``: The method by which to locate a web element.
           - ``timeout``: How long to search for the element before throwing a TimeoutException.
        """
        return self.get_web_element(locator=locator, timeout=timeout).text