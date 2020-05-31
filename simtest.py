import ootp
from itertools import combinations
from sqlalchemy import create_engine


def main():
    al = 'BAL BOS CWS CLE DET HOU KC LAA MIN NYY OAK SEA TB TEX TOR'.split()
    nl = 'ARI ATL CHC CIN COL LAD MIA MIL NYM PHI PIT SD SF STL WAS'.split()

    matchups = combinations(al + nl, 2)

    # This following block is dumb but was using this as a testing script and was lazy
    new_matchups = []
    for matchup in matchups:
        if 'SEA' in matchup:
            new_matchups.append(matchup)

    report_path = 'C:/Users/lcarl/Documents/Out of the Park Developments/OOTP Baseball 20/saved_games/New Game 5.lg/news/html/temp/simulation_report.html'

    # Setting up where the OOTP client has certain menu items
    sim = ootp.Simulation(report_path)
    play_menu = ootp.PlayMenu(x=3021, y=96)
    sim_menu = ootp.SimMenu()
    sim_module = ootp.SimModule(x=2937, away_y=441, home_y=480, clear_y=42,
                                button_y=689, file_path='mlb.csv')
    reset = ootp.ResetWindow(x=3726, y=20)

    stats = ootp.Stats()

    home = None
    matchups = new_matchups

    # Run through each matchup, simulate, and parse the report
    for matchup in matchups:
        play_menu.open()
        sim_menu.open()

        if matchup[0] != home:
            home = matchup[0]
            print('Starting {}'.format(home))
            sim_module.clear_matchup()
            sim_module.update_team(sim_module.locs[home])

        sim_module.update_team(sim_module.locs[matchup[1]], type='away')

        sim_module.simulate()
        sim.watch_file_updates()
        sim.create_soup()
        result = ootp.Matchup(sim.soup)
        stats.add_matchup_stats(result)
        reset.iterate()

    # Takes all those stats from the simulations and just combines them based on player and team IDs
    stats.aggregate_stats()

    # Can save as a CSV with specific path and file name
    stats.send_to_csv(prepend='mlb_', append='_2020-05-29', path='E:/')

    # With SQLAlchemy can send to database tables
    engine = create_engine(
        'mysql://{0}:{1}@{2}:{3}'.format('username', 'password', '127.0.0.1', '3306'))
    connection = engine.connect()
    stats.send_to_mysql(connector=connection, tables=['pb', 'pp', 'tb', 'tp'],
                        schema='pcbl', if_exists='replace')


if __name__ == '__main__':
    main()
