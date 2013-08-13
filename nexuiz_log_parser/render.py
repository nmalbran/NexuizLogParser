# -*- coding: utf-8 -*-
import os

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html_templates')
SEP = "=" * 80 + "\n"
STR_GAME_ROW = ["%(name)", "s  %(score)5s  %(frags)5s  %(fc_kills)9s  %(tk)10s | %(deaths)6s  %(suicide)8s  %(accident)9s | %(steal)6s  %(capture)4s  %(pickup)7s | %(pweapon)-28s  %(teams)s\n"]
STR_TOTAL_ROW = ["%(name)", "s  %(score)5s  %(frags)5s  %(fc_kills)9s  %(tk)10s | %(deaths)6s  %(suicide)8s  %(accident)9s | %(steal)6s  %(capture)4s  %(pickup)7s | %(pweapon)-28s\n"]

class BaseRender(object):

    def __init__(self, header_names, **kwargs):
        self.header_names = header_names

    def base(self, base_data):
        """
            Expect: base_data = {
                                'title': '',
                                'total_table': '',
                                'games_tables': '',
            }
        """
        return ''

    def game(self, game_data):
        """
            Expect: game_data = {
                                'map_name': '',
                                'game_type': '',
                                'start_time': '',
                                'duration': '',
                                'player_stats': '',
                                'player_vs_player': '',
                                'teams_stats': '',
            }
        """
        return ''

    def total(self, total_data):
        """
            Expect: total_data = {
                                'game_number': '',
                                'player_stats': '',
                                'player_vs_player': '',
            }
        """
        return ''


class HTMLRender(BaseRender):

    def __init__(self, header_names, **kwargs):
        capitalized_names = dict([(i, n.capitalize()) for i,n in header_names.items()])
        super(HTMLRender, self).__init__(capitalized_names, **kwargs)
        self.base_t = open(os.path.join(TEMPLATE_FOLDER, 'base.html')).read()
        self.game_t = open(os.path.join(TEMPLATE_FOLDER, 'game.html')).read()
        self.player_row_t = open(os.path.join(TEMPLATE_FOLDER, 'player_row.html')).read()
        self.team_row_t = open(os.path.join(TEMPLATE_FOLDER, 'team_row.html')).read()
        self.total_row_t = open(os.path.join(TEMPLATE_FOLDER, 'total_row.html')).read()
        self.total_t = open(os.path.join(TEMPLATE_FOLDER, 'total.html')).read()
        self.header_css = 'header'

    def base(self, base_data):
        css = open(os.path.join(TEMPLATE_FOLDER, 'style.css')).read()
        js = open(os.path.join(TEMPLATE_FOLDER, 'sorttable.js')).read()

        return self.base_t % dict(base_data, css=css, js=js)

    def game(self, game_data):
        return self.game_t % game_data

    def total(self, total_data):
        return self.total_t % total_data


    def game_table_header(self):
        return self.player_row_t % dict(self.header_names, css=self.header_css)

    def game_table_row(self, player):
        css = "%s-t" % player['last_team'].lower()
        return self.player_row_t % dict(player, css=css)

    def total_table_header(self):
        return self.total_row_t % dict(self.header_names, css=self.header_css)

    def total_table_row(self, player):
        return self.total_row_t % dict(player, css='')

    def kills_by_player_table_header(self, players_name):
        header = "<tr class='" + self.header_css + "'><td>%(killervskilled)s</td>" % self.header_names
        for name in players_name:
            header += "<td>%s</td>" % name
        return header

    def kills_by_player_table_row(self, data):
        return self._standard_row(data)

    def teams_table_header(self):
        return self.team_row_t % dict(self.header_names, css=self.header_css)

    def teams_table_row(self, team):
        css = "%s-t" % team['color'].lower()
        return self.team_row_t % dict(team, css=css)

    def _standard_row(self, data, css=''):
        return "<tr class='%s'>%s</tr>" % (css, ''.join(["<td>%s</td>" % d for d in data]))


class PlainTextRender(BaseRender):

    def __init__(self, header_names, **kwargs):
        uppercased_names = dict([(i, n.upper()) for i,n in header_names.items()])
        super(PlainTextRender, self).__init__(uppercased_names, **kwargs)
        lnl = kwargs['lnl']
        fcl = str(max(lnl, 4) + 1)
        self.player_row = STR_GAME_ROW[0] + fcl + STR_GAME_ROW[1]
        self.total_row = STR_TOTAL_ROW[0] + fcl + STR_TOTAL_ROW[1]
        self.kills_by_player_row_base = "  %"+str(lnl)+"s"


    def game_table_header(self):
        return self.player_row % self.header_names

    def game_table_row(self, player):
        return self.player_row % player

    def total_table_header(self):
        return self.total_row % self.header_names

    def total_table_row(self, player):
        return self.total_row % player

    def game(self, game_data):
        output  = SEP
        output += " MAP: %(map_name)s  TYPE: %(game_type)s  DATE: %(start_time)s  DURATION: %(duration)s\n"
        output += SEP
        output += "%(player_stats)s\n"
        output += "%(player_vs_player)s\n"
        output += "%(teams_stats)s\n"
        output += SEP
        return output % game_data

    def base(self, base_data):
        return "%(games_tables)s \n%(total_table)s" % base_data

    def kills_by_player_table_header(self, players_name):
        strf = self.kills_by_player_row_base * (len(players_name)+1)
        return (strf + "\n") % tuple([self.header_names['killervskilled']]+players_name)

    def kills_by_player_table_row(self, data):
        strf = self.kills_by_player_row_base * len(data)
        return (strf + "\n") % tuple(data)

    def teams_table_header(self):
        return "\n   %(color)s  %(caps)s  %(score)s\n" % self.header_names

    def teams_table_row(self, team):
        return "   %(color)5s  %(caps)4s  %(score)s\n" % team

    def total(self, total_data):
        output  = SEP
        output += "   TOTAL  N° JUEGOS: %(game_number)s\n" % total_data
        output += SEP
        output += "%(player_stats)s \n%(player_vs_player)s\n" % total_data
        output += SEP

        return output
