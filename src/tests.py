import server
import client
import unittest


# UNIT TESTS

class CommunicationServerTest(unittest.TestCase):
    def test_cs_initialize(self):
        cs = server.CommunicationServer()
        self.assertEqual(len(cs.Games), 0)
        self.assertEqual(len(cs.Clients), 0)
        self.assertEqual(cs.MaxConcurrentClients, 8)
        self.assertIsNone(cs.app)

    def test_cs_maxconcurrentclients(self):
        cs = server.CommunicationServer(5)
        self.assertEqual(cs.MaxConcurrentClients, 5)

    #If this test is included the server will actually start and you will need to Ctrl+C to exit the server and continue with the testing
    """
    def test_create_server(self):
        cs = server.CommunicationServer()
        cs.CreateServer('127.0.0.1', '5000')
        self.assertIsNotNone(cs.app)
    """

class ClientTest(unittest.TestCase):
    def test_client_id(self):
        client = server.Client('abc123')
        self.assertTrue(client.get_id(), 'abc123')
        self.assertTrue(client.compare('abc123'))

class PlayerInfoTest(unittest.TestCase):
    def test_player_info(self):
        playerinfo = server.PlayerInfo()
        self.assertEqual(playerinfo.GamesPlayed, 0)
        self.assertEqual(playerinfo.GamesLeft, 0)
        self.assertEqual(playerinfo.NumberOfWins, 0)

class GameTest(unittest.TestCase):
    def test_game(self):
        game = server.Game('Adam', 'Bailey', True, None)
        self.assertEqual(game.PlayerA, 'Adam')
        self.assertEqual(game.PlayerB, 'Bailey')
        self.assertTrue(game.Active)
        self.assertIsNone(game.Winner)



# INTEGRATION TESTS

if __name__ == '__main__':
    unittest.main()
