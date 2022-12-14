from methods import *
import multiprocessing as mp
import os
import sys


# os.path.join(logdir, method.__name__ + '_' + str(n + testnum) + '.txt')
def play_game(player, method, filename, number, param1, param2=None, start=0):
    for testnum in range(number):
        f = open(filename + str(start + testnum) + '.txt', 'w')
        f.write(f"\tSimulation #{start + testnum}\n")
        f.write(f"{method.__code__.co_varnames[1]} : {param1}\n")
        if param2:
            f.write(f"{method.__code__.co_varnames[2]} : {param2}\n")
        # I know it's bad practice, but I needed the name and __code__ is *right there*.
        f.write(f"board :\n")
        player.create_board()
        for row in player.board:
            f.write(f"{'|'.join([case if case != '' else '  ' for case in row])}|\n")
        plays = []
        points = 0
        by_line = []
        wordzee = True
        for i, row in enumerate(player.board):
            f.write("----------\n")
            f.write(f"\tRound {i + 1}\n")
            # print(f"Playing round {row}")
            k = len(row)
            player.cases = row
            player.swap_letters('', inPlace=True)
            # print(f"Letters are {player.letters}")
            f.write(f"Starting letters : |{'|'.join(player.letters)}|\n")
            for l in range(2):
                if param2:
                    kept = method(param1, param2)
                else:
                    kept = method(param1)
                # print(f"Keeping {kept}")
                player.swap_letters(kept)
                # print(f"New letters are {player.letters}")
                f.write(f"Swap {l + 1} :           |{'|'.join(player.letters)}|\n")
            P = player.words_containing(player.letters, row)
            played = max(P.keys(), key=P.get)
            if len(played) < k:
                wordzee = False
                plays.append(list(played) + (k - len(played)) * [' '])
            else:
                plays.append(list(played))
                P[played] -= player.full_bonus
            P[played] *= i + 1
            # print(f"Playing {played} for {P[played]} points")
            # print(played)
            f.write(f"{' |'.join(plays[-1])} | {P[played]}\n")
            f.write(f"{'|'.join([case if case != '' else '  ' for case in row])}|\n")
            points += P[played]
            by_line.append(P[played])
            # print("-----------")
        if wordzee:
            points += 100
            # print("Wordzee !")

        f.write(f"----------\n")
        for i, p in enumerate(plays):
            f.write(f"{'|'.join(p)}| {'  ' * (player.max_letters - len(p))} |{by_line[i]}|\n")

        f.write(f"\nWordzee : {wordzee}\n")
        f.write(f"Total score : {points}")

        print(f"Game number {start + testnum}\nPoints:{points}\nWordzee:{wordzee}")

        # print(plays)
        # print(points)

        f.close()


def simuls(start, number):
    player = Wordzee("French ODS dictionary.txt", "letters.txt")

    method = player.KPPV_search
    logdir = "D://Wordzee/logs/" + method.__name__
    # Number of files in log folder
    n = len([entry for entry in os.listdir(logdir) if
             os.path.isfile(os.path.join(logdir, entry)) and entry.startswith(method.__name__)]) + 1

    param1 = 2
    param2 = 1 / 2 - 0.001  # minus epsilon for stability.
    play_game(player, method, os.path.join(logdir, method.__name__ + '_'), number, param1, param2, start=start)


if __name__ == '__main__':
    free_cores = 1
    d = "D://Wordzee/logs/" + "KPPV_search"
    s = len([entry for entry in os.listdir(d) if
             os.path.isfile(os.path.join(d, entry))]) + 1
    max_cores = mp.cpu_count()
    cores = max_cores - free_cores
    nmax = 100000
    processes = [mp.Process(target=simuls, args=(s + k * nmax // cores, nmax // cores)) for k in range(cores)]
    for p in processes:
        p.start()
