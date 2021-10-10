import os, sys
current_path = os.getcwd()
sys.path.append(current_path + '/src')

from src import server
from external.platform.UUGame.platform import mainmenu as menu

host = server.CommunicationServer()
host.CreateServer()

menu.mainmenu()
