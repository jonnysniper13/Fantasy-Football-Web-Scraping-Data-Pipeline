"""
This module scrapes data from a specified website.

The module contains one class in which all methods are contained and operated
out of. The class is also initiated when called in the main block. Common scraper
methods are containing within this class to be call from other scripts.

The only usage of this module is to initiate an instance of the Class:
scraped_data = WebScraper()
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
import time
import os
from typing import Optional, Union, List


if __name__ == "__main__":
    pass
else:
    class WebScraper:
        """This Class scrapes data from a specified website.

        See Module description and __init__ method for description of this
        Class.

        """

        def __init__(self) -> None:
            """Constructor method for the Class.

            This method creates all class variables.

            Attributes:
                driver: Initiates the Chromedriver element.

            Returns:
                None

            """
            os.system("windscribe connect")
            self.driver: WebElement = webdriver.Chrome(options=self.setup_options())

        @staticmethod
        def setup_options():
            """Helper function to setup Chromedriver parameters.

            This function defines parameters for running the Chromedriver,
            including running in headless mode, defining the window size
            (to support running in headless mode), disabling sandbox, and
            disabling the driver from using memory.

            Attributes:
                options (ChromeOptions): Sets parameters for Chromedriver.

            Returns:
                options

            """
            options = Options()
            options.add_argument('window-size=1920x1080')
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-dev-shm-usage')
            return options

        def gdpr_consent(self, xpath: str) -> None:
            """Method that handles the gdpr consent popup.

            This method will find the accept cookies button on the gdpr popup
            and will close the popup, and switch back to the main content.

            Args:
                xpath: XPATH element identifier to be located.

            Attributes:
                accept_cookies_button: Chromedriver WebElement for
                    the accept cookies button.

            Returns:
                None

            """
            accept_cookies_button: WebElement = self.find_xpaths(xpath, multi=False, pause=True)
            self.close_popup(accept_cookies_button)
            self.driver.switch_to.default_content()

        def find_xpaths(self, xpath: str, multi: Optional[bool] = False, pause: Optional[bool] = False) -> Union[WebElement, list[WebElement]]:
            """Helper function to shorten syntax for finding data types.

            This function searches the current webpage for elements located by
            XPATH identifiers. It has optional arguments for searching for
            multiple occurences and for enforcing for dynamic time delays
            (up to 30 sec) based on screen loading time.

            Args:
                xpath: XPATH element identifier to be located.
                multi (optional): Determines if multiple elements are to be
                    found. Defaults to False.
                pause (optional): Determines if a delay is to be instructed.
                    Defaults to False.

            Attributes:
                obj: Chromedriver webelement of specified XPATH.

            Raises:
                TimeoutException: Prints an error message if page loading
                exceeds default limits.

            Returns:
                obj

            """
            try:
                if pause:
                    time.sleep(1)
                    WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//*[@{xpath}]')))
                if multi:
                    obj: list[WebElement] = self.driver.find_elements(By.XPATH, f"//*[@{xpath}]")
                else:
                    obj: WebElement = self.driver.find_element(By.XPATH, f"//*[@{xpath}]")
                time.sleep(1)
                return obj
            except TimeoutException:
                print("Loading took too much time!")
                return None

        def close_popup(self, popup_name: WebElement) -> None:
            """Helper function to close popups.

            This function closes the popup and then asserts when it has
            disappeared by enforcing a dynamic time delay (up to 30 sec).

            Args:
                popup_name: Chromedriver webelement of specified
                    XPATH.

            Raises:
                TimeoutException: Prints an error message if page loading
                exceeds default limits.

            Returns:
                None

            """
            try:
                popup_name.click()
                WebDriverWait(self.driver, 60).until(EC.invisibility_of_element_located((popup_name)))
                time.sleep(1)
            except TimeoutException:
                print("Loading took too much time!")

        def login(self, cred_xpaths: dict, cred: list) -> None:
            """Method to handle login page.

            This method handles the login page by locating the appropiate
            fields and sending the appropiate keys to the page, before
            clicking the login button and ensuring the popup closes.

            Args:
                cred: Dictionary of credentials

            Attributes:
                usr_name_field: Chromedriver webelement of
                    specified XPATH.
                pword_name_field: Chromedriver webelement of
                    specified XPATH.
                login_button: Chromedriver webelement of
                    specified XPATH.

            Returns:
                None

            """
            usr_name_field: WebElement = self.find_xpaths(cred_xpaths['Username xpath'])
            usr_name_field.send_keys(cred[0])
            pword_name_field: WebElement = self.find_xpaths(cred_xpaths['Password xpath'])
            pword_name_field.send_keys(cred[1])
            login_button: WebElement = self.find_xpaths(cred_xpaths['Login xpath'])
            self.close_popup(login_button)

        def navigate(self, xpath: str) -> None:
            """Method to navigate to a specified page.

            This method takes in a required XPATH element, locates it,
            and then clicks it.

            Args:
                xpath: XPATH element to be found.

            Returns:
                None

            """
            nav_to = self.find_xpaths(xpath, multi=False, pause=True)
            nav_to.click()

        def retrieve_attr(self, xpath_parent: str, xpath_child: Optional[str] = '', attr: Optional[str] = '') -> str:
            """Method to return a specified attribute from the webpage.

            This method finds the header for the text containing the required
            attribute, and then locates the child element (if applicable) of which
            the text attribute can be retrieved.

            Args:
                xpath_parent: Parent XPATH element to be found.
                xpath_child: Child XPATH element to be found.

            Attributes:
                output: Text string to be outputted.

            Returns:
                output

            """
            try:
                output: WebElement = self.find_xpaths(xpath_parent)
                if xpath_child != '':
                    output: WebElement = output.find_element(By.XPATH, xpath_child)
                if attr == '':
                    return output.text
                return output.get_attribute(attr)
            except NoSuchElementException:
                return None

        def goto_page(self, next_page_xpath: str, desired_page: int) -> None:
            """Method that moves list to required page.

            This method handles the method for clicking the 'Next Page'
            button to ensure it is called the required number of times (i.e.
            up to the page counter). Each time a new page is loaded, the
            button element is re-located and the boolean next page checker is
            reset.

            Args:
                next_page_xpath: XPATH for the next page button.
                desired_page: Target page number.

            Attributes:
                page_buttons: Chromedriver WebElement for the
                    'Next Page' button on the list.

            Returns:
                None

            """
            for _ in range(1, desired_page):
                page_buttons: list[WebElement] = self.find_xpaths(next_page_xpath, multi=True)
                self.click_next(page_buttons)

        @staticmethod
        def click_next(page_buttons: list[WebElement]) -> None:
            """Method that clicks the next page button.

            This method will click the 'Next Page' button, located within
            a WebElement list. A time delay is enforced after a new page is clicked.

            Args:
                page_buttons: List of WebElements for page navigator buttons.

            Returns:
                None

            """
            for button in page_buttons:
                if button.text == 'Next':
                    button.click()
                    break
            time.sleep(1)

        def find_list(self, xpath: str) -> list[WebElement]:
            """Finds a list from an xpath.

            This method finds a container list based on a given xpath element.

            Args:
                xpath: XPATH element to be found.

            Attributes:
                data_list: List of WebElements.

            Returns:
                data_list
            """
            data_list: list[WebElement] = self.find_xpaths(xpath, multi=True, pause=True)
            return data_list

        def open_popup(self, target: WebElement, xpath: str) -> None:
            """Cycles through page and calls scraping method and output.

            This method will open a popup for a given target and then return the
            WebElement for the button to close the popup.

            Args:
                target: Target popup to be opened.
                xpath: XPATH element to be found.

            Attributes:
                popup: Popup element.

            Returns:
                None

            """
            self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(target)))
            popup: WebElement = self.find_xpaths(xpath)
            return popup

        def get_from_popup_header(self, xpath_parent: str, xpath_child: str, tag_list: list) -> List[str]:
            """Gets details from the header of a popup.

            This method gets main details contained within the header of a popup.

            Args:
                xpath_parent: Parent XPATH element to be found.
                xpath_child: Child XPATH element to be found.
                tag_list: Tags to be searched for.

            Attributes:
                parent: Parent web element.
                children: Child web element.
                output_list: List of strings to be returned.

            Returns:
                output_list

            """
            parent: WebElement = self.find_xpaths(xpath_parent)
            children: list[WebElement] = parent.find_elements(By.XPATH, xpath_child)
            output_list: list = [None] * len(tag_list)
            for index, element in enumerate(tag_list):
                for c in children:
                    if c.tag_name == element:
                        output_list[index] = c.text
            return output_list

        def get_from_fields(self, key_list: dict) -> dict:
            """Gets data from various fields.

            This method collects data from numerous specified fields.

            Args:
                key_list: Dictionary of keys to cycle through.

            Attributes:
                parent: Parent web element.
                children: Child web element.
                name: Name of attribute to be scraped.
                data_dict: Dictionary of data to be returned.

            Returns:
                data_dict

            """
            data_dict: dict = {}
            name: str = ''
            parent: WebElement = self.find_xpaths(key_list['xpath'])
            children: list[WebElement] = parent.find_elements(By.XPATH, './/*')
            for c in children:
                if c.tag_name == key_list['heading']:
                    name: str = c.text
                elif c.tag_name == key_list['heading_value']:
                    data_dict[name] = c.text
                    name = ''
            return data_dict

        def get_from_table(self, parent: WebElement) -> list:
            """Scrapes tabular data.

            This method scrapes data from tables located via an xpath.

            Args:
                parent: WebElement containing the tables that are to be scraped.
                table_name: Name of table to be scraped.

            Attributes:
                children: WebElement of the table.
                data_list: List of tabular data.

            Returns:
                data_list

            """
            try:
                children = parent.find_elements(By.XPATH, './/*')
                data_list = self.carve_table(children)
            except NoSuchElementException:
                data_list = []
            return data_list

        @staticmethod
        def carve_table(children: WebElement) -> list:
            """Scrapes tabular data.

            This method scrapes tabular data from a chosen location by
            iterating through webelements. Depending on the tag name it
            determines whether the data relates to a new row or column.

            Args:
                children: List of applicable WebElements.
                table_name: Name of table to be scraped.

            Attributes:
                i: Iterator variable used to handle list entries.
                data_list: List of tabular data.

            Returns:
                data_list

            """
            i: int = 0
            data_list = []
            for c in children:
                if c.tag_name == 'tr':
                    data_list.append([])
                    i += 1
                elif c.tag_name in ['th', 'td']:
                    data_list[i - 1].append(c.text)
            return data_list

        def quit(self) -> None:
            """Quits the webdriver.

            Returns:
                None

            """
            self.driver.quit()
            os.system("windscribe disconnect")
