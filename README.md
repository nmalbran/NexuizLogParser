Nexuiz Log Parser
=================

Log parser for Nexuiz game.
Based in Trablas' parser.

### Usage example

#### CLI
    python nex_parser.py server.log

#### As module
    from nex_parser import NexuizLogParser

    nlp = NexuizLogParser(KNOWN_PLAYER_NICKS)
    nlp.parse_log('server.log')

    print nlp.get_results()

### `KNOWN_PLAYER_NICKS` format
The same person can have different nicknames in one log file. To solve that, the parser receive the following dictionary with nicknames:

    KNOWN_PLAYER_NICKS =
        {
            'NamePlayer1': ['nick1', 'nick2', 'nick3'],
            'NamePlayer2': ['John', 'foo', 'bar'],
        }

### Result format
The results given by the `NexuizLogParser.get_results()` function follow this format:

    {
     0: {
         'map_data': {
                      'map_name': string,
                      'start_time': datetime.datetime,
                      'end_time': datetime.datetime,
                      'duration': 'H:MM:SS',
                      'game_type': string,
         },
         'teams': {
                   team1_id: {
                              'id': team1_id,
                              'color': string,
                              'caps': int,
                              'score': int,
                   },
                   team2_id: {...},
         },
         'players': {
                     player1_id: {
                                  'id': player1_id,
                                  'ip': string,
                                  'nick': string,
                                  'name': string,
                                  'team': ['<team_color> (H:MM:SS)', ...],

                                  'frags': int,
                                  'suicide': int,
                                  'accident': int,
                                  'tk': int,

                                  'capture': int,
                                  'return': int,
                                  'steal': int,
                                  'dropped': int,
                                  'pickup': int,
                     },
                     player2_id: {...},
         }
     },
     1: {...},
    }

*Notes*:

- `teamX_id` & `playerX_id` are the id given by Nexuiz, in string format.
- `[]['players']['nick']` is the nickname used in that game, while `[]['players']['name']` is the name mapped by `KNOWN_PLAYER_NICKS`.
- The time in `[]['players']['team']` is when the player joined the team.
- The top level numbers are the game's number, in order of appearance in the log.