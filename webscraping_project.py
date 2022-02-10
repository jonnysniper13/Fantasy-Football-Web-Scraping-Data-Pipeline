'''
This module scrapes player data from the Premier League fantasy football website.

The module contains one class in which all methods are contained and operated
out of. The class is also initiated when called in the main block. The scraper
cycles through each currently registered player and saves all their attributes,
points history, upcoming fixtures, and previous season data in a dictionary.
Each dictionary is then exported into a json file within a target directory,
along with a photo of that player.
Scraper progress is reported in the terminal, and will end automatically when
all players have been scraped.

The only usage of this module is to initiate an instance of the Class:
scraped_data = WebScraper()
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
import json
import time
from datetime import datetime
import os
import uuid
import urllib.request
from typing import Optional, Union
import getpass


class WebScraper:
    """This Class scrapes player data from the Premier League fantasy
    football website.

    See Module description and __init__ method for description of this
    Class.

    """

    def __init__(self, url: str, usr_name: Optional[str] = '', pword: Optional[str] = '', sample_mode: Optional[bool] = False) -> None:
        """Constructor method for the Class.

        This method creates all class variables, initiates the method
        to create a target folder for exporting data to, and initiates the
        main scraper method.

        Args:
            url: URL for website to be scraped.
            usr_name: Optional user input for user name.
            pword: Optional user input for password.
            sample_mode: Optional mode for testing the script by scraping one player only.

        Attributes:
            sample_mode: Mode for collecting one player sample for testing.
            url: URL for website to be scraped.
            tic: App timer start timestmamp.
            script_dir: Root directory path name.
            dir_name: Directory path name for data to be exported
                to.
            page_counter: Counter to count the current page for the
                list of players.
            chk_new_page: Boolean variable that determines if the current
                page is not the latest.
            total_pages: Total number of pages to be scraped.
            plyr_count: Counter to count the number of players that
                have been scraped.
            total_plyrs: Total number of players to be scraped.
            plyr_name: Name of player being scraped.
            plyr_dict: Dictionary of data for that player.
            tags: HTML XPATH and tag names to be used by Selenium.

        Returns:
            None

        """
        self.sample_mode: bool = sample_mode
        self.__get_credentials(usr_name, pword)
        self.url: str = url
        self.tic: float = time.perf_counter()
        self.script_dir: str = os.path.dirname(__file__)
        self.dir_name: str = f'raw_data/raw_data_{datetime.now().replace(microsecond=0).isoformat()}'
        self.make_folder(self.dir_name)
        self.page_counter: int = 1
        self.chk_new_page: bool = True
        self.total_pages: int = 0
        self.plyr_count: int = 0
        self.total_plyrs: int = 0
        self.plyr_dict: dict = {}
        self.plyr_name: str = ""
        self.tags: int = self.get_html_tags()
        self.cycle_scraper()

    def make_folder(self, *args: list[str]) -> str:
        """Helper function to create new folders in a specified location.

        This function creates a new folder in a location specified in the
        method arguments. It first creates the full path string and then
        calls a method to create the directory.

        Args:
            *args: Variable length argument list of folder names.

        Attributes:
            dir_path = Full folder path of the new folder.

        Raises:
            FileExistsError: Prints error message if an existing folder
            already exists.

        Returns:
            dir_path

        """
        dir_path = self.create_file_path(self.script_dir, *args)
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            print("Directory ", dir_path,  " already exists")
        return dir_path

    @staticmethod
    def create_file_path(root_dir: str, *args: list[str]) -> str:
        """Helper function to create full filepaths from arguments.

        This function creates a full filepath based on the root directory
        and further specified folder names.

        Args:
            root_dir: Root directory path.
            *args: Variable length argument list of folder names.

        Attributes:
            file_path: Full file path string.

        Returns:
            file_path

        """
        file_path: str = os.path.join(root_dir, *args)
        return file_path

    @staticmethod
    def get_html_tags() -> dict:
        """Dictionary of XPATH tags.

        Attributes:
            tags: XPATH element identifiers to be used throughout class.

        Returns:
            tags

        """
        tags: dict = {
            'TransferPage': 'href="/transfers"',
            'CookieButton': 'class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"',
            'UserNameField': 'type="email"',
            'PasswordField': 'type="password"',
            'LoginButton': 'type="submit"',
            'PlyrCount': 'class="ElementList__ElementsShown-j2itt6-1 dYWYXj"',
            'PlyrCountChild': './/strong',
            'PageCount': 'class="sc-bdnxRM sc-gtsrHT eVZJvz gfuSqG"',
            'PageCountChild': 'role="status"',
            'PlyrList': 'class="ElementDialogButton__StyledElementDialogButton-sc-1vrzlgb-0 hYsBeR"',
            'PlyrPopup': 'class="Dialog__Button-sc-5bogmv-2 ejzwPB"',
            'PlyrDetailSections': {
                'plyr_form': {
                    'xpath': 'class="ElementDialog__StatList-gmefnd-6 gRiDnT"',
                    'heading': 'h3',
                    'heading_value': 'div'},
                'plyr_ICT': {
                    'xpath': 'class="ElementDialog__ICTBody-gmefnd-12 cYozoC"',
                    'heading': 'h3',
                    'heading_value': 'strong'}
                    },
            'NextPageButton': 'class="PaginatorButton__Button-xqlaki-0 cDdTXr"',
            'PlyrDetails': 'class="sc-bdnxRM cqTHxz"',
            'PlyrStatus': 'type="error"',
            'PlyrImg': 'class="sc-bdnxRM bCIGtR"',
            'MatchDataKeyList': {
                '2021/22': 'PlyrMatches',
                'Previous Seasons': 'PrevSeasons',
                'Fixtures': 'FixList'},
            'PlyrMatches': 'class="ElementDialog__ScrollTable-gmefnd-15 bMDIkP ism-overflow-scroll"',
            'PrevSeasons': 'class="sc-bdnxRM fDjTdD"',
            'FixPage': 'href="#fixtures"',
            'FixList': 'class="Table-ziussd-1 fHBHIK"'
            }
        return tags

    def cycle_scraper(self) -> None:
        """Function to initiate the scraper method if the current page exists.

        The function will initiate the scraper method if the page counter
        does not exceed the number of pages on the website. Only initiates
        the scraper if this is true. After executing the scraper an
        enforced time delay is passed.

        Returns:
            None

        """
        while self.chk_new_page:
            self.scrape()
            time.sleep(10)
        return

    def scrape(self) -> None:
        """Function to initiate the web scraper.

        This the main web scraper method. It initiates the Chromedriver
        method and then launches the driver to the target website. It then
        handles the gdpr popup, logs in to the website and then navigates
        to the required part of the website.
        If this is the first iteration it counts the total number of
        players and pages that need to be scraped, else it navigates the website
        to the required player page.
        It then inititates the player scraper for all players on the
        selected page, quits the Chromedriver and increases the page counter by 1.

        Attributes:
            self.driver: Initiates the Chromedriver element.

        Returns:
            None

        """
        self.driver: WebElement = webdriver.Chrome(options=self.setup_options())
        self.driver.get(self.url)
        self.gdpr_consent()
        self.login()
        self.navigate(self.tags['TransferPage'])
        if self.page_counter == 1:
            self.count_total_players()
            self.count_total_pages()
        self.goto_page()
        self.cycle_thru_plyr_list()
        self.quit()
        if not self.sample_mode:
            if self.total_pages == self.page_counter:
                self.chk_new_page = False
            self.page_finished_msg()
            self.page_counter += 1
        return

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
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options

    def gdpr_consent(self) -> None:
        """Method that handles the gdpr consent popup.

        This method will find the accept cookies button on the gdpr popup
        and will close the popup, and switch back to the main content.

        Attributes:
            accept_cookies_button: Chromedriver WebElement for
                the accept cookies button.

        Returns:
            None

        """
        accept_cookies_button: WebElement = self.find_xpaths(self.tags['CookieButton'], multi=False, pause=True)
        self.close_popup(accept_cookies_button)
        self.driver.switch_to.default_content()
        return

    def find_xpaths(self, tag: str, multi: Optional[bool] = False, pause: Optional[bool] = False) -> Union[WebElement, list[WebElement]]:
        """Helper function to shorten syntax for finding data types.

        This function searches the current webpage for elements located by
        XPATH identifiers. It has optional arguments for searching for
        multiple occurences and for enforcing for dynamic time delays
        (up to 30 sec) based on screen loading time.

        Args:
            tag: XPATH element identifier to be located.
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
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//*[@{tag}]')))
            if multi:
                obj: list[WebElement] = self.driver.find_elements(By.XPATH, f"//*[@{tag}]")
            else:
                obj: WebElement = self.driver.find_element(By.XPATH, f"//*[@{tag}]")
        except TimeoutException:
            print("Loading took too much time!")
        time.sleep(1)
        return obj

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
            WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((popup_name)))
        except TimeoutException:
            print("Loading took too much time!")
        time.sleep(1)
        return

    def __get_credentials(self, usr_name: str = '', pword: str = '') -> None:
        """Private method that creates the login credentials.

        Creates login credentials based on arguments passed to the Class
        or user inputted arguments.

        Args:
            usr_name: Login user name.
            pword: Login password.

        Attributes:
            usr_name: Login user name.
            pword: Login password.

        Returns:
            None

        """
        if usr_name == '':
            usr_name = input("Enter username:")
        if pword == '':
            pword = getpass.getpass('Enter password:')
        self.usr_name = usr_name
        self.pword = pword
        return

    def login(self) -> None:
        """Method to handle login page.

        This method handles the login page by locating the appropiate
        fields and sending the appropiate keys to the page, before
        clicking the login button and ensuring the popup closes.

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
        usr_name_field: WebElement = self.find_xpaths(self.tags['UserNameField'])
        usr_name_field.send_keys(self.usr_name)
        pword_name_field: WebElement = self.find_xpaths(self.tags['PasswordField'])
        pword_name_field.send_keys(self.pword)
        login_button: WebElement = self.find_xpaths(self.tags['LoginButton'])
        self.close_popup(login_button)
        return

    def navigate(self, destination: str) -> None:
        """Method to navigate to a specified page.

        This method takes in a required XPATH element, locates it,
        and then clicks it.

        Args:
            destination: XPATH element to be found.

        Returns:
            None

        """
        nav_to = self.find_xpaths(destination, multi=False, pause=True)
        nav_to.click()
        return

    def count_total_players(self) -> None:
        """Method to count the total number of players to be scraped.

        This method finds the header for the text containing total number
        of players, and then locates the child element of which the text
        attribute can be retrieved.

        Attributes:
            total_plyrs_header: Parent element of total number
                of players.
            total_plyrs: Element containing total number of
                players.

        Returns:
            None

        """
        total_plyrs_header: WebElement = self.find_xpaths(self.tags['PlyrCount'])
        total_plyrs: WebElement = total_plyrs_header.find_element(By.XPATH, self.tags['PlyrCountChild'])
        self.total_plyrs = int(total_plyrs.text)
        return

    def count_total_pages(self) -> None:
        """Method to count the total number of pages to be scraped.

        This method finds the header for the text containing total number
        of pages, and then locates the child element of which the text
        attribute can be retrieved.

        Attributes:
            total_pages_header: Parent element of total number
                of pages.
            total_pages: Element containing total number of
                pages.

        Returns:
            None

        """
        total_pages_header: WebElement = self.find_xpaths(self.tags['PageCount'])
        total_pages: WebElement = total_pages_header.find_element(By.XPATH, f'./*[@{self.tags["PageCountChild"]}]')
        self.total_pages = int(total_pages.text.split()[2])
        return

    def goto_page(self) -> None:
        """Method that moves player list to required page.

        This method handles the method for clicking the 'Next Page'
        button to ensure it is called the required number of times (i.e.
        up to the page counter). Each time a new page is loaded, the
        button element is re-located and the boolean next page checker is
        reset.

        Attributes:
            page_buttons: Chromedriver WebElement for the
                'Next Page' button on the player list.

        Returns:
            None

        """
        for _ in range(1, self.page_counter):
            page_buttons: list[WebElement] = self.find_xpaths(self.tags['NextPageButton'], multi=True)
            self.click_next(page_buttons)
        return

    def click_next(self, page_buttons: list[WebElement]) -> None:
        """Method that clicks the next page button.

        This method will click the 'Next Page' button, located within
        a WebElement list. If a new page is clicked, the next page
        boolean checker is set to True. A time delay is enforced between
        each page.

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
        return

    def cycle_thru_plyr_list(self) -> None:
        """Cycles through player page and calls scraping method and output.

        This method will cycle through the players on the current page list
        and call the method for scraping the different types of
        data. After scraping the data it processes the output, clears the
        dictionary and reports on progress.

        Attributes:
            plyr_list: List of all player elements.
            popup: Player popup element.

        Returns:
            None

        """
        plyr_list: list[WebElement] = self.find_xpaths(self.tags['PlyrList'], multi=True, pause=True)
        for plyr in plyr_list:
            self.driver.execute_script("arguments[0].click();", WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(plyr)))
            self.get_plyr_stats()
            popup: WebElement = self.find_xpaths(self.tags['PlyrPopup'])
            self.plyr_count += 1
            self.close_popup(popup)
            self.process_output()
            if self.sample_mode:
                self.chk_new_page = False
                break
            self.progress_update()
        return

    def get_plyr_stats(self):
        """Handles scraping method for different data types.

        This method scrapes the different types of data available for
        each player and assigns them to the player dictionary.

        Returns:
            None

        """
        self.get_plyr_details()
        self.get_plyr_status()
        self.get_plyr_img_src()
        for k in self.tags['PlyrDetailSections']:
            self.get_plyr_attr(self.tags['PlyrDetailSections'][k], k)
        for k, v in self.tags['MatchDataKeyList'].items():
            self.get_match_data(k, v)
        return

    def get_plyr_details(self) -> None:
        """Gets players details.

        This method gets players main details, i.e. name, position,
        and team.

        Attributes:
            plyr_attr_parent: Parent web element of player.
            plyr_attr_children: Child web element of player.
            plyr_name: Player name.
            plyr_pos: Player position.
            plyr_team: Player team.

        Returns:
            None

        """
        plyr_attr_parent: WebElement = self.find_xpaths(self.tags['PlyrDetails'])
        plyr_attr_children: list[WebElement] = plyr_attr_parent.find_elements(By.XPATH, './*')
        for attr in plyr_attr_children:
            if attr.tag_name == 'h2':
                plyr_name: str = attr.text
            elif attr.tag_name == 'span':
                plyr_pos: str = attr.text
            elif attr.tag_name == 'div':
                plyr_team: str = attr.text
            else:
                pass
        self.plyr_name = plyr_name
        self.plyr_dict = {plyr_name: {'UUID': str(uuid.uuid4()), 'Position': plyr_pos, 'Team': plyr_team}}
        return

    def get_plyr_status(self):
        """Gets player fitness status.

        This method checks if the player is injured otherwise returns
        that they are fully fit.

        Attributes:
            plyr_status: Element containing player status.
            status: Player status text.

        Returns:
            None

        """
        try:
            plyr_status: WebElement = self.find_xpaths(self.tags['PlyrStatus'])
            status: str = plyr_status.text
        except NoSuchElementException:
            status: str = '100% Fit'
        self.plyr_dict[self.plyr_name]['Status'] = status
        return

    def get_plyr_img_src(self):
        """Gets player image src.

        This method finds element containing the player image and extracts
        the SRC string.

        Attributes:
            img_parent: Container element of image.
            img: Child element of image.
            img_src: SRC string

        Returns:
            None

        """
        img_parent: WebElement = self.find_xpaths(self.tags['PlyrImg'])
        img: WebElement = img_parent.find_element(By.XPATH, './/*')
        img_src: str = img.get_attribute('src')
        self.plyr_dict[self.plyr_name]['Image SRC'] = img_src
        return

    def get_plyr_attr(self, key_list: dict, k: str):
        """Gets player other attributes.

        This method collects players form attributes.

        Args:
            key_list: Dictionary of keys to cycle through.
            k: Key iterable.

        Attributes:
            plyr_attr_parent: Parent web element of player.
            plyr_attr_children: Child web element of player.
            attr_name: Name of attribute to be scraped.
            attr_value: Value of attribute to be scraped.

        Returns:
            None

        """
        plyr_attr_parent: WebElement = self.find_xpaths(key_list['xpath'])
        plyr_attr_children: list[WebElement] = plyr_attr_parent.find_elements(By.XPATH, './/*')
        if k == 'plyr_ICT':
            self.plyr_dict[self.plyr_name]['ICT'] = {}
        for attr in plyr_attr_children:
            if attr.tag_name == key_list['heading']:
                attr_name: str = attr.text
            elif attr.tag_name == key_list['heading_value']:
                attr_value: str = attr.text
                if k == 'plyr_ICT':
                    self.plyr_dict[self.plyr_name]['ICT'][attr_name] = attr_value
                else:
                    self.plyr_dict[self.plyr_name][attr_name] = attr_value
                attr_name = ''
                attr_value = ''
        return

    def get_match_data(self, match_data_type: str, match_data_tag: str) -> None:
        """Scrapes player matches.

        This method scrapes data on player's matches (current season,
        upcoming fixtures and previous seasons.

        Args:
            match_data_type: Type of match data to be scraped.
            match_data_tag: Tag for the type of match data.

        Attributes:
            plyr_attr_parents: WebElement containing the
                tables that are to be scraped.
            table_name: List of tables that are to be scraped, for using
                as keys in the dictionary.

        Returns:
            None

        """
        try:
            if match_data_type == 'Fixtures':
                self.navigate(self.tags['FixPage'])
                plyr_attr_parent: WebElement = self.find_xpaths(self.tags[match_data_tag])
            else:
                plyr_attr_grandparents = self.find_xpaths(self.tags[match_data_tag])
                plyr_attr_parent = plyr_attr_grandparents.find_element(By.XPATH, './/table')
            plyr_attr_children = plyr_attr_parent.find_elements(By.XPATH, './/*')
            self.get_table(plyr_attr_children, match_data_type)
        except NoSuchElementException:
            self.plyr_dict[self.plyr_name][match_data_type] = 'No data'
        return

    def get_table(self, plyr_attr_children: WebElement, match_data_type: str) -> None:
        """Scrapes tabular data.

        This method scrapes tabular data from a chosen location by
        iterating through webelements. Depending on the tag name it
        determines whether the data relates to a new row or column.

        Args:
            plyr_attr_children: List of applicable
                WebElements.
            match_data_type: Type of match data to be scraped.

        Attributes:
            i: Iterator variable used to handle list entries.

        Returns:
            None

        """
        i: int = 0
        self.plyr_dict[self.plyr_name][match_data_type] = []
        for attr in plyr_attr_children:
            if attr.tag_name == 'tr':
                self.plyr_dict[self.plyr_name][match_data_type].append([])
                i += 1
            elif attr.tag_name == 'th' or attr.tag_name == 'td':
                self.plyr_dict[self.plyr_name][match_data_type][i - 1].append(attr.text)
        return

    def process_output(self) -> None:
        """Handles the routine for processing the scraper output.

        This method calls the method to make new folders for scraper
        output to be saved within. It then creates full file paths
        that include the file name, to support further exporting of
        data. It then calls the method in which data is exported to file.

        Attributes:
            plyr_dir: Directory path for player data to be saved.
            img_dir: Directory path for player image to be saved.
            json_file_path: Dir path for json file to be saved.
            img_path: Dir path for image to be saved.

        Returns:
            None

        """
        plyr_dir, img_dir = self.prep_dir()
        json_file_path: str = self.create_file_path(plyr_dir, f'{plyr_dir}/data.json')
        img_path: str = self.create_file_path(img_dir, '0.png')
        self.write_to_file(json_file_path, img_path)
        return

    def prep_dir(self) -> list[str]:
        """Prepares the directories for saving json file and image data.

        This method handles the creation of new folders for the player data
        to be saved within.

        Args:
            plyr_name: Name of current playing being scraped.
            plyr_dict: Dictionary of scraped data.

        Attributes:
            plyr_dir: Directory path for player data to be saved.
            img_dir: Directory path for player image to be saved.

        Returns:
            plyr_dir
            img_dir

        """
        plyr_dir: str = self.make_folder(self.dir_name, self.plyr_dict[self.plyr_name]['UUID'])
        img_dir: str = self.make_folder(plyr_dir, 'images')
        return plyr_dir, img_dir

    def write_to_file(self, json_file_path: str, img_path: str) -> None:
        """Saves player dictionary and image in player folder.

        This method saves the player dictionary to a json file in the
        player's target folder. It also saves the player's image using
        urllib.

        Args:
            json_file_path: Dir path for json file to be saved.
            img_path: Dir path for image to be saved.

        Returns:
            None

        """
        with open(json_file_path, 'x') as json_file:
            json.dump(self.plyr_dict, json_file)
        urllib.request.urlretrieve(self.plyr_dict[self.plyr_name]['Image SRC'], img_path)
        return

    def calc_timestep(self) -> float:
        """Calculates the time elapsed.

        This method calculates the difference between the current time
        and the timestamp that was assigned at the start of the Class
        execution.

        Attributes:
            toc: Current timestamp.
            time_elapsed: Difference between toc and tic.

        Returns:
            time_elapsed

        """
        toc: float = time.perf_counter()
        time_elapsed: float = toc - self.tic
        return time_elapsed

    def progress_stats(self) -> list[float]:
        """Calculates stats on the scraper's progress.

        This method calculates the % progress, the amount of time that has
        elapsed and the estimated time to completion of the web scraper.

        Attributes:
            progress: % complete.
            time_elapsed: Amount of time elapsed since start of execution.
            est_time: Estimated time until completion.

        Returns:
            progress
            time_elapsed
            est_time

        """
        progress: float = self.plyr_count / self.total_plyrs
        time_elapsed: float = self.calc_timestep()
        est_time: float = (time_elapsed / progress) * (self.total_plyrs - self.plyr_count) / self.total_plyrs
        return progress, time_elapsed, est_time

    def progress_update(self) -> None:
        """Prints stats on the scraper's progress.

        Args:
            plyr_name: Name of last player scraped.

        Attributes:
            progress: % complete.
            time_elapsed: Amount of time elapsed since start of execution.
            est_time: Estimated time until completion.

        Returns:
            None

        """
        prog_stats = self.progress_stats()
        print(f'{self.plyr_name} just scraped.')
        print(f'{self.plyr_count} players of {self.total_plyrs} scraped in {round(prog_stats[1] / 60)} minutes.')
        print(f'{100 * prog_stats[0]:.2f}% complete. Estimated {round(prog_stats[2] / 60)} minutes remaining.')
        return

    def quit(self) -> None:
        """Quits the webdriver.

        Returns:
            None

        """
        self.driver.quit()
        return

    def page_finished_msg(self) -> None:
        """Prints a page completed status message.

        Returns:
            None

        """
        line_brk = '#########################################'
        print(f'{line_brk}\nPage {self.page_counter} of {self.total_pages} finished.\n{line_brk}')
        return


if __name__ == "__main__":
    ff_scraper = WebScraper('https://fantasy.premierleague.com/')
