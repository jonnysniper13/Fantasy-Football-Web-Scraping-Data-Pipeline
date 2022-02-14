import unittest
from webscraping_project import WebScraper


class WebScraperTestCase(unittest.TestCase):
    """This Class carries out units tests on the WebScraper script.

    The WebScraper script is tested by comparing scraped data to that
    retrieved manually and stored in a local dictionary.
    Scraped data types are also compared.
    """

    def setUpClass(self) -> None:
        """Sets up the answers for the test cases.

        This function supplies a manually inputted dictionary of scraped
        data for which newly scraped data can be compared to. Only one
        instance of a player is tested.
        It also sets up an instance of the WebScraper class in sample
        mode, meaning only player's data is scraped.
        """
        self.sample = WebScraper('https://fantasy.premierleague.com/', sample_mode=True)
        self.sample_plyr = self.sample.plyr_dict
        self.sample_total_plyrs = self.sample.total_plyrs
        self.sample_total_pages = self.sample.total_pages
        self.test_plyr_name = "Ederson Santana de Moraes"
        self.test_answers = {
            "Sample Player Stats": {
                "Position": "Goalkeeper",
                "Team": "Man City",
                "Status": "100% Fit",
                "Form": "4.7",
                "GW24": "6pts",
                "Total": "102pts",
                "Price": "£6.1",
                "TSB": "12.3%"
                },
            "Sample Player Img": "https://resources.premierleague.com/premierleague/photos/players/110x140/p121160.png",
            "2021/22": ["1", "TOT (A) 1 - 0", "2", "90", "0", "0", "0", "1", "0", "0", "0", "0", "0", "1", "0", "10", "6.6", "0.0", "0.0", "0.7", "0", "683423", "£6.0"],
            "Previous Seasons": ["2020/21", "160", "3240", "0", "1", "19", "28", "0", "1", "0", "3", "0", "66", "3", "696", "586.0", "10.0", "0.0", "59.6", "£6.0", "£6.1"],
            "Fixtures": ["Sat 12 Feb 17:30", "25", "NOR (A)", "2"],
            "Total Pages": 19,
            "Total Players": 570
            }

    def test_plyr_attr(self):
        """Tests player's key attributes by comparing dictionaries.

        """
        exp_value = self.test_answers['Sample Player Stats']
        key_list = list(exp_value.keys())
        act_value = {k: v for k, v in self.sample_plyr[self.test_plyr_name].items() if k in key_list}
        self.assertDictEqual(exp_value, act_value)

    def test_plyr_attr_type(self):
        """Tests player's key attributes by comparing dictionaries of
        data types.

        """
        exp_value = [type(v) for _, v in self.test_answers['Sample Player Stats'].items()]
        key_list = list(self.test_answers['Sample Player Stats'].keys())
        act_value = [type(v) for k, v in self.sample_plyr[self.test_plyr_name].items() if k in key_list]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_img(self):
        """Tests player's image SRCs by comparing strings.

        """
        exp_value = self.test_answers['Sample Player Img']
        act_value = self.sample_plyr[self.test_plyr_name]['Image SRC']
        self.assertMultiLineEqual(exp_value, act_value)

    def test_plyr_img_type(self):
        """Tests player's image SRCs by comparing data types.

        """
        exp_value = type(self.test_answers['Sample Player Img'])
        act_value = type(self.sample_plyr[self.test_plyr_name]['Image SRC'])
        self.assertEqual(exp_value, act_value)

    def test_plyr_season_stats(self):
        """Tests player's season stats by comparing lists.

        """
        exp_value = self.test_answers['2021/22']
        act_value = self.sample_plyr[self.test_plyr_name]['2021/22'][1]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_season_stats_type(self):
        """Tests player's season stats by comparing lists of data types.

        """
        exp_value = [type(i) for i in self.test_answers['2021/22']]
        act_value = [type(i) for i in self.sample_plyr[self.test_plyr_name]['2021/22'][1]]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_prev_seasons(self):
        """Tests player's previous season stats by comparing lists.

        """
        exp_value = self.test_answers["Previous Seasons"]
        act_value = self.sample_plyr[self.test_plyr_name]["Previous Seasons"][1]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_prev_seasons_type(self):
        """Tests player's previous season stats by comparing lists of data types.

        """
        exp_value = [type(i) for i in self.test_answers["Previous Seasons"]]
        act_value = [type(i) for i in self.sample_plyr[self.test_plyr_name]["Previous Seasons"][1]]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_fixtures(self):
        """Tests player's fixtures by comparing lists.

        """
        exp_value = self.test_answers["Fixtures"]
        act_value = self.sample_plyr[self.test_plyr_name]["Fixtures"][1]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_fixtures_type(self):
        """Tests player's fixtures by comparing lists of data types.

        """
        exp_value = [type(i) for i in self.test_answers["Fixtures"]]
        act_value = [type(i) for i in self.sample_plyr[self.test_plyr_name]["Fixtures"][1]]
        self.assertListEqual(exp_value, act_value)

    def test_total_pages(self):
        """Tests total number of pages to be scraped by comparing integers.

        """
        exp_value = self.test_answers["Total Pages"]
        act_value = self.sample_total_pages
        self.assertEqual(exp_value, act_value)

    def test_total_plyrs(self):
        """Tests total number of players to be scraped by comparing integers.

        """
        exp_value = self.test_answers["Total Players"]
        act_value = self.sample_total_plyrs
        self.assertEqual(exp_value, act_value)


if __name__ == '__main__':
    unittest.main()
