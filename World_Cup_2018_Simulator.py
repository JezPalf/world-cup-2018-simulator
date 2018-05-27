import itertools
from random import random, randint
import texttable
import operator
from collections import Counter
import pprint


# the fixture function finds the result of the two teams and updates the team class as appropriate
def football_fixture(team1, team2, draws_allowed, reporting):
    # use rank to set win conditions
    delta = int(team1.rank) - int(team2.rank)
    # positive delta = team 1 better than team 2
    # negative delta = team 2 better than team 1
    if delta >= 0:
        win_condition_1 = 0.0006 * delta + 0.35
        win_condition_2 = 1 - (-0.0003 * delta + 0.35)
    else:
        win_condition_1 = -0.0003 * abs(delta) + 0.35
        win_condition_2 = 1 - (0.0006 * abs(delta) + 0.35)

    if not draws_allowed:
        draw_probability = win_condition_2 - win_condition_1
        win_condition_1 += draw_probability / 2
        win_condition_2 -= draw_probability / 2

    r = random()

    if r < win_condition_1:  # team 1 won
        if draws_allowed:
            team1.points += 3
            team1.result = team1.result + 'W'
            team2.result = team2.result + 'L'

        if delta >= 0:
            # this is the most likely result
            team1_goals = randint(1, int(round(0.0027 * delta + 2)))
            team2_goals = min([team1_goals - 1, int(round(-0.0009 * delta + 2))])
        else:
            team1_goals = randint(1, int(round(-0.0009 * abs(delta) + 2)))
            team2_goals = min([team1_goals - 1, int(round(0.0027 * abs(delta) + 2))])

    elif r < win_condition_2 and draws_allowed:
        # then we have a draw
        team1.points += 1
        team1.result = team1.result + 'D'
        team2.points += 1
        team2.result = team2.result + 'D'
        draw_goals = randint(0, int(round(-0.0036 * delta + 3)))
        team1_goals = draw_goals
        team2_goals = draw_goals

    else:  # team 2 won the game
        if draws_allowed:
            team2.points += 3
            team2.result = team2.result + 'W'
            team1.result = team1.result + 'L'

        if delta >= 0:
            # this is the most likely result
            team2_goals = randint(1, int(round(0.0027 * delta + 2)))
            team1_goals = min([team2_goals - 1, int(round(-0.0009 * delta + 2))])
        else:
            team2_goals = randint(1, int(round(-0.0009 * abs(delta) + 2)))
            team1_goals = min([team2_goals - 1, int(round(0.0027 * abs(delta) + 2))])

    # update the goal differences for each team for group stages
    if draws_allowed:
        team1.goals_forward += team1_goals
        team1.goals_against += team2_goals
        team1.goal_difference = team1.goals_forward - team1.goals_against
        team2.goals_forward += team2_goals
        team2.goals_against += team1_goals
        team2.goal_difference = team2.goals_forward - team2.goals_against

    # update the fixture history
    team1.fixtures += team2.team + ', ' + team1.result[-1]
    team2.fixtures += team1.team + ', ' + team2.result[-1]
    # report result
    if reporting:
        print('          ' + team1.code + '  ' + str(team1_goals) + ' - ' + str( team2_goals) + '  ' + team2.code)

    if not draws_allowed:
        if team1_goals > team2_goals:
            return team1
        else:
            return team2


# the group_stage function resolves all the fixtures within a group stage and stores the results inside the team class
def group_stages(teams_in_group, reporting):
    final_16 = []
    for i in range(8):  # 8 groups A to H
        this_group = teams_in_group[i]
        if reporting:
            print('\n               GROUP ' + this_group[0].group)
            # find all the fixtures for this group
        group_fixtures = list(itertools.combinations(this_group, 2))
        # play each fixture
        for j in range(len(group_fixtures)):
            team1, team2 = group_fixtures[j]
            football_fixture(team1, team2, draws_allowed=True, reporting=reporting)

        # determine group winners
        # sorted by points, GD, GF
        # still need to add in: points among those tied, GD among those tied.
        sorted_group = sorted(this_group, key=operator.attrgetter('points', 'goal_difference', 'goals_forward'))
        sorted_group.reverse()

        # build league tales using text table
        headers = ['Group ' + this_group[0].group, 'Form', 'GF', 'GD', 'Pts']
        table = texttable.Texttable()
        table.header(headers)
        for x in range(4):
            table.add_row([sorted_group[x].team, sorted_group[x].result, sorted_group[x].goals_forward,
                           sorted_group[x].goal_difference, sorted_group[x].points])

        table.set_cols_align(['l', 'r', 'r', 'r', 'r'])
        table.set_cols_width([15, 7, 7, 7, 7])
        table.set_chars(['', '', '', '='])

        if reporting:
            print(table.draw())

        # populate a list of winners and runners up from the group stages
        final_16 += [sorted_group[0], sorted_group[1]]

    return final_16


# the Finals function resolves the knock out stages of the finals
def final_stage(final_16, reporting):
    # Knock-out stages
    # the order of the final_16 list is:
    #   1A, 2A, 1B, 2B, 1C, 2C, 1D, 2D, 1E, 2E, 1F, 2F, 1G, 2G, 1H, 2H
    #   0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15
    # final 16
    if reporting:
        print('\n            Round of 16')
    # 1A v 2B (Match 49)
    match_49 = football_fixture(final_16[0], final_16[3], draws_allowed=False, reporting=reporting)
    # 1C v 2D (Match 50)
    match_50 = football_fixture(final_16[4], final_16[7], draws_allowed=False, reporting=reporting)
    # 1B v 2A (Match 51)
    match_51 = football_fixture(final_16[2], final_16[1], draws_allowed=False, reporting=reporting)
    # 1D v 2C (Match 52)
    match_52 = football_fixture(final_16[6], final_16[5], draws_allowed=False, reporting=reporting)
    # 1E v 2F (Match 53)
    match_53 = football_fixture(final_16[8], final_16[11], draws_allowed=False, reporting=reporting)
    # 1G v 2H (Match 54)
    match_54 = football_fixture(final_16[12], final_16[15], draws_allowed=False, reporting=reporting)
    # 1F v 2E (Match 55)
    match_55 = football_fixture(final_16[10], final_16[9], draws_allowed=False, reporting=reporting)
    # 1H v 2G (Match 56)
    match_56 = football_fixture(final_16[14], final_16[13], draws_allowed=False, reporting=reporting)

    # Quarter finals
    if reporting:
        print('\n          Quarter-finals')
    # Winner match 49 v Winner match 50 (Match 57)
    match_57 = football_fixture(match_49, match_50, draws_allowed=False, reporting=reporting)
    # Winner match 53 v Winner match 54 (Match 58)
    match_58 = football_fixture(match_53, match_54, draws_allowed=False, reporting=reporting)
    # Winner match 51 v Winner match 52 (Match 59)
    match_59 = football_fixture(match_51, match_52, draws_allowed=False, reporting=reporting)
    # Winner match 55 v Winner match 56 (Match 60)
    match_60 = football_fixture(match_55, match_56, draws_allowed=False, reporting=reporting)

    # Semi-finals
    if reporting:
        print('\n            Semi-finals')
    # Winner match 57 v Winner match 58 (Match 61)
    match_61 = football_fixture(match_57, match_58, draws_allowed=False, reporting=reporting)
    # Winner match 59 v Winner match 60 (Match 62)
    match_62 = football_fixture(match_59, match_60, draws_allowed=False, reporting=reporting)

    # Finals
    if reporting:
        print('\n               Final')
    # Winner match 61 v Winner match 62 (Match 63)
    world_cup_champions = football_fixture(match_61, match_62, draws_allowed=False, reporting=reporting)

    if reporting:
        print('\n  ' + world_cup_champions.team + ' are World Cup 2018 Champions!')

    return world_cup_champions


# The script that triggers the full simulation. Enter True to see tables and results. enter False to just have
# returned the champions instance.
def world_cup_simulator(reporting):
    # input data
    # team name, FIFA rank, group ID
    # 'England', 8, 'E'

    teams_list = []
    # load csv
    with open('teams.csv', 'r') as f:
        for line in f.readlines()[1:]:
            team, code, rank, group = line.strip().split(',')
            # define Team class
            teams_list.append(Team(team, code, rank, group))

    # isolate the teams by the group they appear in
    teams_in_group = [(list(g)) for _, g in itertools.groupby(teams_list, lambda x: x.group)]

    # simulate the group stages
    final_16 = group_stages(teams_in_group, reporting=reporting)

    # simulate the finals
    world_cup_champions = final_stage(final_16, reporting=reporting)

    return world_cup_champions


# define the team class
class Team:
    def __init__(self, team, code, rank, group):
        self.team = team
        self.code = code
        self.rank = rank
        self.group = group
        self.fixtures = []
        self.points = 0
        self.result = ''
        self.goal_difference = 0
        self.goals_forward = 0
        self.goals_against = 0

    def __repr__(self):
        return f'{self.team}'


# My useless code :)

def multiSim(num):
    count = num
    winners = []
    while count > 0:
        count -= 1
        winners.append(str((world_cup_simulator(reporting=False))))
    topFive = Counter(winners).most_common(5)
    print('The teams with the most world cup wins are:')
    pprint.pprint(topFive)


answer = input('Would you like a [d]etailed simulation or run [m]ultiple simulations? ')
if answer == 'd':
    world_cup_simulator(reporting=True)

elif answer == 'm':
    num = int(input('How many times would you like to run the simulation? '))
    multiSim(num)
