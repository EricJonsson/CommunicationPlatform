import server, client
import time
import logging

val = int(input("Choose player 1 or 2 (Server - 4): "))

if val == 1:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    GameState = {"data": "[1,0,1] or sth"}
    player.SendGameData(GameState)
    time.sleep(2)
    player.Ready()
    time.sleep(5)

    #player.GetPlayerInfo()
    #time.sleep(2)
    player.SendGameData(GameState)
    player.GetMessageFromOpponent()
    time.sleep(3)
    player.SignalVictory()
    time.sleep(1000)
    player.Disconnect()
elif val == 2:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    player.SendInformationToOpponent({"data": "Hello dear opponent!"})
    time.sleep(2)
    player.Ready()
    time.sleep(6)
    player.SendInformationToOpponent({"data": "Hello dear opponent!"})
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
    cs.sio.logger.setLevel(logging.DEBUG)
    cs.CreateServer('127.0.0.1', 5000)
    input('Press Any Key to Shut down')
elif val == 5:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    player.Ready()
    time.sleep(2)
    input('Press Any Key to send message')
    player.SendInformationToOpponent({"data": "Hello dear opponent!"})
    input('Press Any Key to send message')
elif val == 6:
    player = client.Player()
    player.ConnectToServer('127.0.0.1', 5000)
    time.sleep(2)
    player.Ready()
    time.sleep(2)
    input('Press Any Key to Shut down')
    player.SendInformationToOpponent({"data": "Hello dear opponent!"})
    input('Press Any Key to Shut down')
else: # do whatever you want here :)
    pass
