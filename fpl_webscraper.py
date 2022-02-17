"""
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
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import json
import time
from datetime import datetime
import os
import cred
import uuid
import urllib.request
from typing import Optional, List
import getpass
import boto3
from webscraper import WebScraper


class FPLWebScraper:
    """This Class scrapes player data from the Premier League fantasy
    football website.

    See Module description and __init__ method for description of this
    Class.

    """

    def __init__(self, url: str, sample_mode: Optional[bool] = False) -> None:
        """Constructor method for the Class.

        This method creates all class variables, initiates the method
        to create a target folder for exporting data to, and initiates the
        main scraper method and attributes.

        Args:
            url: URL for website to be scraped.
            sample_mode: Optional mode for testing the script by scraping one player
                only.

        Attributes:
            sample_mode: Mode for collecting one player sample for testing.
            url: URL for website to be scraped.
            tic: App timer start timestmamp.
            script_dir: Root directory path name.
            timestamp: Create timestamp for scraper.
            page_counter: Counter to count the current page for the
                list of players.
            chk_new_page: Boolean variable that determines if the current
                page is not the latest.
            total_pages: Total number of pages to be scraped.
            plyr_count: Counter to count the number of players that
                have been scraped.
            total_plyrs: Total number of players to be scraped.
            plyr: WebElement for the current player being scraped.
            plyr_dict: Dictionary of data for that player.
            plyr_dir: Directory path for player data to be saved.
            img_dir: Directory path for player image to be saved.
            html_inputs: HTML XPATH and tag names to be used by Selenium.
            s3_client: Initiates the boto3 client.

        Returns:
            None

        """
        self.sample_mode: bool = sample_mode
        self.url: str = url
        self.tic: float = time.perf_counter()
        self.script_dir: str = os.path.dirname(__file__)
        self.timestamp: datetime = datetime.now().replace(microsecond=0).isoformat()
        self.page_counter: int = 1
        self.chk_new_page: bool = True
        self.total_pages: int = 0
        self.plyr_count: int = 0
        self.total_plyrs: int = 0
        self.plyr: WebElement = ''
        self.plyr_dict: dict = {}
        self.plyr_dir: str = ''
        self.img_dir: str = ''
        self.html_inputs: int = self.get_html_inputs()
        self.s3_client = boto3.client('s3')
        self.cycle_scraper()

    def get_html_inputs(self) -> dict:
        """Dictionary of XPATH tags.

        Attributes:
            tags: XPATH element identifiers to be used throughout class.

        Returns:
            tags

        """
        tags: dict = {
            'CookieButton': 'class="_2hTJ5th4dIYlveipSEMYHH BfdVlAo_cgSVjDUegen0F js-accept-all-close"',
            'Credentials': {
                'Username': self.__get_credentials()[0],
                'Username xpath': 'type="email"',
                'Password': self.__get_credentials()[1],
                'Password xpath': 'type="password"',
                'Login xpath': 'type="submit"'},
            'TransferPage': 'href="/transfers"',
            'PlyrCount': 'class="ElementList__ElementsShown-j2itt6-1 dYWYXj"',
            'PlyrCountChild': './/strong',
            'PageCount': 'class="sc-bdnxRM sc-gtsrHT eVZJvz gfuSqG"',
            'PageCountChild': './*[@role="status"]',
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
        """Function to initiate the scraper method if the next page exists.

        The function will re-initiate the scraper method if the page counter
        does not exceed the number of pages on the website. Only initiates
        the scraper if this is true. After executing the scraper the WebDriver
        is closed and an enforced time delay is passed on each iteration.
        After completing the scraper, a timestamp txt file is written.

        Returns:
            None

        """
        while self.chk_new_page:
            self.ws = WebScraper()
            self.scrape()
            self.ws.quit()
            time.sleep(30)
        self.write_timestamp()

    def scrape(self) -> None:
        """Function to initiate the web scraper.

        This the main web scraper method. It launches the driver to the target website.
        It then handles the gdpr popup, logs in to the website and then navigates
        to the required part of the website.
        If this is the first iteration it counts the total number of
        players and pages that need to be scraped, else it navigates the website
        to the required player page.
        It then inititates the player scraper for all players on the selected page,
        and increases the page counter by 1.

        Attributes:
            total_plyrs: Total number of players in string format.
            total_pages: Total number of pages in string format.

        Returns:
            None

        """
        self.ws.driver.get(self.url)
        self.ws.gdpr_consent(self.html_inputs['CookieButton'])
        self.ws.login(self.html_inputs['Credentials'])
        self.ws.navigate(self.html_inputs['TransferPage'])
        if self.page_counter == 1:
            total_plyrs: str = self.ws.retrieve_attr(self.html_inputs['PlyrCount'], self.html_inputs['PlyrCountChild'])
            self.total_plyrs = int(total_plyrs)
            total_pages: str = self.ws.retrieve_attr(self.html_inputs['PageCount'], self.html_inputs['PageCountChild'])
            self.total_pages = int(total_pages.split()[-1])
        self.ws.goto_page(self.html_inputs['NextPageButton'], self.page_counter)
        self.cycle_thru_plyr_list()
        if not self.sample_mode:
            if self.total_pages == self.page_counter:
                self.chk_new_page = False
            self.page_finished_msg()
            self.page_counter += 1

    @staticmethod
    def __get_credentials() -> List[str]:
        """Private method that creates the login credentials.

        Creates login credentials based on arguments passed to the Class
        or user inputted arguments.

        Attributes:
            usr_name: Login user name.
            pword: Login password.

        Returns:
            user_name
            pword

        """
        try:
            usr_name: str = cred.username
        except AttributeError:
            usr_name: str = input("Enter username:")
        try:
            pword: str = cred.password
        except AttributeError:
            pword: str = getpass.getpass('Enter password:')
        return usr_name, pword

    def cycle_thru_plyr_list(self) -> None:
        """Cycles through player page and calls scraping method and output.

        This method will cycle through the players on the current page list
        and call the method for scraping the different types of
        data. After scraping the data it clears the dictionary, reports on
        progress and resets instance attributes.

        Attributes:
            plyr_list: List of all player elements.
            popup: Player popup element.

        Returns:
            None

        """
        plyr_list = self.ws.find_list(self.html_inputs['PlyrList'])
        for plyr in plyr_list:
            self.plyr = plyr
            popup = self.ws.open_popup(self.plyr, self.html_inputs['PlyrPopup'])
            self.get_plyr_stats()
            self.plyr_count += 1
            self.ws.close_popup(popup)
            if self.sample_mode:
                self.chk_new_page = False
                break
            self.progress_update()
            self.plyr_dict = {}
            self.plyr_dir = ''
            self.img_dir = ''

    def get_plyr_stats(self) -> None:
        """Handles scraping method for different data types.

        This method scrapes the different types of data available for
        each player and assigns them to the player dictionary which is
        then written to a file. This is only performed if the player
        hasn't recently been scraped.

        Returns:
            None

        """
        self.create_plyr_dict()
        plyr_already_scraped = self.check_plyr_scraped()
        if not plyr_already_scraped:
            self.get_plyr_status()
            self.get_plyr_img_data()
            self.get_plyr_form_data()
            self.get_plyr_match_data()
            print(self.plyr_dict)
            self.process_output()

    def create_plyr_dict(self) -> None:
        """This method creates the player dictionary based on attributes.

        This method retrieves player name, position, and team and assigns
        these to the player dictionary.

        Attributes:
            id: Unique ID for each player that does not change.

        Returns:
            None

        """
        try:
            plyr_name, plyr_pos, plyr_team = self.ws.get_from_popup_header(self.html_inputs['PlyrDetails'], './*', ['h2', 'span', 'div'])
        except ValueError:
            plyr_name, plyr_pos, plyr_team = ['Error', 'Error', 'Error']
        id: str = ' '.join([plyr_team, plyr_pos, plyr_name]).replace(' ', '-')
        self.plyr_dict = {
            'Name': plyr_name,
            'Unique ID': id,
            'UUID': str(uuid.uuid4()),
            'Position': plyr_pos,
            'Team': plyr_team,
            'Last Scraped': self.timestamp}

    def get_plyr_status(self) -> None:
        """Gets player fitness status.

        This method checks if the player is injured otherwise returns
        that they are fully fit. This status is added to the dictionary.

        Attributes:
            status: Player status text.

        Returns:
            None

        """
        status: str = self.ws.retrieve_attr(self.html_inputs['PlyrStatus'])
        if status is None:
            status: str = '100% Fit'
        self.plyr_dict['Status'] = status

    def get_plyr_img_data(self) -> None:
        """Gets player image data.

        This method gets the image src for the player and appends it to the player
        dictionary.

        Returns:
            None

        """
        self.plyr_dict['Image SRC'] = self.ws.retrieve_attr(self.html_inputs['PlyrImg'], './/*', 'src')

    def get_plyr_form_data(self) -> None:
        """Gets player form data.

        This method gets the form data for the player and appends it to the
        player dictionary.

        Attributes:
            data_dict: Dictionary of data to be returned.

        Returns:
            None

        """
        for k in self.html_inputs['PlyrDetailSections']:
            data_dict = self.ws.get_from_fields(self.html_inputs['PlyrDetailSections'][k])
            self.plyr_dict.update(data_dict)

    def get_plyr_match_data(self):
        """Gets player match data.

        This method gets the match data for the player and appends it to the
        player dictionary.

        Attributes:
            parent: Parent of the WebElement child containing the table.
            child: WebElement containing the tables that are to be scraped.

        Returns:
            None

        """
        for k, v in self.html_inputs['MatchDataKeyList'].items():
            if k == 'Fixtures':
                self.ws.navigate(self.html_inputs['FixPage'])
                child: WebElement = self.ws.find_xpaths(self.html_inputs[v])
            else:
                parent: WebElement = self.ws.find_xpaths(self.html_inputs[v])
                child: WebElement = parent.find_element(By.XPATH, './/table')
            self.plyr_dict[k] = self.ws.get_from_table(child)

    def check_plyr_scraped(self) -> bool:
        """This method checks if a player has recently been scraped.

        This method checks if a player has recently been scraped
        by checking the appropiate key in the data output dictionary.
        If a file exists but it was scraped in the last day,
        the player will not be scraped again. For all other
        permutations, the file will be deleted and player scraped.

        Attributes:
            json_file = Full path for player json file.
            old_plyr_dict = Previously scraped dictionary of player data.
            last_scraped = Date player was last scraped.
            delta = Delta between today and the date the player was last
                scraped.

        Returns:
            None

        """
        self.prep_dir()
        try:
            json_file: str = os.path.join(self.plyr_dir, f'{self.plyr_dict["Unique ID"]}_data.json')
            with open(json_file) as f:
                old_plyr_dict: dict = json.load(f)
            last_scraped: datetime = datetime.strptime(old_plyr_dict['Last Scraped'][:10], '%Y-%m-%d')
            delta: int = (datetime.now() - last_scraped).days
            if delta > 1:
                os.remove(json_file)
                return False
            return True
        except FileNotFoundError:
            return False

    def prep_dir(self) -> None:
        """Prepares the directories for saving json file and image data.

        This method handles the creation of new folders for the player data
        to be saved within.

        Returns:
            None

        """
        self.plyr_dir = self.make_folder('raw_data', self.plyr_dict['Unique ID'])
        self.img_dir = self.make_folder(self.plyr_dir, 'images')
        return

    def make_folder(self, *args: List[str]) -> str:
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
            os.makedirs(dir_path)
            return dir_path
        except FileExistsError:
            return dir_path

    @staticmethod
    def create_file_path(root_dir: str, *args: List[str]) -> str:
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

    def process_output(self) -> None:
        """Handles the routine for processing the scraper output.

        This method calls creates full file paths that include the
        file name, to support further exporting of data. It then calls
        the method in which data is exported to file. All data is then
        uploaded to an s3 bucket.

        Attributes:
            json_file_path: Dir path for json file to be saved.
            img_file_path: Dir path for image to be saved.
            s3_plyr_path: Dir path on s3 bucket.

        Returns:
            None

        """
        json_file_path: str = self.create_file_path(self.plyr_dir, f'{self.plyr_dict["Unique ID"]}_data.json')
        img_file_path: str = self.create_file_path(self.img_dir, f'{self.plyr_dict["Unique ID"]}_0.png')
        self.write_json(json_file_path)
        self.write_img(img_file_path)
        s3_plyr_path = f'raw_data/{self.plyr_dict["Unique ID"]}'
        self.s3_client.upload_file(json_file_path, 'fplplayerdatabucket', f'{s3_plyr_path}/{self.plyr_dict["Unique ID"]}_data.json')
        self.s3_client.upload_file(img_file_path, 'fplplayerdatabucket', f'{s3_plyr_path}/images/{self.plyr_dict["Unique ID"]}_0.png')

    def write_json(self, json_file_path: str) -> None:
        """Saves player dictionary in player folder.

        This method saves the player dictionary to a json file in the
        player's target folder.

        Args:
            json_file_path: Dir path for json file to be saved.

        Returns:
            None

        """
        with open(json_file_path, 'x') as json_file:
            json.dump(self.plyr_dict, json_file)

    def write_img(self, img_file_path: str) -> None:
        """Saves player image in player folder if it is empty.

        This method checks if the player's image folder is empty
        and then saves the player's image then, provided the
        urllib path starts with 'http'.

        Args:
            img_file_path: Dir path for image to be saved.

        Returns:
            None

        """
        if (len(os.listdir(os.path.dirname(img_file_path))) == 0 and
                self.plyr_dict['Image SRC'].lower().startswith('http')):
            urllib.request.urlretrieve(self.plyr_dict['Image SRC'], img_file_path)

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

    def progress_stats(self) -> List[float]:
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

        Attributes:
            progress: % complete.
            time_elapsed: Amount of time elapsed since start of execution.
            est_time: Estimated time until completion.

        Returns:
            None

        """
        prog_stats = self.progress_stats()
        print(f'{self.plyr_dict["Name"]} just scraped.')
        print(f'{self.plyr_count} players of {self.total_plyrs} scraped in {round(prog_stats[1] / 60)} minutes.')
        print(f'{100 * prog_stats[0]:.2f}% complete. Estimated {round(prog_stats[2] / 60)} minutes remaining.')

    def page_finished_msg(self) -> None:
        """Prints a page completed status message.

        Returns:
            None

        """
        line_brk = '#########################################'
        print(f'{line_brk}\nPage {self.page_counter} of {self.total_pages} finished.\n{line_brk}')

    def write_timestamp(self) -> None:
        """Writes a txt file in the raw data folder containing the timestamp.

        Returns:
            None

        """
        txt_path = os.path.join(self.script_dir, 'raw_data', 'timestamp.txt')
        with open(txt_path, 'w') as f:
            f.write(f'Scraper last ran at: {self.timestamp}')
        self.s3_client.upload_file(txt_path, 'fplplayerdatabucket', 'raw_data/timestamp.txt')


if __name__ == "__main__":
    ff_scraper = FPLWebScraper('https://fantasy.premierleague.com/')
