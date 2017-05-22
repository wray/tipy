import unittest
import slackbot_tipy.bot_id
import slackbot_tipy.slackpi

class TestSlackBotFunctions(unittest.TestCase):

    def test_ci(self):
        self.assertTrue(True)

    def test_slack_client(self):
        self.assertTrue(bot_id.get_id() == None)

    def test_slack_pi(self):
        self.assertTrue(slackpi.handle_command("","") == None)


if __name__ == '__main__':
    unittest.main()
