import os, sys
current_path = os.getcwd()
sys.path.append(current_path + '/src')
sys.path.append(current_path + '/external/engine/src')

from src import server
from external.platform.UUGame.platform import mainmenu as menu
from external.engine.src import game_engine

#host = server.CommunicationServer()
#host.CreateServer()

menu.mainmenu()
