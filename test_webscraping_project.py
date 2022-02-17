import unittest
from fpl_webscraper import FPLWebScraper


class FPLWebScraperTestCase(unittest.TestCase):
    """This Class carries out units tests on the WebScraper script.

    The WebScraper script is tested by comparing scraped data to that
    retrieved manually and stored in a local dictionary.
    Scraped data types are also compared.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the answers for the test cases.

        This function supplies a manually inputted dictionary of scraped
        data for which newly scraped data can be compared to. Only one
        instance of a player is tested.
        It also sets up an instance of the WebScraper class in sample
        mode, meaning only player's data is scraped.

        Manual test cases last updated on 14/02/2022.
        """
        cls.sample = FPLWebScraper('https://fantasy.premierleague.com/', sample_mode=True)
        cls.sample_plyr = cls.sample.plyr_dict
        cls.sample_total_plyrs = cls.sample.total_plyrs
        cls.sample_total_pages = cls.sample.total_pages
        cls.test_answers = {
            "Sample Player Stats": {
                "Name": "Ederson Santana de Moraes",
                "Position": "Goalkeeper",
                "Team": "Man City",
                "Status": "100% Fit",
                "Form": "5.0",
                "GW25": "7pts",
                "Total": "109pts",
                "Price": "£6.1",
                "TSB": "12.2%"
                },
            "Sample Player Img": "https://resources.premierleague.com/premierleague/photos/players/110x140/p121160.png",
            "2021/22": ["1", "TOT (A) 1 - 0", "2", "90", "0", "0", "0", "1", "0", "0", "0", "0", "0", "1", "0", "10", "6.6", "0.0", "0.0", "0.7", "0", "683423", "£6.0"],
            "Previous Seasons": ["2020/21", "160", "3240", "0", "1", "19", "28", "0", "1", "0", "3", "0", "66", "3", "696", "586.0", "10.0", "0.0", "59.6", "£6.0", "£6.1"],
            "Fixtures": ["Sat 19 Feb 17:30", "26", "TOT (H)", "3"],
            "Total Pages": 20,
            "Total Players": 573
            }

    def test_plyr_attr(self):
        """Tests player's key attributes by comparing dictionaries."""
        exp_value = self.test_answers['Sample Player Stats']
        key_list = list(exp_value.keys())
        act_value = {k: v for k, v in self.sample_plyr.items() if k in key_list}
        print(exp_value)
        print(act_value)
        self.assertDictEqual(exp_value, act_value)

    def test_plyr_attr_type(self):
        """Tests player's key attributes by comparing dictionaries of data types."""
        exp_value = [type(v) for _, v in self.test_answers['Sample Player Stats'].items()]
        key_list = list(self.test_answers['Sample Player Stats'].keys())
        act_value = [type(v) for k, v in self.sample_plyr.items() if k in key_list]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_img(self):
        """Tests player's image SRCs by comparing strings."""
        exp_value = self.test_answers['Sample Player Img']
        act_value = self.sample_plyr['Image SRC']
        self.assertMultiLineEqual(exp_value, act_value)

    def test_plyr_img_type(self):
        """Tests player's image SRCs by comparing data types."""
        exp_value = type(self.test_answers['Sample Player Img'])
        act_value = type(self.sample_plyr['Image SRC'])
        self.assertEqual(exp_value, act_value)

    def test_plyr_season_stats(self):
        """Tests player's season stats by comparing lists."""
        exp_value = self.test_answers['2021/22']
        act_value = self.sample_plyr['2021/22'][1]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_season_stats_type(self):
        """Tests player's season stats by comparing lists of data types."""
        exp_value = [type(i) for i in self.test_answers['2021/22']]
        act_value = [type(i) for i in self.sample_plyr['2021/22'][1]]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_prev_seasons(self):
        """Tests player's previous season stats by comparing lists."""
        exp_value = self.test_answers["Previous Seasons"]
        act_value = self.sample_plyr["Previous Seasons"][1]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_prev_seasons_type(self):
        """Tests player's previous season stats by comparing lists of data types."""
        exp_value = [type(i) for i in self.test_answers["Previous Seasons"]]
        act_value = [type(i) for i in self.sample_plyr["Previous Seasons"][1]]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_fixtures(self):
        """Tests player's fixtures by comparing lists."""
        exp_value = self.test_answers["Fixtures"]
        act_value = self.sample_plyr["Fixtures"][1]
        self.assertListEqual(exp_value, act_value)

    def test_plyr_fixtures_type(self):
        """Tests player's fixtures by comparing lists of data types."""
        exp_value = [type(i) for i in self.test_answers["Fixtures"]]
        act_value = [type(i) for i in self.sample_plyr["Fixtures"][1]]
        self.assertListEqual(exp_value, act_value)

    def test_total_pages(self):
        """Tests total number of pages to be scraped by comparing integers."""
        exp_value = self.test_answers["Total Pages"]
        act_value = self.sample_total_pages
        self.assertEqual(exp_value, act_value)

    def test_total_plyrs(self):
        """Tests total number of players to be scraped by comparing integers."""
        exp_value = self.test_answers["Total Players"]
        act_value = self.sample_total_plyrs
        self.assertEqual(exp_value, act_value)


if __name__ == '__main__':
    unittest.main()
