import os
from datetime import datetime
import json


def write_report(dir_path: str) -> None:
    """Writes a txt file in the raw data folder containing a timestamp and data
    verification checks.

    This report is saved in the raw_data folder as well as being uploaded to the
    s3 bucket.

    Attributes:
        txt_path: String path where the report is to be saved.
        report (str): Verification report.
        json_count (int): Number of players with populated json files.
        img_count (int): Number of players with populated image files.
        scraped_data (datetime): Latest date at which player was scraped.
        report_txt: Concatenation of report string.

    Returns:
        None

    """
    txt_path: str = os.path.join(dir_path, 'report.txt')
    report, json_count, img_count, scraped_date = verification_report(dir_path)
    report_txt: str = f"Scraper ran on {scraped_date}.\n{json_count} json files and {img_count} image files scraped.\n\n{report}"
    print(report_txt)
    with open(txt_path, 'w') as f:
        f.write(report_txt)
    # self.s3_client.upload_file(txt_path, 'fplplayerdatabucket', 'raw_data/report.txt')


def verification_report(dir_path: str) -> list:
    """Produces verification report on scraped data.

    Verification report which calculates number of populated json files, image
    files and last scraped date data. Also returns a list of players that will
    need to be verified by the user due to confirm that the ID matches the player
    that had been scraped.

    Args:
        dir_path: Directory to be searched.

    Attributes:
        report: Verification report.
        json_count: Number of populated json files in directory.
        img_count:N umber of image files in directory.
        scraped_data (datetime): Latest date at which player was scraped.

    Returns:
        report
        json_count
        img_count
        scraped_date

    """
    report: str = 'Please verify the following players:\n\n'
    json_count: int = 0
    img_count: int = 0
    scraped_date: datetime = datetime.strptime('2000-01-01', '%Y-%m-%d')
    for root, _, files in os.walk(dir_path):
        for filename in files:
            if filename[-3:] == 'png':
                img_count += 1
            if filename[-4:] == 'json':
                with open(os.path.join(root, filename)) as f:
                    plyr_dict = json.load(f)
                file_scraped: datetime = datetime.strptime(plyr_dict['Last Scraped'][:10], '%Y-%m-%d')
                if file_scraped > scraped_date:
                    scraped_date = file_scraped
                if len(plyr_dict) > 18:
                    json_count += 1
                if plyr_dict['ID'][7:] not in plyr_dict['Name']:
                    report += f"{plyr_dict['ID']} = {plyr_dict['Name']}, {plyr_dict['Team']}, {plyr_dict['Position']}\n"
    scraped_date = scraped_date.date()
    return report, json_count, img_count, scraped_date


if __name__ == "__main__":
    write_report(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'raw_data'))
