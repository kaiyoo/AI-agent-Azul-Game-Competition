from advance_model import AdvanceGameRunner, ReplayRunner
from displayer import TextGameDisplayer,GUIGameDisplayer
from utils import *
import sys
import importlib
import traceback
import players.naive_player
import random
import os
import pickle

players_names = []
players = [players.naive_player.myPlayer(0), players.naive_player.myPlayer(1)]
random_seed = 90054
warnning_time = 1
num_of_warning = 3
delay = 0.1
file_path = ""
games_results = [(0,0,0,0,0,0,0)]


def loadAgent(file_list,name_list):
    for i,file in enumerate(file_list):
        player_temp = None
        try:
            # if not name.endswith(".py"):
            #     name += ".py"
                
            player_file_path = 'players.'+ file
            mymodule = importlib.import_module(player_file_path)
            # students need to name their player as follows
            player_temp = mymodule.myPlayer(i)
        except (NameError, ImportError):
            print('Error: The team "' + player_file_path + '" could not be loaded! ', file=sys.stderr)
            traceback.print_exc()

        except IOError:
            print('Error: The team "' + player_file_path + '" could not be loaded! ', file=sys.stderr)
            traceback.print_exc()

        if player_temp != None:
            players[i] = player_temp
            if not options.superQuiet:
                print ('Player {} team {} agent {} loaded'.format(i,name_list[i],file_list[i]))
        else:
            print ('\n[Error] Player {} team {} agent {} loaded\n'.format(i,name_list[i],file_list[i]))


class HidePrint:
    # setting output steam
    def __init__(self,flag,file_path,f_name):
        self.flag = flag
        self.file_path = file_path
        self.f_name = f_name
        self._original_stdout = sys.stdout

    def __enter__(self):
        if self.flag:
            if not os.path.exists(self.file_path):
                os.makedirs(self.file_path)
            sys.stdout = open(self.file_path+"/log-"+self.f_name+".log", 'w')
            sys.stderr = sys.stdout
        else:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = sys.stdout

    # Restore
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr = sys.stdout


def run(options):

    # text displayer, will disable GUI
    displayer = GUIGameDisplayer(options.delay)
    if options.textgraphics:
        displayer = TextGameDisplayer()
    elif options.quiet or options.superQuiet:
        displayer = None
    # elif options.quiet:
    #     import textDisplay
    #     args['display'] = textDisplay.NullGraphics()
    # elif options.super_quiet:
    #     import textDisplay
    #     args['display'] = textDisplay.NullGraphics()
    #     args['muteAgents'] = True

    players_names.append(options.redName)
    players_names.append(options.blueName)
    for i in range(2):
        players_names[i] = players_names[i].replace(" ","_")

    random_seed = options.setRandomSeed
    warnning_time = options.warningTimeLimit
    num_of_warning = options.numOfWarnings
    file_path = options.output

    if options.replay != None:
        if not options.superQuiet:
            print('Replaying recorded game %s.' % options.replay)
        replay_dir = options.replay
        replay_dir = os.path.join(options.output,replay_dir)
        if "." not in replay_dir:
            replay_dir +=".replay"
        replay = pickle.load(open(replay_dir,'rb'),encoding="bytes")
        ReplayRunner(replay,displayer).Run()
    else: 
        for i in range(options.multipleGames):
            # loading players
            loadAgent([options.red,options.blue],players_names)

            import datetime
            f_name = players_names[0]+'-vs-'+players_names[1]+datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S-%f")
            
            if options.setRandomSeed == 90054:
                import time
                random_seed = int(str(time.time()).replace('.', ''))

            gr = AdvanceGameRunner(players,
                            seed=random_seed,
                            time_limit=warnning_time,
                            warning_limit=num_of_warning,
                            displayer=displayer,
                            players_namelist=players_names)
            print(file_path)
            with HidePrint(options.saveLog,file_path,f_name):                
                replay = gr.Run()

            _,_,r_total,b_total,r_win,b_win,tie = games_results[len(games_results)-1]
            r_score = replay[0][0]
            b_score = replay[1][0]
            r_total = r_total+r_score
            b_total = b_total+b_score
            if r_score==b_score:
                tie =  tie + 1
            elif r_score<b_score:
                b_win = b_win + 1
            else:
                r_win = r_win + 1
            if not options.superQuiet:
                print("Result of game ({}/{}): Player {} earned {} points; Player {} earned {} points\n".format(i+1,options.multipleGames,players_names[0],r_score,players_names[1],b_score))
            games_results.append((r_score,b_score,r_total,b_total,r_win,b_win,tie))

            if options.saveGameRecord:
                # f_name = file_path+"/replay-"+players_names[0]+'-vs-'+players_names[1]+datetime.datetime.now().strftime("%d-%b-%Y-%H-%M-%S-%f")+'.replay'
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                if not options.superQuiet:
                    print("Game ({}/{}) has been recorded!\n".format(i+1,options.multipleGames))
                record = pickle.dumps(replay)
                with open(file_path+"/replay-"+f_name+".reply",'wb') as f:
                    f.write(record)
        _,_,r_total,b_total,r_win,b_win,tie = games_results[len(games_results)-1]
        r_avg = r_total/options.multipleGames
        b_avg = b_total/options.multipleGames
        r_win_rate = r_win / options.multipleGames *100
        b_win_rate = b_win / options.multipleGames *100
        if not options.superQuiet:
            print(
                "Over {} games: \nPlayer {} earned {:+.2f} points in average and won {} games, winning rate {:.2f}%; \nPlayer {} earned {:+.2f} points in average and won {} games, winning rate {:.2f}%; \nAnd {} games tied.".format(options.multipleGames,
                players_names[0],r_avg,r_win,r_win_rate,players_names[1],b_avg,b_win,b_win_rate,tie))


def loadParameter():

    """
    Processes the command used to run Azul from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python runner.py <options>
    EXAMPLES:   (1) python runner.py
                    - starts a game with two NaivePlayer
                (2) python runner.py -r naive_player -b myPlayer
                    - starts a fully automated game where the red team is a NaivePlayer and blue team is myPlayer
    """
    parser = OptionParser(usageStr)

    parser.add_option('-r', '--red', help='Red team player file (default: naive_player)', default='naive_player')
    parser.add_option('-b', '--blue', help='Blue team player file (default: naive_player)', default='naive_player')
    parser.add_option('--redName', help='Red team name (default: Red NaivePlayer)', default='Red NaivePlayer')
    parser.add_option('--blueName', help='Blue team name (default: Blue NaivePlayer)',default='Blue NaivePlayer')
    parser.add_option('-t','--textgraphics', action='store_true', help='Display output as text only (default: False)', default=False)
    parser.add_option('-q','--quiet', action='store_true', help='No text nor graphics output, only show game info', default=False)
    parser.add_option('-Q', '--superQuiet', action='store_true', help='No output at all', default=False)
    parser.add_option('-w', '--warningTimeLimit', type='float',help='Time limit for a warning of one move in seconds (default: 1)', default=1.0)
    parser.add_option('-n', '--numOfWarnings', type='int',help='Num of warnings a team can get before fail (default: 3)', default=3)
    parser.add_option('-m', '--multipleGames', type='int',help='Run multiple games in a row', default=1)
    parser.add_option('--setRandomSeed', type='int',help='Set the random seed, otherwise it will be completely random (default: 90054)', default=90054)
    parser.add_option('-s','--saveGameRecord', action='store_true', help='Writes game histories to a file (named by teams\' names and the time they were played) (default: False)', default=False)
    parser.add_option('-o','--output', help='output directory for replay and log (default: output)',default='output')
    parser.add_option('-l','--saveLog', action='store_true',help='Writes player printed information into a log file(named by the time they were played)', default=False)
    parser.add_option('--replay', default=None, help='Replays a recorded game file by a relative path')
    parser.add_option('--delay', type='float', help='Delay action in a play or replay by input (float) seconds (default 0.1)', default=0.1)

    options, otherjunk = parser.parse_args(sys.argv[1:] )
    assert len(otherjunk) == 0, "Unrecognized options: " + str(otherjunk)
    return options


if __name__ == '__main__':

    """
    The main function called when advance_model.py is run
    from the command line:

    > python runner.py

    See the usage string for more details.

    > python runner.py --help
    """

    options = loadParameter()
    run(options)





