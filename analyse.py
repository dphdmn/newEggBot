import copy
import move
from prettytable import PrettyTable
from solver import solvers

def analyse(scramble, solution):
    # check that the solution works
    scramble2 = copy.deepcopy(scramble)
    scramble2.apply(solution)
    if not scramble2.solved():
        raise ValueError(f"solution \"{solution.to_string()}\" does not solve scramble \"{scramble.to_string()}\"")

    table = PrettyTable()
    table.field_names = ["N", "State", "Setup", "Move", "Better", "Your ending", "Better ending", "Your+opt"]

    # the optimal solution of the scramble
    opt_end = solvers[4].solveOne(scramble)

    pos = copy.deepcopy(scramble)

    for i in range(1, solution.length()):
        # the first i moves of our solution
        user_start = solution.take(i)

        # apply the next move
        next_move = solution.at(i-1)
        pos.move(next_move)

        # optimal solution of position with i-1 moves applied
        last_opt_end = opt_end

        # solutions of the position with i moves applied
        opt_end = solvers[4].solveOne(pos)
        user_end = solution.drop(i)

        # the optimal solution length increased, so this is a mistake
        if opt_end.length() == last_opt_end.length() + 1:
            N = i

            pos.undo_move(next_move)
            state = pos.to_string()
            pos.move(next_move)
            
            setup = user_start.rdrop(1).to_string()
            bad_move = move.to_string(next_move)
            better = move.to_string(last_opt_end.first())
            your_ending = solution.drop(i-1).to_string()
            better_ending = last_opt_end.to_string()
            your_plus_opt = setup + better_ending

            table.add_row([N, state, setup, bad_move, better, your_ending, better_ending, your_plus_opt])

        # user end is optimal, so we don't need to calculate any further
        if opt_end.length() == user_end.length():
            break

    return table.get_string()