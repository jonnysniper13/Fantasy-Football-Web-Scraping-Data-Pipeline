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
from selenium.common.exceptions import NoSuchElementException
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
from xpaths import xpaths


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
            project_dir: Root directory path name.
            timestamp: Create timestamp for scraper.
            page_counter: Counter to count the current page for the
                list of players.
            chk_new_page: Boolean variable that determines if the current
                page is not the last.
            total_pages: Total number of pages to be scraped.
            plyr_count: Counter to count the number of players that
                have been scraped.
            total_plyrs: Total number of players to be scraped.
            plyr: WebElement for the current player being scraped.
            plyr_dict: Dictionary of data for that player.
            plyr_dir: Directory path for player data to be saved.
            img_dir: Directory path for player image to be saved.
            page_list: List of players on the open page.
            line_break: Line break string to be used for print statements.
            s3_client: Initiates the boto3 client.

        Returns:
            None

        """
        self.sample_mode: bool = sample_mode
        self.url: str = url
        self.tic: float = time.perf_counter()
        self.project_dir: str = os.path.dirname(os.path.dirname(__file__))
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
        self.page_list: list = []
        self.line_break: str = ('=' * 0.8 * os.get_terminal_size().columns)
        self.s3_client = boto3.client('s3')
        self.start_scraper()

    def start_scraper(self) -> None:
        """Function to initiate the scraper method.

        The function will initiate the scraper method and navigates to the
        required part of the website. It also takes counts on the total
        number of pages and players. When complete it quits the WebDriver.

        Returns:
            None

        """
        self.ws = WebScraper()
        self.navigate_website()
        self.get_counts()
        self.scrape_handler()
        self.ws.quit()

    def navigate_website(self) -> None:
        """Navigates website actions to get to the desired page.

        The function will navigate the website by initiating it, handling
        gdpr popus, logging in, and then going to the desired page.

        Attributes:
            credentials: List of credentials for the login page.

        Returns:
            None

        """
        self.ws.driver.get(self.url)
        self.ws.gdpr_consent(xpaths['CookieButton'])
        credentials: list[str] = self.__get_credentials()
        self.ws.login(xpaths['Credentials'], credentials)
        self.ws.go_to(xpaths['TransferPage'])

    def get_counts(self) -> None:
        """Function to get total numbers of players and pages.

        The function will find the WebElement containing the total number
        of players and pages and will assign these to attributes.

        Attributes:
            total_plyrs: Text from WebElement of total player.
            total_pages: Text from WebElement of total pages.

        Returns:
            None

        """
        total_plyrs: str = self.ws.retrieve_attr(xpaths['PlyrCount'], xpaths['PlyrCountChild'])
        self.total_plyrs = int(total_plyrs)
        total_pages: str = self.ws.retrieve_attr(xpaths['PageCount'], xpaths['PageCountChild'])
        self.total_pages = int(total_pages.split()[-1])

    def scrape_handler(self) -> None:
        """Function to control how the target page is handled.

        Provided there are still new pages to be handled, this method
        will create a player list for the current page of players on the
        page, and then initiate the method to cycle through these players.
        Once complete, it will move on to the next page, reset and increment
        counters/arrtibutes, and write a page finished report.

        Returns:
            None

        """
        while self.chk_new_page:
            self.make_plyr_list()
            self.cycle_thru_plyr_list()
            self.chk_new_page = self.ws.click_next(xpaths['NextPageButton'])
            if not self.sample_mode:
                self.page_finished_msg()
                self.write_report()
                [self.page_counter] = self.increase_counters(self.page_counter)

    def make_plyr_list(self) -> None:
        """Creates the list of players on the current page.

        This method finds the table of players on the current page, and creates
        a list from it. For each player and ID is generated based on their name,
        club and position.

        Attributes:
            plyr_text = Text from WebElement.
            plyr_id = Generated id from WebElement text.

        Returns:
            None

        """
        self.page_list = []
        plyr_list = self.ws.find_list('class="Media__Body-sc-94ghy9-2 eflLUc"')
        for plyr in plyr_list:
            plyr_text: list[str] = plyr.find_elements(By.XPATH, './/div')
            plyr_id: str = '-'.join([plyr_text[1].text, plyr_text[0].text])
            self.page_list.append(plyr_id)
        time.sleep(self.ws.human_lag(5, 1))

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
        data. It also checks whether the player meets the criteria for being
        recently scraped and will not re-scrape if this is the case.
        After scraping the data it clears the dictionary, reports on
        progress and resets instance attributes.

        Attributes:
            plyr_container: List of all player elements.
            list_count: Counter for players on the page list.
            plyr_already_scraped: Checks if player has been recently scraped.
            popup: Player popup element.

        Returns:
            None

        """
        plyr_container: List[WebElement] = self.ws.find_list(xpaths['PlyrList'])
        list_count: int = 0
        for plyr in plyr_container:
            self.plyr_dict['ID'] = self.page_list[list_count]
            plyr_already_scraped: bool = self.check_plyr_scraped()
            if not plyr_already_scraped:
                popup: WebElement = self.ws.open_popup(plyr, xpaths['PlyrPopup'])
                self.get_plyr_stats()
                self.ws.close_popup(popup)
            if self.sample_mode:
                self.chk_new_page = False
                break
            self.plyr_count, list_count = self.increase_counters(self.plyr_count, list_count)
            self.progress_update()
            self.plyr_dict, self.plyr_dir, self.img_dir = self.reset_var(self.plyr_dict, self.plyr_dir, self.img_dir)

    def check_plyr_scraped(self) -> bool:
        """This method checks if a player has recently been scraped.

        This method checks if a player has recently been scraped
        by checking the appropiate key in the data output dictionary.
        If a file exists and it was scraped recently (see delta),
        the player will not be scraped again. For all other
        permutations, the file will be deleted and player scraped.
        If the player has been recently scraped and won't be rescraped,
        the player dictionary name is updated from the old dictionary.

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
            json_file: str = os.path.join(self.plyr_dir, f'{self.plyr_dict["ID"]}_data.json')
            with open(json_file) as f:
                old_plyr_dict: dict = json.load(f)
            last_scraped: datetime = datetime.strptime(old_plyr_dict['Last Scraped'][:10], '%Y-%m-%d')
            delta: int = (datetime.now() - last_scraped).days
            if delta >= 7:
                os.remove(json_file)
                return False
            self.plyr_dict['Name'] = old_plyr_dict['Name']
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
        self.plyr_dir = self.make_folder('raw_data', self.plyr_dict['ID'])
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
        dir_path = self.create_file_path(self.project_dir, *args)
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

    @staticmethod
    def increase_counters(*args) -> list:
        """Increases counters by 1.

        Args:
            args: Arguments to be updated.

        Attributes:
            output: List of updated arguments.

        Returns:
            output

        """
        output: list = []
        for arg in args:
            output.append(arg + 1)
        return output

    @staticmethod
    def reset_var(*args) -> list:
        """Resets variables to empty, respecting their data type.

        Args:
            args: Arguments to be updated.

        Attributes:
            output: List of updated arguments.

        Returns:
            output

        """
        output: list = []
        for arg in args:
            if type(arg) == dict:
                arg = {}
            elif type(arg) == list:
                arg = []
            else:
                arg = ''
            output.append(arg)
        return output

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
        self.get_plyr_status()
        self.get_plyr_img_data()
        self.get_plyr_form_data()
        self.get_plyr_match_data()
        self.process_output()

    def create_plyr_dict(self) -> None:
        """This method creates the player dictionary based on attributes.

        This method retrieves player name, position, UUID, team and timestamp,
        and assigns these to the player dictionary.

        Returns:
            None

        """
        plyr_name, plyr_pos, plyr_team = self.ws.get_from_popup_header(xpaths['PlyrDetails'], './*', ['h2', 'span', 'div'])
        self.plyr_dict['Name'] = plyr_name
        self.plyr_dict['UUID'] = str(uuid.uuid4())
        self.plyr_dict['Position'] = plyr_pos
        self.plyr_dict['Team'] = plyr_team
        self.plyr_dict['Last Scraped'] = self.timestamp

    def get_plyr_status(self) -> None:
        """Gets player fitness status.

        This method checks if the player is injured otherwise returns
        that they are fully fit. This status is added to the dictionary.

        Attributes:
            status: Player status text.

        Returns:
            None

        """
        status: str = self.ws.retrieve_attr(xpaths['PlyrStatus'])
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
        self.plyr_dict['Image SRC'] = self.ws.retrieve_attr(xpaths['PlyrImg'], './/*', 'src')

    def get_plyr_form_data(self) -> None:
        """Gets player form data.

        This method gets the form data for the player and appends it to the
        player dictionary.

        Attributes:
            data_dict: Dictionary of data to be returned.

        Returns:
            None

        """
        for k in xpaths['PlyrDetailSections']:
            data_dict = self.ws.get_from_fields(xpaths['PlyrDetailSections'][k])
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
        for k, v in xpaths['MatchDataKeyList'].items():
            try:
                if k == 'Fixtures':
                    self.ws.go_to(xpaths['FixPage'])
                    child: WebElement = self.ws.find_xpaths(xpaths[v])
                else:
                    parent: WebElement = self.ws.find_xpaths(xpaths[v])
                    child: WebElement = parent.find_element(By.XPATH, './/table')
                self.plyr_dict[k] = self.ws.get_from_table(child)
            except NoSuchElementException:
                self.plyr_dict[k] = 'No data'

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
        json_file_path: str = self.create_file_path(self.plyr_dir, f'{self.plyr_dict["ID"]}_data.json')
        img_file_path: str = self.create_file_path(self.img_dir, f'{self.plyr_dict["ID"]}_0.png')
        self.write_json(json_file_path)
        self.write_img(img_file_path)
        #s3_plyr_path = f'raw_data/{self.plyr_dict["ID"]}'
        #self.s3_client.upload_file(json_file_path, 'fplplayerdatabucket', f'{s3_plyr_path}/{self.plyr_dict["ID"]}_data.json')
        #self.s3_client.upload_file(img_file_path, 'fplplayerdatabucket', f'{s3_plyr_path}/images/{self.plyr_dict["ID"]}_0.png')

    def write_json(self, json_file_path: str) -> None:
        """Saves player dictionary in player folder.

        This method saves the player dictionary to a json file in the
        player's target folder.

        Args:
            json_file_path: Dir path for json file to be saved.

        Returns:
            None

        """
        with open(json_file_path, 'w') as json_file:
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
        print(
            f"""{self.line_break}
            Page {self.page_counter} of {self.total_pages} finished.
            {self.line_break}""")

    def write_report(self) -> None:
        """Writes a txt file in the raw data folder containing a timestamp and data verification checks.

        This report is saved in the raw_data folder as well as being uploaded to the
        s3 bucket.

        Attributes:
            txt_path: String path where the report is to be saved.

        Returns:
            None

        """
        txt_path: str = os.path.join(self.project_dir, 'raw_data', 'report.txt')
        with open(txt_path, 'w') as f:
            f.write(
                f"""Scraper ran at: {self.timestamp}.
                {self.plyr_count} players scraped.

                {self.verification_report}""")
        #self.s3_client.upload_file(txt_path, 'fplplayerdatabucket', 'raw_data/report.txt')

    def verification_report(self) -> str:
        """Performs a data verification check to confirm that the ID matches the player.

        Verification is confirmed by verifying that the name part of the player
        ID appears within the player name. This won't be the case for 100% of the
        players due to abbreviations permutations - hence the need for this report.

        Attributes:
            report: Output report string to be printed.
            path: Location of player dictionaries.
            plyr_dict: Player dictionary read from json file.

        Returns:
            None

        """
        report: str = ''
        path = os.path.join(self.project_dir, 'raw_data')
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename[-4:] == 'json':
                    with open(os.path.join(root, filename)) as f:
                        plyr_dict = json.load(f)
                    if plyr_dict['ID'][7:] not in plyr_dict['Name']:
                        report = f"""Please verify the following:

                        {plyr_dict['ID'][7:]} = {plyr_dict['Name']}, {plyr_dict['Name']}, {plyr_dict['Name']}"""
        return report


if __name__ == "__main__":
    ff_scraper = FPLWebScraper('https://fantasy.premierleague.com/')
