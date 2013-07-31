
TEMPLATE_FOLDER = 'html_templates/'


class BaseRender(object):

    def __init__(self, header_names, display_bot=False):
        self.display_bot = display_bot
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
            }
        """
        return ''

class HTMLRender(BaseRender):

    def __init__(self, header_names, display_bot=False):
        super(HTMLRender, self).__init__(header_names, display_bot)
        self.base_t = open(TEMPLATE_FOLDER + 'base.html').read()
        self.game_t = open(TEMPLATE_FOLDER + 'game.html').read()
        self.row_t = open(TEMPLATE_FOLDER + 'row.html').read()


    def table_row_header(self):
        return self.row_t % dict(self.header_names, css='header')

    def table_row_player(self, player):
        return self.row_t % dict(player, css='')

    def game(self, game_data):
        return self.game_t % game_data

    def base(self, base_data):
        return self.base_t % base_data


class PlainTextRender(BaseRender):

    def __init__(self, display_bot=False):
        super(PlainTextRender, self).__init__(display_bot)