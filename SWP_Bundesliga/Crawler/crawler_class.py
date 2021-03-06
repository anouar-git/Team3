import urllib.request
from urllib.error import HTTPError
import pandas as pd


class Crawler:

    def __init__(self, league):
        """Initializing of Crawler for league from OpenLigaDB

         :param league: Describes which league gets crawled

         :type league: str"""

        self.url = "https://www.openligadb.de/api"
        self.league = league

    def get_data(self, year, data, s_day, e_day):
        """Loads and stores a portion the wanted data into a dictionary and returns the dictionary.
        Always gets entire year which gets filter by s_day and e_day

         :param year: The year which the current data origins
         :param data: A Dictionary which holds already collected data and where the new data gets stored into
         :param s_day: Starting play day for the requested data needed
         :param e_day: Ending play day for the requested data needed

         :type year: int
         :type data: Dictionary
         :type s_day: int
         :type e_day: int

         :return: a dictionary which contains the already collected data and the new data from the year \n"""

        url_header = urllib.request.Request(
            url=self.url + "/getmatchdata/" + self.league + "/" + str(year),
            data=None,
            headers={'Content-Type': 'application/json'}
        )
        page = urllib.request.urlopen(url_header)
        matches = pd.read_json(page)
        game_num = len(matches)
        try:
            for m in range(0, game_num):
                if matches['Group'][m]['GroupOrderID'] in range(s_day, e_day + 1):
                    data['date'].append(matches['MatchDateTime'][m])
                    data['team1'].append(matches['Team1'][m]['TeamName'])
                    data['team2'].append(matches['Team2'][m]['TeamName'])
                    data['is_finished'].append(matches['MatchIsFinished'][m])
                    data['play_day'].append(matches['Group'][m]['GroupOrderID'])
                    if matches['MatchIsFinished'][m]:
                        if matches['MatchResults'][m][0]['ResultName'] == "Endergebnis":
                            data['goal1'].append(matches['MatchResults'][m][0]['PointsTeam1'])
                            data['goal2'].append(matches['MatchResults'][m][0]['PointsTeam2'])
                        else:
                            data['goal1'].append(matches['MatchResults'][m][1]['PointsTeam1'])
                            data['goal2'].append(matches['MatchResults'][m][1]['PointsTeam2'])
                    else:
                        data['goal1'].append("-")
                        data['goal2'].append("-")
        except KeyError:
            print('Can not find "Group" -> the file is empty ')
        return data

    def get_match_data_interval(self, s_year, s_day, e_year, e_day):
        """Searches the match data which are requested. All match data gets stored into a dict.
        After all the required data is stored into the dictionary, the dictionary
        then gets stored as matches.csv

        :param s_year: Specifies the starting year for the data
        :param s_day: Specifies the starting day in s_year
        :param e_year: Specifies the ending year for the data
        :param e_day: Specifies the ending day in e_year

        :type s_year: int
        :type s_day: int
        :type e_year: int
        :type e_day: int """

        group_num = self.get_group_size(s_year)

        data = {'date': [],
                'team1': [],
                'team2': [],
                'is_finished': [],
                'play_day': [],
                'goal1': [],
                'goal2': []}
        if s_year == e_year:
            self.get_data(s_year, data, s_day, e_day)
        else:
            for y in range(s_year, e_year + 1):
                if y == s_year:
                    self.get_data(y, data, s_day, group_num)
                else:
                    if y == e_year:
                        self.get_data(y, data, 1, e_day)
                    else:
                        self.get_data(y, data, 1, group_num)
        df = pd.DataFrame(data, columns=['date', 'team1', 'team2', 'goal1', 'goal2', 'is_finished', 'play_day'])
        df.to_csv('matches.csv', index=False)

    def get_teams(self, s_year, e_year):
        """ Gets and stores all Teams which played between s_year and e_year in bl1
        into the file teams.csv

         :param s_year: Specifies starting year for the Team data
         :param e_year: Specifies ending year for the Team data

         :type s_year: int
         :type e_year: int """

        team_dict = {'name': [],
                     'year': []}
        for y in range(s_year, e_year + 1):
            url_header = urllib.request.Request(
                url=self.url + "/getavailableteams/" + self.league + "/" + str(y),
                data=None,
                headers={'Content-Type': 'application/json'}
            )
            page = urllib.request.urlopen(url_header)
            teams = pd.read_json(page)
            team_num = len(teams)
            for i in range(0, team_num):
                team_dict['name'].append(teams['TeamName'][i])
                team_dict['year'].append(y)
        df = pd.DataFrame(team_dict, columns=['name', 'year'])
        df.to_csv('teams.csv', index=False)

    def get_group_size(self, year):
        """ Gets and returns the number of play-days of the league of crawler

            :param year: Specifies year for the data. Not important which year as long as it is a year that is complete

            :type year: int

            :return: a int which is the number of days"""
        try:
            url_header = urllib.request.Request(
                url=self.url + "/getavailablegroups/" + self.league + "/" + str(year),
                data=None,
                headers={'Content-Type': 'application/json'}
            )
            page = urllib.request.urlopen(url_header)
            groups = pd.read_json(page)
            group_num = len(groups)
            return group_num
        except urllib.error.HTTPError:
            return 0
