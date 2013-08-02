# -*- coding: utf-8 -*-

import os
from datetime import datetime
from optparse import OptionParser
from weapons import WEAPONS, WEAPON_MOD, STRENGTH, FLAG, SHIELD
from render import HTMLRender, PlainTextRender

TEAM_COLOR = {'5': 'Red', '14': 'Blue'}
HEADER_NAMES = {'name': 'name',
                'frags': 'frags',
                'suicide': 'suicides',
                'accident': 'accidents',
                'tk': 'team kill',
                'fckills': 'fc kills',
                'deaths': 'deaths',
                'capture': 'caps',
                'steal': 'steals',
                'pickup': 'pickups',
                'teams': 'team',

                'killervskilled': 'killer',

                'color': 'teams',
                'caps': 'caps',
                'score': 'score',

                'pweapon': 'preffered weapon',
                'survival_index': 'survival index',
                'cap_index': 'capture success index',
                'nemesis': 'nemesis',
                }


class NexuizLogParser:

    def __init__(self, known_player_nicks, teams=TEAM_COLOR):
        self.reset()
        self.known_player_nicks = known_player_nicks
        self.teams = teams

        self.longest_name_length = {
            True: max([len(p) for p in known_player_nicks.keys()]), # display_bot = True
            False: max([len(p) for p in known_player_nicks.keys() if not self.is_bot(p)]), # display_bot = False
        }

        self.special_stats = {
            'pweapon': self.get_preffered_weapons,
            'survival_index': self.get_survival_index,
            'cap_index': self.get_cap_index,
            'nemesis': self.get_nemesis,
        }


    def reset(self):
        """
            Reset variables for a new log file.
        """
        self.in_game = False
        self.count = 0
        self.line_number = 0
        self.games = dict()
        self.player_nicks = set()
        self.info = []
        self.total = dict()
        self.logfile_list = []


    def is_bot(self, name):
        return name.startswith('[BOT]')


    def _get_name_from_nick(self, nick):
        for name in self.known_player_nicks:
            if nick in self.known_player_nicks[name]:
                return name
        if nick not in self.player_nicks:
            self.player_nicks.add(nick)
            self.info.append("Nick not recognized (line: %d): '%s': ['%s']" % (self.line_number, nick, repr(nick)))
        return 'UNKNOWN'


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


    def parse_log(self, logfile_list):
        """
            Parse the log in `logfile`.
        """
        self.logfile_list = logfile_list
        players_name = dict()
        for logfile in logfile_list:
            self.line_number = 0
            for line in open(logfile):
                self.line_number += 1

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
                        self.in_game = True
                        self.games[self.count] = dict()
                        self.games[self.count]['map_data'] = {'map_name': map_name,
                                                              'start_time': gametime,
                                                              'duration': '',
                                                              'game_type': game_type,
                                                              }

                        self.games[self.count]['teams'] = dict()
                        for (t_id, team) in self.teams.items():
                            self.games[self.count]['teams'][t_id] = {'id': t_id, 'color': team, 'caps': 0, 'score': 0}

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
                            self.info.append('gameinfo subcommand not recognized (line %d):' % line_number)
                            self.info.append(command)

                    elif command_name == "scores":
                        pass

                    elif command_name == "join":
                        # This data is valid only during this game
                        # ip_from: IP address of the player
                        # nick: Nickname of the player
                        # xx: ??
                        player_id, xx, ip_from, nick = command[1:]
                        #if nick[0:5] != "[BOT]":
                        player_name = self._get_name_from_nick(nick)

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

                                                                            'frags': 0,
                                                                            'suicide': 0,
                                                                            'accident': 0,
                                                                            'tk': 0,
                                                                            'deaths': 0,
                                                                            'fckills': 0,

                                                                            'kills_by_player': dict(),
                                                                            'deaths_by_player': dict(),
                                                                            'kills_by_weapon': dict(),

                                                                            'capture': 0,
                                                                            'return': 0,
                                                                            'steal': 0,
                                                                            'dropped': 0,
                                                                            'pickup': 0,}

                    elif command_name == "team":
                        player_id , team_id = command[1:]
                        change_time = gametime - self.games[self.count]['map_data']['start_time']
                        if team_id not in self.teams:
                            continue
                        self.games[self.count]['players'][players_name[player_id]]['team'].append("%s (%s)" % (self.teams[team_id], change_time))

                    elif command_name == "kill":
                        text, killer, killed = command[1:4]
                        other_data = command[4:] # items=killer weapon, victimitems=killed weapon
                        killer = players_name[killer]
                        killed = players_name[killed]
                        self.games[self.count]['players'][killed]['deaths'] += 1

                        killer_weapon, killer_mod = self._parse_weapon(other_data[1][6:])
                        if text in ['frag', 'tk']:
                            killed_weapon, killed_mod = self._parse_weapon(other_data[2][12:])

                        self.games[self.count]['players'][killer]['kills_by_weapon'][killer_weapon] = self.games[self.count]['players'][killer]['kills_by_weapon'].get(killer_weapon, 0) + 1

                        if text == "frag":         # kill other player
                            self.games[self.count]['players'][killer]['frags'] += 1
                            self.games[self.count]['players'][killer]['kills_by_player'][killed] = self.games[self.count]['players'][killer]['kills_by_player'].get(killed, 0) + 1
                            self.games[self.count]['players'][killed]['deaths_by_player'][killer] = self.games[self.count]['players'][killed]['deaths_by_player'].get(killer, 0) + 1

                            if FLAG in killed_mod:
                                self.games[self.count]['players'][killer]['fckills'] += 1


                        elif text == "suicide":    # kill himself, by weapon
                            self.games[self.count]['players'][killer]['suicide'] += 1
                        elif text == "accident":   # kill himself, not by weapon
                            self.games[self.count]['players'][killer]['accident'] += 1
                        elif text == "tk":         # TeamMate kill
                            self.games[self.count]['players'][killer]['tk'] += 1
                        else:
                            self.info.append('kill text not recognized for command (line %d):' % self.line_number)
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
                        if subcommand == "returned":
                            pass
                        elif (subcommand == "capture" or
                             subcommand == "return"  or
                             subcommand == "steal"   or
                             subcommand == "dropped" or
                             subcommand == "pickup"):
                            player_id = command[3]
                            self.games[self.count]['players'][players_name[player_id]][subcommand] += 1
                        else:
                            self.info.append('ctf subcommand not recognized (line %d):' % self.line_number)
                            self.info.append(command)

                    elif command_name == "part":
                        # This means: "player_id left the game"
                        player_id = command[1]

                    elif command_name == "labels":
                        subcommand = command[1]
                        if subcommand == "player":
                            pass
                        elif subcommand == "teamscores":
                            pass
                        else:
                            self.info.append('labels subcommand not recognized (line %d):' % self.line_number)
                            self.info.append(command)

                    elif command_name == "player":
                        # final stats for player
                        player_stats = command[2:]

                    elif command_name == "teamscores":
                        # final stats for teams
                        team_stats = command[2]
                        team_id = command[3]
                        if team_id in self.teams and team_stats:
                            caps, score = team_stats.split(',')
                            self.games[self.count]['teams'][team_id]['caps'] = int(caps)
                            self.games[self.count]['teams'][team_id]['score'] = int(score)

                    elif command_name == "end":
                        self.games[self.count]['map_data']['end_time'] = gametime
                        self.games[self.count]['map_data']['duration'] = str(gametime - self.games[self.count]['map_data']['start_time'])

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
                        self.info.append('main command not recognized (line %d):' % line_number)
                        self.info.append(command)

        self._clean_games()
        self._compute_extra_stats()
        self._compute_total()


    def _clean_games(self):
        for i, game in self.games.items():
            if 'players' not in game:
                del self.games[i]


    def _compute_extra_stats(self):
        for i, game in self.games.items():
            for pname, player in game['players'].items():
                for stat, stat_func in self.special_stats.items():
                    self.games[i]['players'][pname][stat] = stat_func(player)


    def _compute_total(self):
        stats = ['frags', 'suicide', 'accident', 'tk', 'fckills', 'deaths', 'capture', 'return', 'steal', 'dropped', 'pickup']
        stats_by_player = ['kills_by_player', 'deaths_by_player']
        for game in self.games.values():
            if 'players' not in game:
                continue

            for player in game['players'].values():
                pname = player['name']
                if pname not in self.total:
                    self.total[pname] = {'name': pname, 'team': [], 'kills_by_weapon': dict()}

                for stat in stats:
                    self.total[pname][stat] = self.total[pname].get(stat, 0) + player[stat]

                for stat in stats_by_player:
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



    def _parse_weapon(self, weapon):
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
            self.info.append("Unknown weapon id: Line Number: %d, Weapon: %s" % (self.line_number, weapon))
            weapon_str = 'new weapon'
        else:
            weapon_str = WEAPONS[weapon_id]

        clean_mod = ''
        for m in weapon_mod:
            if m not in WEAPON_MOD:
                self.info.append("Unknown weapon mod: Line Number: %d, Weapon: %s" % (self.line_number, weapon))
            else:
                clean_mod += m

        return (weapon_str, clean_mod)


    def get_preffered_weapons(self, player, num=2):
        weapons = sorted(player['kills_by_weapon'].items(), key=lambda x: x[1], reverse=True)[:num]
        return ", ".join(["%s(%d)" % w for w in weapons])

    def get_survival_index(self, player):
        return round((player['frags'] * 1.0) / (player['deaths'] or 1), 2)

    def get_cap_index(self, player):
        return str(round((player['capture'] * 100.0) / ((player['steal'] + player['pickup']) or 1), 1))+ " %"

    def get_nemesis(self, player):
        ordered_nemesis = sorted(player['deaths_by_player'].items(), key=lambda x:x[1], reverse=True)
        try:
            return ordered_nemesis[0][0]
        except IndexError as e:
            return ''

    def display_parser_info(self):
        """
            Display info messages generated by the parser.
        """
        if not self.info:
            return
        print "\nPARSER INFO:"
        for e in self.info:
            print e


    def _filter_and_sort(self, players, display_bot=False):
        def valid(player):
            if self.is_bot(player['name']) and not display_bot:
                return False
            return True

        return sorted([p for p in players if valid(p)], key=lambda x: x['name'])

    def _output_players_scores(self, render, players):
        output = render.game_table_header()
        for player in players:
            player['teams'] = ', '.join(player['team'])
            output += render.game_table_row(player)
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
        game_number = 0

        if display_parcial:
            for i, game in sorted(self.games.items(), key=lambda x: x[0]):
                players = self._filter_and_sort(game['players'].values(), display_bot)
                if len(players) < 1:
                    continue
                game_data = game['map_data']
                game_data['player_stats'] = self._output_players_scores(render, players)
                game_data['player_vs_player'] = self._output_kills_by_player(render, players)

                if 'teams' in game and game['map_data']['game_type'] == 'ctf':
                    game_data['teams_stats'] = self._output_teams_scores(render, game['teams'])
                else:
                    game_data['teams_stats'] = ''

                content['games_tables'] += render.game(game_data)
                game_number += 1
        else:
            game_number = len(self.games)

        if display_total:
            total_players = self._filter_and_sort(self.total.values(), display_bot)
            total_data = {
                'game_number': game_number,
                'player_stats': self._output_players_scores(render, total_players),
                'player_vs_player': self._output_kills_by_player(render, total_players),
            }
            content['total_table'] = render.total(total_data)

        return render.base(content)


if __name__ == '__main__':
    from players import KNOWN_PLAYER_NICKS

    parser = OptionParser(usage='usage: %prog [options] logfile1 [logfile2 logfile3 ...]')
    parser.add_option("-t", '--type', action="store", help="Type of the output result (html, txt)", default='html', choices=['html', 'txt'])
    parser.add_option("-o", '--output', action="store", help="File to output result.", default='')
    parser.add_option('-b', "--bot", action="store_true", help="Display Bot's results", default=False)
    parser.add_option("--nototal", action="store_false", dest='total', help="Don't display totals", default=True)
    parser.add_option("--noparcial", action="store_false", dest='parcial', help="Don't display individual game results", default=True)
    parser.add_option("-q", "--quiet", action="store_false", dest='info', help="Don't display parser error", default=True)

    (options, args) = parser.parse_args()

    nlp = NexuizLogParser(KNOWN_PLAYER_NICKS)
    nlp.parse_log(args)

    if not options.output:
        filename = 'parsedlog.%s' % options.type
    else:
        filename = options.output
    f = open(filename, 'w')
    output = nlp.output(display_bot=options.bot, output=options.type, display_total=options.total, display_parcial=options.parcial)
    f.write(output)
    f.close()

    if options.info:
        nlp.display_parser_info()
