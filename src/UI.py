import server, client
import time

val = int(input("Choose player 1 or 2 (Server - 4): "))

if val == 1:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    GameState = "[1,0,1] or sth"
    player.SendGameData(GameState)
    time.sleep(2)
    player.Ready()
    time.sleep(5)

    #player.GetPlayerInfo()
    #time.sleep(2)
    player.SendGameData(GameState)
    time.sleep(3)
    player.SignalVictory()
    time.sleep(1000)
    player.Disconnect()
elif val == 2:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    player.SendInformationToOpponent("Hello dear opponent!")
    time.sleep(2)
    player.Ready()
    time.sleep(6)
    player.SendInformationToOpponent("Hello dear opponent!")
    time.sleep(1000)
    player.Disconnect()
elif val == 3:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    time.sleep(2)
    player.Ready()
    time.sleep(1000)
    player.Disconnect()
elif val == 4:
    cs = server.CommunicationServer(8)
    cs.CreateServer('127.0.0.1', 5000)
    input('Press Any Key to Shut down')
else: # do whatever you want here :)
    pass
