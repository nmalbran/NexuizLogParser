# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime, timedelta
from optparse import OptionParser
from operator import itemgetter, attrgetter

from weapons import WEAPONS, WEAPON_MOD, STRENGTH, FLAG, SHIELD, TEXT
from ctf_strs import RETURNED, CAPTURE, RETURN, STEAL, DROPPED, PICKUP
from render import HTMLRender, PlainTextRender
from player_maps import AutoCompletePlayerMapAdmin

TEAM_COLOR = {'5': 'Red', '14': 'Blue'}
OPPOSITE_TEAM = {'5': 'Blue', '14': 'Red'}
START_DELAY_TIME = timedelta(seconds=15)
N_KILL_SPREE = 3
DEFAULT_COLUMN_WIDTH = 10
AVERAGE_TIME_TO_SELECT_A_MAP = timedelta(seconds=25)
HEADER_NAMES = {
            # Players Stats Table
                'name': 'name',
                'frags': 'frags',
                'tk': 'team kill',
                'deaths': 'deaths',
                'suicide': 'suicides',
                'accident': 'accidents',

                'fc_kills': 'fc kills',
                'sc_kills': 'strength kills',
                'ic_kills': 'shield kills',
                'tc_kills': 'texting kills',
                'kills_wf': 'kills w/ flag',
                'kills_ws': 'kills w/ strength',
                'kills_wi': 'kills w/ shield',

                'capture': 'caps',
                'steal': 'steals',
                'pickup': 'pickups',
                'return': 'return',
                'dropped': 'dropped',
                'cap_by_steal': 'caps by steal',
                'cap_by_pickup': 'caps by pickup',

                'score': 'score',
                'games_played': 'games played',

                'teams': 'team',
                'last_team': 'last team',

                'pweapon': 'preffered weapon',
                'max_killing_spree': 'longest killing spree',
                'n_killing_spree': '# of killing spree',
                'survival_index': 'survival index',
                'cap_index': 'capture success index (%)',
                'nemesis': 'nemesis',
                'rag_doll': 'rag doll',
                'last': 'last',
                'not_last': 'not last',

            # Players vs Players Table
                'killervskilled': 'killer',

            # Teams Stats Table
                'color': 'teams',
                'caps': 'caps',
                'score': 'score',
                'last_players': 'players',
                'captures': 'captures log',
                }


NUMERIC_STATS = ['score', 'frags', 'tk', 'n_killing_spree',
                 'fc_kills', 'sc_kills', 'ic_kills', 'tc_kills', 'kills_wf', 'kills_ws', 'kills_wi',
                 'deaths', 'suicide', 'accident',
                 CAPTURE, RETURN, STEAL, DROPPED, PICKUP, 'cap_by_steal', 'cap_by_pickup',
                 'last', 'not_last',
                ]
STATS_BY_PLAYER = ['kills_by_player', 'deaths_by_player']
STATS_BY_WEAPON = ['kills_by_weapon', ]


class NexuizLogParser:

    def __init__(self, known_player_nicks=dict(), teams=TEAM_COLOR, average_precision=2, min_players_per_game=3):
        self.reset()
        self.player_map = AutoCompletePlayerMapAdmin(known_player_nicks)
        self.teams = teams
        self.average_precision = average_precision
        self.min_players_per_game = min_players_per_game

        self.longest_name_length = {
            True: max([len(p) for p in known_player_nicks.keys()] or [DEFAULT_COLUMN_WIDTH]), # display_bot = True
            False: max([len(p) for p in known_player_nicks.keys() if not self.is_bot(p)] or [DEFAULT_COLUMN_WIDTH]), # display_bot = False
        }

        self.special_stats = {
            'pweapon': self.get_preffered_weapons,
            'survival_index': self.get_survival_index,
            'cap_index': self.get_cap_index,
            'nemesis': self.get_nemesis,
            'rag_doll': self.get_rag_doll,
            'not_last': self.get_not_last,
        }


    def reset(self):
        """
            Reset variables for a new log file.
        """
        self.in_game = False
        self.count = 0
        self.games = dict()
        self.info = []
        self.total = dict()
        self.average = dict()
        self.logfile_list = []
        self.logline = ''


    def is_bot(self, name):
        return self.player_map.is_bot(name)


    def get_results(self):
        """
            Return a dictionary with all the parsed information.
        """
        return self.games


    def get_total(self):
        """
            Return a dictionary with summary of all games in the log.
        """
        return self.total


    def get_average(self):
        """
            Return a dictionary with summary of all games in the log, in average per game.
        """
        return self.average


    def parse_logs(self, logfile_list):
        """
            Parse the log in `logfile`.
        """
        self.logfile_list = logfile_list
        players_name = dict()
        for logfile in logfile_list:
            line_number = 0
            capture_stack = dict()
            killing_spree = dict()

            for line in open(logfile):
                line_number += 1
                self.logline = "%s:%d :" % (logfile, line_number)

                if (len(line) > 25) and (line[24] == ":"):
                    timestamp = line[3:22]
                    gametime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                    command = line[25:].strip().split(":")

                    ########################
                    # COMAND PARSING START #
                    ########################
                    command_name = command[0]
                    if command_name == "gamestart":
                        underscore_pos = command[1].find('_')
                        game_type = command[1][:underscore_pos]
                        map_name = command[1][underscore_pos+1:]

                        players_name = dict()
                        capture_stack = dict()
                        killing_spree = dict()
                        self.in_game = True
                        self.games[self.count] = dict()
                        self.games[self.count]['map_data'] = {'map_name': map_name,
                                                              'start_time': gametime + START_DELAY_TIME,
                                                              'duration': '',
                                                              'game_type': game_type,
                                                              }

                        self.games[self.count]['teams'] = dict()
                        for (t_id, team) in self.teams.items():
                            self.games[self.count]['teams'][team] = {'id': t_id,
                                                                     'color': team,
                                                                     'caps': 0,
                                                                     'score': 0,
                                                                     'last_players': [],
                                                                     'captures_log': [],
                                                                    }

                    elif not self.in_game:
                        # commands outside a game are discarded
                        continue

                    elif command_name == "gameinfo":
                        subcommand = command[1]
                        if subcommand == "end":
                            pass
                        elif subcommand == "mutators":
                            mutators = command[2:]
                        else:
                            # just to discover other gameinfo log lines
                            self.info.append('%s gameinfo subcommand not recognized:' % self.logline)
                            self.info.append(command)

                    elif command_name == "scores":
                        pass

                    elif command_name == "join":
                        # This data is valid only during this game
                        # ip_from: IP address of the player
                        # nick: Nickname of the player
                        # xx: ??
                        player_id = command[1]
                        xx = command[2]
                        ip_from = command[3]
                        nick = ':'.join(command[4:])

                        player_name = self.player_map.get_name_from_nick(nick)

                        if 'players' not in self.games[self.count]:
                            self.games[self.count]['players'] = dict()

                        if player_id not in players_name:
                            players_name[player_id] = player_name

                        if player_name not in self.games[self.count]['players']:
                            self.games[self.count]['players'][player_name] = {
                                                                            'id': player_id,
                                                                            'ip': ip_from,
                                                                            'nick': nick,
                                                                            'name': player_name,

                                                                            'team': [],
                                                                            'last_team': '',

                                                                            'kills_by_player': dict(),
                                                                            'deaths_by_player': dict(),
                                                                            'kills_by_weapon': dict(),

                                                                            'killing_spree' : [],
                                                                            }
                            for stat in NUMERIC_STATS:
                                self.games[self.count]['players'][player_name][stat] = 0

                            capture_stack[player_name] = []
                            killing_spree[player_name] = 0

                    elif command_name == "team":
                        player_id , team_id = command[1:]
                        change_time = gametime + START_DELAY_TIME - self.games[self.count]['map_data']['start_time']
                        if team_id not in self.teams:
                            continue
                        self.games[self.count]['players'][players_name[player_id]]['team'].append("%s (%s)" % (self.teams[team_id], change_time))
                        self.games[self.count]['players'][players_name[player_id]]['last_team'] = self.teams[team_id]

                    elif command_name == "kill":
                        text, killer, killed = command[1:4]
                        other_data = command[4:] # items=killer weapon, victimitems=killed weapon
                        killer = players_name[killer]
                        killed = players_name[killed]
                        self.games[self.count]['players'][killed]['deaths'] += 1

                        killer_weapon, killer_mod = self._parse_weapon(other_data[1][6:], killer, killed)
                        if text in ['frag', 'tk']:
                            killed_weapon, killed_mod = self._parse_weapon(other_data[2][12:], killer, killed)

                        self.games[self.count]['players'][killer]['kills_by_weapon'][killer_weapon] = self.games[self.count]['players'][killer]['kills_by_weapon'].get(killer_weapon, 0) + 1

                        if killing_spree[killed] >= N_KILL_SPREE:
                            self.games[self.count]['players'][killed]['killing_spree'].append(killing_spree[killed])
                        killing_spree[killed] = 0

                        if text == "frag":         # kill other player
                            self.games[self.count]['players'][killer]['frags'] += 1
                            self.games[self.count]['players'][killer]['kills_by_player'][killed] = self.games[self.count]['players'][killer]['kills_by_player'].get(killed, 0) + 1
                            self.games[self.count]['players'][killed]['deaths_by_player'][killer] = self.games[self.count]['players'][killed]['deaths_by_player'].get(killer, 0) + 1

                            if FLAG in killed_mod:
                                self.games[self.count]['players'][killer]['fc_kills'] += 1
                            if SHIELD in killed_mod:
                                self.games[self.count]['players'][killer]['ic_kills'] += 1
                            if STRENGTH in killed_mod:
                                self.games[self.count]['players'][killer]['sc_kills'] += 1
                            if TEXT in killed_mod:
                                self.games[self.count]['players'][killer]['tc_kills'] += 1

                            if FLAG in killer_mod:
                                self.games[self.count]['players'][killer]['kills_wf'] += 1
                            if SHIELD in killer_mod:
                                self.games[self.count]['players'][killer]['kills_wi'] += 1
                            if STRENGTH in killer_mod:
                                self.games[self.count]['players'][killer]['kills_ws'] += 1

                            killing_spree[killer] += 1


                        elif text == "suicide":    # kill himself, by weapon
                            self.games[self.count]['players'][killer]['suicide'] += 1
                        elif text == "accident":   # kill himself, not by weapon
                            self.games[self.count]['players'][killer]['accident'] += 1
                        elif text == "tk":         # TeamMate kill
                            self.games[self.count]['players'][killer]['tk'] += 1
                        else:
                            self.info.append('%s kill text not recognized for command:' % self.logline)
                            self.info.append(command)

                    elif command_name == "ctf":
                        # Recognized subcommand:
                        #  returned --> lost flag automatically returned by timeout
                        #  capture  --> a capture for the team
                        #  return   --> flag returned by a player
                        #  steal    --> flag stealed by a player (flag in the base)
                        #  dropped  --> flag dropped by the player
                        #  pickup   --> flag taken by a player (flag in the field)
                        subcommand = command[1]
                        team_id = command[2]
                        if subcommand == RETURNED:
                            pass
                        elif subcommand in [CAPTURE, RETURN, STEAL, DROPPED, PICKUP]:
                            player_id = command[3]
                            player_name = players_name[player_id]

                            self.games[self.count]['players'][player_name][subcommand] += 1

                            if subcommand in [STEAL, DROPPED, PICKUP]:
                                capture_stack[player_name].append(subcommand)

                            if subcommand == CAPTURE:
                                capture_time = gametime - self.games[self.count]['map_data']['start_time']
                                self.games[self.count]['teams'][OPPOSITE_TEAM[team_id]]['captures_log'].append((capture_time, player_name))

                                type_of_capture = capture_stack[player_name][-1]
                                if type_of_capture == STEAL:
                                    self.games[self.count]['players'][player_name]['cap_by_steal'] += 1
                                elif type_of_capture == PICKUP:
                                    self.games[self.count]['players'][player_name]['cap_by_pickup'] += 1

                                capture_stack[player_name] = []

                        else:
                            self.info.append('%s ctf subcommand not recognized:' % self.logline)
                            self.info.append(command)

                    elif command_name == "part":
                        # This means: "player_id left the game"
                        player_id = command[1]
                        self.games[self.count]['players'][players_name[player_id]]['last_team'] = ''

                    elif command_name == "labels":
                        subcommand = command[1]
                        if subcommand == "player":
                            pass
                        elif subcommand == "teamscores":
                            pass
                        else:
                            self.info.append('%s labels subcommand not recognized:' % self.logline)
                            self.info.append(command)

                    elif command_name == "player":
                        # final stats for player
                        player_stats = command[2]
                        player_id = command[5]
                        team_id = command[4]
                        player_score = int(player_stats.split(',')[0])

                        self.games[self.count]['players'][players_name[player_id]]['score'] = player_score

                    elif command_name == "teamscores":
                        # final stats for teams
                        team_stats = command[2]
                        team_id = command[3]
                        if team_id in self.teams and team_stats:
                            team = self.teams[team_id]
                            caps, score = team_stats.split(',')
                            self.games[self.count]['teams'][team]['caps'] = int(caps)
                            self.games[self.count]['teams'][team]['score'] = int(score)

                    elif command_name == "end":
                        self.games[self.count]['map_data']['end_time'] = gametime
                        self.games[self.count]['map_data']['duration'] = gametime - self.games[self.count]['map_data']['start_time']

                        for pname, ks in killing_spree.items():
                            if ks >= N_KILL_SPREE:
                                self.games[self.count]['players'][pname]['killing_spree'].append(ks)

                    elif command_name == "gameover":
                        # This command marks the end of the game
                        self.count += 1
                        self.in_game = False
                        #break # for testing only... I want to play with 1 game's data

                    elif command_name == "vote":
                        # This command shows map voting
                        subcommand = command[1]
                        if subcommand == "keeptwo":
                            pass
                        elif subcommand == "finished":
                            pass

                    elif command_name == "recordset":
                        pass

                    elif command_name == "name":
                        # Player changes his/her name
                        pass

                    else:
                        # This is to show any unknown command
                        self.info.append('%s main command not recognized:' % self.logline)
                        self.info.append(command)

        self._clean_games()
        self._compute_extra_stats()
        self._compute_total()
        self._compute_average()
        self.info += self.player_map.get_info()


    def _clean_games(self):
        for i, game in self.games.items():
            if 'players' not in game:
                del self.games[i]
            else:
                players = [p for p in game['players'].keys() if not self.is_bot(p)]
                if len(players) < self.min_players_per_game:
                    del self.games[i]


    def _compute_extra_stats(self):
        for i, game in self.games.items():
            last_player_name = self._get_last_player_name(game['players'])
            self.games[i]['players'][last_player_name]['last'] = 1

            for pname, player in game['players'].items():
                for stat, stat_func in self.special_stats.items():
                    self.games[i]['players'][pname][stat] = stat_func(player)

                if player['last_team']:
                    self.games[i]['teams'][player['last_team']]['last_players'].append(pname)

                self.games[i]['players'][pname]['n_killing_spree'] = len(self.games[i]['players'][pname]['killing_spree'])
                self.games[i]['players'][pname]['max_killing_spree'] = max(self.games[i]['players'][pname]['killing_spree'] or [0])

            for tname, team in game['teams'].items():
                self.games[i]['teams'][tname]['last_players'] = ", ".join(self.games[i]['teams'][tname]['last_players'])

    def _compute_total(self):
        for game in self.games.values():
            if 'players' not in game:
                continue

            for player in game['players'].values():
                pname = player['name']
                if pname not in self.total:
                    self.total[pname] = {'name': pname, 'team': [], 'kills_by_weapon': dict(), 'games_played': 0}

                self.total[pname]['games_played'] += 1

                for stat in NUMERIC_STATS:
                    self.total[pname][stat] = self.total[pname].get(stat, 0) + player[stat]

                for stat in STATS_BY_PLAYER:
                    if stat not in self.total[pname]:
                        self.total[pname][stat] = dict()

                    for p2name, num in player[stat].items():
                        self.total[pname][stat][p2name] = self.total[pname][stat].get(p2name, 0) + num


                for weapon, num in player['kills_by_weapon'].items():
                    self.total[pname]['kills_by_weapon'][weapon] = self.total[pname]['kills_by_weapon'].get(weapon, 0) + num

                self.total[pname]['pweapon'] = self.get_preffered_weapons(self.total[pname], 3)
                self.total[pname]['survival_index'] = self.get_survival_index(self.total[pname])
                self.total[pname]['cap_index'] = self.get_cap_index(self.total[pname])
                self.total[pname]['nemesis'] = self.get_nemesis(self.total[pname])
                self.total[pname]['rag_doll'] = self.get_rag_doll(self.total[pname])

                self.total[pname]['max_killing_spree'] = max(self.total[pname].get('max_killing_spree', 0), player['max_killing_spree'])
                self.total[pname]['max_killing_spree_sum'] = self.total[pname].get('max_killing_spree_sum', 0) + player['max_killing_spree']

    def _compute_average(self):
        stats_by_something = STATS_BY_PLAYER + STATS_BY_WEAPON

        def av(val, tot):
            return round(val * 1.0 / tot, self.average_precision)

        for pname, player in self.total.items():
            num = player['games_played']
            self.average[pname] = {'name': pname, 'team':[], 'games_played': num}

            for stat in NUMERIC_STATS:
                self.average[pname][stat] = av(player[stat], num)

            for stat in stats_by_something:
                self.average[pname][stat] = dict()
                for key, val in player[stat].items():
                    self.average[pname][stat][key] = av(val, num)

            for stat, stat_func in self.special_stats.items():
                self.average[pname][stat] = stat_func(self.average[pname])

            self.average[pname]['max_killing_spree'] = av(player['max_killing_spree_sum'], num)


    def _parse_weapon(self, weapon, killer='', killed=''):
        weapon_id = ''
        weapon_mod = ''
        for c in weapon:
            try:
                int(c)
                weapon_id += c
            except ValueError as e:
                weapon_mod += c

        weapon_id = int(weapon_id)
        if weapon_id not in WEAPONS:
            self.info.append("%s Unknown weapon id: %s, map: %s (%s -> %s)" % (self.logline, weapon, self.games[self.count]['map_data']['map_name'], killer, killed))
            weapon_str = 'new weapon'
        else:
            weapon_str = WEAPONS[weapon_id]

        clean_mod = ''
        for m in weapon_mod:
            if m not in WEAPON_MOD:
                self.info.append("%s Unknown weapon mod: %s, map: %s (%s -> %s)" % (self.logline, weapon, self.games[self.count]['map_data']['map_name'], killer, killed))
            else:
                clean_mod += m

        return (weapon_str, clean_mod)


    def get_preffered_weapons(self, player, num=2):
        weapons = sorted(player['kills_by_weapon'].items(), key=lambda x: x[1], reverse=True)[:num]
        return ", ".join(["%s(%d)" % w for w in weapons])

    def get_survival_index(self, player):
        return round((player['frags'] * 1.0) / (player['deaths'] or 1), 2)

    def get_cap_index(self, player):
        return round((player['cap_by_steal'] * 100.0) / (player['steal'] or 1), 1)

    def get_nemesis(self, player):
        ordered_nemesis = sorted(player['deaths_by_player'].items(), key=lambda x:x[1], reverse=True)
        try:
            return "%s(%d)" % ordered_nemesis[0]
        except IndexError as e:
            return ''

    def get_rag_doll(self, player):
        ordered_rag_doll = sorted(player['kills_by_player'].items(), key=lambda x:x[1], reverse=True)
        try:
            return "%s(%d)" % ordered_rag_doll[0]
        except IndexError as e:
            return ''

    def get_not_last(self, player, all_games=False):
        if all_games:
            return len(self.games) - player['last']
        else:
            return 1 - player['last']

    def get_total_time_played(self):
        durations = [game['map_data']['duration'] for i, game in self.games.items()]
        return sum(durations, AVERAGE_TIME_TO_SELECT_A_MAP * len(self.games))

    def display_parser_info(self):
        """
            Display info messages generated by the parser.
        """
        if not self.info:
            return
        print "\nPARSER INFO:"
        for e in self.info:
            print e

    def _sorted_games(self):
        return sorted(self.games.items(), key=lambda x: x[0])

    def _game_is_ctf(self, game):
        return 'teams' in game and game['map_data']['game_type'] == 'ctf'

    def _filter_players_from_bots(self, players, display_bot=False):
        def valid(player):
            if self.is_bot(player['name']) and not display_bot:
                return False
            return True

        return [p for p in players.values() if valid(p)]


    def _filter_players_and_sort_by_stat(self, players, display_bot=False, stat='name'):
        filtered_players = self._filter_players_from_bots(players, display_bot)
        return sorted(filtered_players, key=itemgetter(stat))


    def _get_last_player_name(self, players):
        filtered_players = self._filter_players_from_bots(players, display_bot=False)
        filtered_players.sort(key=itemgetter('deaths'), reverse=True)
        filtered_players.sort(key=itemgetter('score'))
        return filtered_players[0]['name']


    def _output_players_scores(self, render, players, table='game'):
        header = {'total':render.total_table_header, 'game': render.game_table_header}
        row = {'total':render.total_table_row, 'game': render.game_table_row}

        output = header[table]()
        for player in players:
            player['teams'] = ', '.join(player['team'])
            output += row[table](player)
        return output

    def _output_kills_by_player(self, render, players):
        output = render.kills_by_player_table_header([p['name'] for p in players])
        for killer in players:
            line = [killer['name']]
            for killed in players:
                line.append(killer['kills_by_player'].get(killed['name'], 0))
            output += render.kills_by_player_table_row(line)
        return output

    def _output_teams_scores(self, render, teams):
        output = render.teams_table_header()
        for team in teams.values():
            team['captures'] = ', '.join(["%s(%s)" % cl for cl in team['captures_log']])
            output += render.teams_table_row(team)
        return output


    def output(self, output='html', display_bot=False, display_parcial=True, display_total=True):
        """
            Outputs the results of the parsed log file.
            @display_bot: if set, display bot results.
            @display_parcial: if set, show info of all games
            @display_total: if set, show summary info
        """
        options = {'html': HTMLRender, 'txt': PlainTextRender}
        if output not in options:
            output = 'html'
        render = options[output](header_names=HEADER_NAMES, lnl=self.longest_name_length[display_bot])

        content = {'title': 'Nexuiz Statistics',
                   'logfiles': ', '.join([os.path.basename(log) for log in self.logfile_list]),
                   'total_table': '',
                   'games_tables':'',
                   }

        if display_parcial:
            for i, game in self._sorted_games():
                players = self._filter_players_and_sort_by_stat(game['players'], display_bot)
                game_data = game['map_data']
                game_data['player_stats'] = self._output_players_scores(render, players, table='game')
                game_data['player_vs_player'] = self._output_kills_by_player(render, players)

                if self._game_is_ctf(game):
                    game_data['teams_stats'] = self._output_teams_scores(render, game['teams'])
                else:
                    game_data['teams_stats'] = ''

                content['games_tables'] += render.game(game_data)

        if display_total:
            total_players = self._filter_players_and_sort_by_stat(self.total, display_bot)
            average_players = self._filter_players_and_sort_by_stat(self.average, display_bot)
            total_data = {
                'game_number': len(self.games),
                'time_played': self.get_total_time_played(),
                'player_stats': self._output_players_scores(render, total_players, table='total'),
                'average_stats': self._output_players_scores(render, average_players, table='total'),
                'player_vs_player': self._output_kills_by_player(render, total_players),
            }
            content['total_table'] = render.total(total_data)

        return render.base(content)



def get_known_player_nicks(player_package=None):
    module = 'players'
    var = 'PLAYERS'

    if player_package:
        dot = player_package.rfind('.')
        if dot > 0:
            module = player_package[:dot]
            var = player_package[dot+1:] or var
        else:
            module = player_package

    from importlib import import_module
    try:
        module = import_module(module)
        known_player_nicks = module.__getattribute__(var)

    except (ImportError, AttributeError) as e:
        known_player_nicks = dict()

    return known_player_nicks


def main():
    parser = OptionParser(usage='usage: %prog [options] logfile1 [logfile2 logfile3 ...]')
    parser.add_option("-t", '--type', action="store", help="Type of the output result (html, txt)", default='html', choices=['html', 'txt'])
    parser.add_option("-o", '--output', action="store", help="File to output result.", default='')
    parser.add_option("-n", '--minplayers', action="store", type="int", help="Minimun number of players to consider a game.", default=3)
    parser.add_option('-b', "--bot", action="store_true", help="Display Bot's results", default=False)
    parser.add_option('-p', "--players", action="store", help="Package.variable containing the players/nicks map. Default: players.PLAYERS", default=None)

    parser.add_option("--nototal", action="store_false", dest='total', help="Don't display totals", default=True)
    parser.add_option("--noparcial", action="store_false", dest='parcial', help="Don't display individual game results", default=True)
    parser.add_option("-q", "--quiet", action="store_false", dest='info', help="Don't display parser error", default=True)

    (options, args) = parser.parse_args()

    nlp = NexuizLogParser(get_known_player_nicks(options.players), min_players_per_game=options.minplayers)
    nlp.parse_logs(args)

    if not options.output:
        filename = '%s-stats.%s' % (time.strftime("%Y%m%d"), options.type)
    else:
        filename = options.output
    print "Output to: %s\n" % filename

    f = open(filename, 'w')
    output = nlp.output(display_bot=options.bot, output=options.type, display_total=options.total, display_parcial=options.parcial)
    f.write(output)
    f.close()

    if options.info:
        nlp.display_parser_info()


if __name__ == '__main__':
    main()
