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
                response = NetworkPlayer.Ready()
                if response == 0:
                    play_network()
                else:
                    input('Failed to Ready up... \nPress any key to continue...')
                invalid_choice = False
            elif choice == 2:
                response = NetworkPlayer.Disconnect()
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
        input('Games Won: ', str(playerinfo.NumberOfWins),
              '\nGames Played: ', str(playerinfo.GamesPlayed),
              '\nGames Lost: ', str(playerinfo.GamesPlayed - playerinfo.NumberOfWins),
              '\n\nPress Any Key to Continue...')
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

    # Get Opponent From Server ( Blocking )
    # Return: Opponent Name / Color

    while NetworkPlayer.CurrentOpponent == None:
        time.sleep(1)
    print('Matchup, Player: ', NetworkPlayer.CurrentOpponent['id'], '\nColor: ',NetworkPlayer.CurrentOpponent['color'])
    input('Match found!\n\nPress Any Key to Continue...')

    should_restart = True
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
