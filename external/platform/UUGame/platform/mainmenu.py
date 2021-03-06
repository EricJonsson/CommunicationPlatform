from .gamemodel import AiDifficulty, GameModel, Color, Player
from .gamecontroller import GameController
from .gameview import GameView
from .utils import clear_screen
from typing import Tuple
from src import server, client
import time

global Hosting
global NetworkPlayer
Hosting = False
NetworkPlayer = None

def mainmenu():
    is_running = True
    global Hosting

    while is_running:
        clear_screen()
        print_main_menu()
        choice = get_numeric_choice()

        if Hosting:
            if choice == 1:
                play_menu()
            elif choice == 2:
                join_menu()
            elif choice == 3:
                is_running = False
        else:
            if choice == 1:
                play_menu()
            elif choice == 2:
                host_menu()
            elif choice == 3:
                join_menu()
            elif choice == 4:
                if NetworkPlayer != None:
                    NetworkPlayer.Disconnect()
                is_running = False

    input("Exiting. \nPress Enter to continue...")


def print_main_menu():
    if Hosting:
        print(" ---------------- UU-Game ---------------- ")
        print("")
        print("")
        print("1) Play Local Game")
        print("2) Join Network Game")
        print("3) Quit")
        print("")
        print(" ***** Hosting Game on port: 5000 *****    ")

    else:
        print(" ---------------- UU-Game ---------------- ")
        print("")
        print("")
        print("1) Play Local Game")
        print("2) Host Network Game")
        print("3) Join Network Game")
        print("4) Quit")

def print_play_menu():
    global NetworkPlayer
    if NetworkPlayer == None:
        print("1) Player vs Player")
        print("2) Player vs Computer")
    else:
        print(" ---------------- Ready up for your next game! ---------------- ")
        print("1) Ready!")
        print("2) Logout")
        print("3) Statistics")

def print_ai_difficulty_menu():
    print("AI Difficulty")
    print("1) Easy")
    print("2) Medium")
    print("3) Hard")

def play_menu():
    invalid_choice = True

    while invalid_choice:
        clear_screen()
        print_play_menu()

        choice = get_numeric_choice()

        global NetworkPlayer

        if NetworkPlayer == None:
            if choice == 1:
                invalid_choice = False
                play_local()
            elif choice == 2:
                invalid_choice = False
                ai_difficulty_menu()
        else:
            if choice == 1:
                try:
                    if NetworkPlayer.Name == None:
                      NetworkPlayer.Name = input('Please Specify your name: ')
                      NetworkPlayer.SetName(NetworkPlayer.Name)

                    response = NetworkPlayer.Ready()
                except:
                    print('Unable to Ready up!')
                else:
                    if response == 0:
                        play_network()
                    else:
                        input('Failed to Ready up... \nPress any key to continue...')
            elif choice == 2:
                try:
                    response = NetworkPlayer.Disconnect()
                except:
                    print('Unable to disconnect!')
                if response == 0:
                    pass
                else:
                    input('Failed to disconnect... \nPress any key to continue...')
                invalid_choice = False
                NetworkPlayer = None
            elif choice == 3:
                display_statistics()
#                invalid_choice = False

def display_statistics():
    playerinfo = NetworkPlayer.GetPlayerInfo()
    try:
        g_wins = playerinfo['NumberOfWins']
        g_played = playerinfo['GamesPlayed']
        g_lost = g_played - g_wins
        stats = '*** Statistics *** \n\nGames Won:    {}\nGames Played: {} (includes skipped games)\nGames Lost:   {}\n\nPress Any Key to Continue...'.format(g_wins,g_played,g_lost)
        input(stats)
    except:
        input('Unable to get statistics... \nPress any key to continue...')

def get_numeric_choice() -> int or None:
    choice = input()
    if not choice.isnumeric():
        return None
    return int(choice)

def ai_difficulty_menu():
    invalid_choice = True

    while invalid_choice:
        clear_screen()
        print_ai_difficulty_menu()
        choice = get_numeric_choice()
        if choice is None:
            continue

        if 1 <= choice <= 3:
            invalid_choice = False
            play_local(ai_opponent = True, ai_difficulty = AiDifficulty(choice))

def host_menu():
    host = server.CommunicationServer()
    host.CreateServer()
    global Hosting
    Hosting = True
def join_menu():
    global NetworkPlayer
    NetworkPlayer = client.Player()
    response = NetworkPlayer.ConnectToServer('127.0.0.1', 5000)
    if response == 0:
        play_menu()
    else:
        input('Failed to Connect to server... \nPress any key to continue...')

def get_player_names() -> Tuple[str, str]:
    clear_screen()
    print("Player Black's name: ")
    black_player_name = input()
    print("Player White's name: ")
    white_player_name = input()
    return (black_player_name, white_player_name)

def play_local(ai_opponent = False, ai_difficulty = AiDifficulty.NONE):
    should_restart = True
    if ai_opponent:
        black_player_name = input('Select Name: ')
        white_player_name = 'AI - ' + str(ai_difficulty)
    else:
        (black_player_name, white_player_name) = get_player_names()

    while should_restart:
        game_model = GameModel()
        game_view = GameView(game_model)
        game_controller = GameController(game_model, game_view)

        if(ai_opponent):
            game_model.set_ai_player(Color.WHITE, ai_difficulty)

        game_model.set_player_name(Color.BLACK, black_player_name)
        game_model.set_player_name(Color.WHITE, white_player_name)

        winner = game_controller.start_game()
        should_restart = False
        if winner is None: # game was a draw
            should_restart = query_rematch_choice()

        input("Press Enter to continue...")

def play_network():
    index = 1
    while NetworkPlayer.CurrentOpponent == None:
        clear_screen()
        print('Matchmaking...\n\nWaiting: ',index)
        index += 1
        time.sleep(1)

    if NetworkPlayer.scoreBoard is not None:
      print('TOURNAMENT HAS ENDED')
      print('------FINAL RESULT--------')
      print(NetworkPlayer.scoreBoard)

      input('Returning to lobby, all stats will be reset\n\nPress any key to continue..')
      NetworkPlayer.CurrentOpponent = None
      NetworkPlayer.scoreboard  = None
      return

    if NetworkPlayer.CurrentOpponent['none'] == 1:
      NetworkPlayer.CurrentOpponent = None
      print('Couldn\'t find a game this round..')
      input('Returning to lobby\n\nPress any key to continue..')
      return


    playerColor = ''
    opponentcolor = NetworkPlayer.CurrentOpponent['color']
    if opponentcolor == 'white':
      playerColor = 'Black'
    else:
      playerColor = 'White'

    print('Matchup, Player: ', NetworkPlayer.CurrentOpponent['id'], '\nYou\'ll be playing: ', playerColor)
    input('Match found!\n\nPress Any Key to Continue...')

    game_model = GameModel()
    game_view = GameView(game_model)
    game_controller = GameController(game_model, game_view)
    game_controller.NetworkPlayer = NetworkPlayer

    if opponentcolor == 'white':
        game_model.set_network_player(Color.WHITE)
    elif opponentcolor == 'black':
        game_model.set_network_player(Color.BLACK)

    if opponentcolor == 'white':
        black_player_name = NetworkPlayer.Name
        white_player_name = NetworkPlayer.CurrentOpponent['id']
    elif opponentcolor == 'black':
        black_player_name = NetworkPlayer.CurrentOpponent['id']
        white_player_name = NetworkPlayer.Name

    game_model.set_player_name(Color.BLACK, black_player_name)
    game_model.set_player_name(Color.WHITE, white_player_name)

    winner = game_controller.start_game(NetworkedGame=True)

    if winner is not None:
        NetworkPlayer.SignalVictory(winner.color)

    input("Press Enter to continue...")


def query_rematch_choice() -> bool:
    invalid_choice = True

    while invalid_choice:
        clear_screen()
        print("Rematch? (Y/N)")
        choice = input().lower()
        if choice == "y":
            return True
        elif choice == "n":
            return False

if __name__ == "__main__":
    mainmenu()
