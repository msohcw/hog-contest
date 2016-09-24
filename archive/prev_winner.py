def final_strategy(score, opponent_score):
     return best_num_dice_to_roll(score, opponent_score)
          
import sys
from decimal import *
#Tell the Decimal class to use 100 digits of precision
getcontext().prec = 100
MAX_DICE = 10
MAX_RECURSION_DPETH = 2000
GOAL_SCORE = 100 # The goal of Hog is to score 100 points.
def memoized(f):
    data = {}
    def lookup(*args):
        key = (f, args)
        if not key in data:
            data[key] = f(*args)
        return data[key]
    return lookup
@memoized
def best_num_dice_to_roll(score, opponent_score):
    """ Returns the optimal number of dice to roll given score and opponent_score
    assuming it is the beginning of your turn.
    """
    if sys.getrecursionlimit() < MAX_RECURSION_DPETH:
        sys.setrecursionlimit(MAX_RECURSION_DPETH)
    if opponent_score == 1:
        #There is a good chance the opponent just hijinksed. Swap and pray!
        return -1
    score = Decimal(score)
    opponent_score = Decimal(opponent_score)
    best_probability, best_n = Decimal(0), 1
    #Iterate through each number of dice that can be rolled
    for n in range(0, MAX_DICE + 1):
        probability = probability_of_winning_by_rolling_n(score, opponent_score, n)
        if probability > best_probability:
            best_probability, best_n = probability, n
    return best_n
@memoized
def probability_of_winning_by_rolling_n(score, opponent_score, n):
    """ Returns probability that you will win if you roll n dice assuming it is
    your turn now.
    """
    sides = 6
    #Hog wild
    if hog_wild(score, opponent_score):
        sides = 4
    probability_of_winning = 0
    if n == 0:
        #Free Bacon
        turn_score = free_bacon_score(opponent_score)
        probability_of_winning = probability_of_winning_with_turn_end_scores(
                score + turn_score, opponent_score)
    else:
        #Iterate over each possible outcome for rolling n dice
        for possible_score in range(1, (sides * n) + 1):
            probability_of_winning += probability_of_scoring(possible_score, n,
                    sides) * probability_of_winning_with_turn_end_scores(
                    score + possible_score, opponent_score)
    return probability_of_winning
   
@memoized 
def probability_of_winning_with_turn_end_scores(score, opponent_score):
    """ Returns the chance that you will win the game if the scores are those
    passed in when your turn is complete.
    """
    #Swine swap
    if should_apply_swap(score, opponent_score):
        score, opponent_score = opponent_score, score
    if score >= GOAL_SCORE:
        return 1
    elif opponent_score >= GOAL_SCORE:
        return 0
    opponent_num_rolls = best_num_dice_to_roll(opponent_score, score)
    probability_of_opponent_winning = probability_of_winning_by_rolling_n(
            opponent_score, score, opponent_num_rolls)
    return 1 - probability_of_opponent_winning
        
@memoized
def number_of_ways_to_score(k, n, s):
    """ Returns the number of ways that k can be scored by rolling n
    s sided dice without pigging out.
    
    k: goal score
    n: number of dice to use
    s: number of sides on dice
    
    >>> number_of_ways_to_score(4, 1, 6)
    1
    >>> number_of_ways_to_score(12, 2, 6)
    1
    >>> number_of_ways_to_score(11, 2, 6)
    2
    >>> number_of_ways_to_score(7, 3, 6)
    3
    >>> number_of_ways_to_score(8, 3, 4)
    6
    """
    if k < 0:
        return 0
    if k == 0 and n == 0:
        return 1
    if n == 0:
        return 0
    total = 0
    for i in range(2, s + 1):
        total += number_of_ways_to_score(k - i, n - 1, s)
    return total
@memoized
def probability_of_scoring(k, n, s):
    """ Returns the chance that at least k will be scored by rolling n s sided
    dice without pigging out.
    
    k: goal score
    n: number of dice to use
    s: number of sides on dice
    
    >>> almost_equal = lambda x, y: abs(x - y) < 1e-10
    >>> almost_equal(probability_of_scoring(4, 1, 6), 1/6)
    True
    >>> almost_equal(probability_of_scoring(7, 3, 6), 3/216)
    True
    >>> almost_equal(probability_of_scoring(1, 2, 6), 11/36)
    True
    >>> almost_equal(probability_of_scoring(2, 3, 6), 0)
    True
    >>> almost_equal(probability_of_scoring(11, 10, 6), 0)
    True
    """
    if k == 1:
        return Decimal(1) - Decimal((pow(s - 1, n) / pow(s, n)))
    return Decimal(number_of_ways_to_score(k, n, s)) / Decimal(pow(s, n))

"""61A Presents The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact
import math
import random
GOAL_SCORE = 100  # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

def roll_dice(num_rolls, dice=six_sided):
    """Simulate rolling the DICE exactly NUM_ROLLS>0 times. Return the sum of
    the outcomes unless any of the outcomes is 1. In that case, return the
    number of 1's rolled.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'

    # BEGIN PROBLEM 1
    pig_out = 0;
    outcome = 0;
    for i in range(0,num_rolls):
        roll = dice()
        if roll == 1: pig_out += 1
        outcome += roll
    return pig_out or outcome
    # END PROBLEM 1


def free_bacon(opponent_score):
    """Return the points scored from rolling 0 dice (Free Bacon)."""
    # BEGIN PROBLEM 2
    return 1 + max(opponent_score//10, opponent_score%10)
    # END PROBLEM 2


# Write your prime functions here!
def is_prime(x):                                                              
    if(x == 2): return True                                                   
    if(x == 1 or x%2==0): return False                                          
    for i in range(3,math.ceil(math.sqrt(x))+1,2):
        if x % i == 0: return False                                    
    return True

def next_prime(x):
    assert is_prime(x), 'x must be prime'
    if x == 2: return 3 # edge case
    for i in range(x+2, GOAL_SCORE + 10, 2): # skips evens
        if is_prime(i): return i

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free Bacon).
    Return the points scored for the turn by the current player. Also
    implements the Hogtimus Prime and When Pigs Fly rules.

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    # Leave these assert statements here; they help check for errors.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice in take_turn.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    
    # BEGIN PROBLEM 2
    if(num_rolls == 0):
        # Free Bacon
        result = free_bacon(opponent_score)
    else:
        result = roll_dice(num_rolls, dice)

    # Hogtimus Prime
    if is_prime(result): result = next_prime(result)
    # When Pigs Fly
    result = min(25 - num_rolls, result)
    return result
    # END PROBLEM 2


def reroll(dice):
    """Return dice that return even outcomes and re-roll odd outcomes of DICE."""
    def rerolled():
        # BEGIN PROBLEM 3
        roll = dice()
        if roll % 2 == 0:
            return roll
        else:
           return dice()
        # END PROBLEM 3
    return rerolled


def select_dice(score, opponent_score, dice_swapped):
    """Return the dice used for a turn, which may be re-rolled (Hog Wild) and/or
    swapped for four-sided dice (Pork Chop).

    DICE_SWAPPED is True if and only if four-sided dice are being used.
    """
    # BEGIN PROBLEM 4
    dice = six_sided
    if dice_swapped: dice = four_sided
    # END PROBLEM 4
    if (score + opponent_score) % 7 == 0:
        dice = reroll(dice)
    return dice


def other(player):
    """Return the other player, for a player PLAYER numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - player

def play(strategy0, strategy1, score0=0, score1=0, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first
    strategy1:  The strategy function for Player 1, who plays second
    score0   :  The starting score for Player 0
    score1   :  The starting score for Player 1
    """

    player = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    dice_swapped = False  # Whether 4-sided dice have been swapped for 6-sided
    # BEGIN PROBLEM 5
    
    while score0 < goal and score1 < goal:
        
        P = {"strategy":[strategy0,strategy1],"score":[score0,score1]}
        
        player_score = P["score"][player]
        opponent_score = P["score"][other(player)]
        strategy = P["strategy"][player](player_score,opponent_score)
        
        if strategy == -1 : 
            # Pork Chop
            dice_swapped = not dice_swapped
            gain = 1
        else:
            gain = take_turn(P["strategy"][player](player_score,opponent_score),\
                            opponent_score,\
                            select_dice(player_score,opponent_score,dice_swapped))
        if player == 0:
            score0 += gain
        elif player == 1:
            score1 += gain
     
        # Swine Swap
        if max(score0,score1) == 2*min(score0,score1):
            store = score0
            score0 = score1
            score1 = store

        player = other(player)

    # END PROBLEM 5
    return score0, score1


#######################
# Phase 2: Strategies #
#######################

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy


def check_strategy_roll(score, opponent_score, num_rolls):
    """Raises an error with a helpful message if NUM_ROLLS is an invalid
    strategy output. All strategy outputs must be integers from -1 to 10.

    >>> check_strategy_roll(10, 20, num_rolls=100)
    Traceback (most recent call last):
     ...
    AssertionError: strategy(10, 20) returned 100 (invalid number of rolls)

    >>> check_strategy_roll(20, 10, num_rolls=0.1)
    Traceback (most recent call last):
     ...
    AssertionError: strategy(20, 10) returned 0.1 (not an integer)

    >>> check_strategy_roll(0, 0, num_rolls=None)
    Traceback (most recent call last):
     ...
    AssertionError: strategy(0, 0) returned None (not an integer)
    """
    msg = 'strategy({}, {}) returned {}'.format(
        score, opponent_score, num_rolls)
    assert type(num_rolls) == int, msg + ' (not an integer)'
    assert -1 <= num_rolls <= 10, msg + ' (invalid number of rolls)'


def check_strategy(strategy, goal=GOAL_SCORE):
    """Checks the strategy with all valid inputs and verifies that the
    strategy returns a valid input. Use `check_strategy_roll` to raise
    an error with a helpful message if the strategy returns an invalid
    output.

    >>> def fail_15_20(score, opponent_score):
    ...     if score != 15 or opponent_score != 20:
    ...         return 5
    ...
    >>> check_strategy(fail_15_20)
    Traceback (most recent call last):
     ...
    AssertionError: strategy(15, 20) returned None (not an integer)
    >>> def fail_102_115(score, opponent_score):
    ...     if score == 102 and opponent_score == 115:
    ...         return 100
    ...     return 5
    ...
    >>> check_strategy(fail_102_115)
    >>> fail_102_115 == check_strategy(fail_102_115, 120)
    Traceback (most recent call last):
     ...
    AssertionError: strategy(102, 115) returned 100 (invalid number of rolls)
    """
    # BEGIN PROBLEM 6
    for i in range(goal):
        for j in range(goal):
            check_strategy_roll(i,j,strategy(i,j))
    # END PROBLEM 6


# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    """
    # BEGIN PROBLEM 7
    def averaged(*args):
        total = 0
        for i in range(0, num_samples):
            total += fn(*args)
        return total/num_samples
    return averaged
    # END PROBLEM 7


def max_scoring_num_rolls(dice=six_sided, num_samples=1000):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE over NUM_SAMPLES times.
    Assume that the dice always return positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    # BEGIN PROBLEM 8
    best = 0
    max_average = 0
    for i in range(1,11):
        result = make_averaged(roll_dice, num_samples)(i,dice)
        if result > max_average:
            best = i
            max_average = result
    return best
    # END PROBLEM 8


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1


def average_win_rate(strategy, baseline=always_roll(4)):
    """Return the average win rate of STRATEGY against BASELINE. Averages the
    winrate when starting the game as player 0 and as player 1.
    """
    win_rate_as_player_0 = 1 - make_averaged(winner,100000)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner,100000)(baseline, strategy)

    return (win_rate_as_player_0 + win_rate_as_player_1) / 2


def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False:  # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        rerolled_max = max_scoring_num_rolls(reroll(six_sided))
        print('Max scoring num rolls for re-rolled dice:', rerolled_max)

    if False:  # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False:  # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False:  # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True:
        print('final_strategy win rate:', average_win_rate(final_strategy))
    "*** You may add additional experiments as you wish ***"


# Strategies

def prime_bacon(score,opponent_score):
    """
    Computes result of rolling 0 using Free Bacon, including effect of Hogtimus Prime
    """
    result = free_bacon(opponent_score)
    if is_prime(result): result = next_prime(result)
    return result

def bacon_strategy(score, opponent_score, margin=8, num_rolls=4):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    # BEGIN PROBLEM 9
    result = prime_bacon(score, opponent_score)
    if result >= margin: return 0
    return num_rolls

    # END PROBLEM 9
check_strategy(bacon_strategy)


def hog_wild(score,opponent_score):
    return (score+opponent_score)%7==0

def swap_strategy(score, opponent_score, margin=8, num_rolls=4):
    """This strategy rolls 0 dice when it triggers a beneficial swap. It also
    rolls 0 dice if it gives at least MARGIN points. Otherwise, it rolls
    NUM_ROLLS.
    """
    # BEGIN PROBLEM 10
    gain = prime_bacon(score,opponent_score)
    if (gain + score)*2 == opponent_score: return 0
    if gain >= margin and opponent_score*2 != (gain+score): return 0
    return num_rolls
    # END PROBLEM 10
check_strategy(swap_strategy)
