import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lumos_cli.cli import _detect_command_intent

class TestJiraIntentDetection(unittest.TestCase):
    def test_jira_query_with_keywords(self):
        """Test that a query with 'jira' and 'tickets' is detected as a jira intent"""
        query = "get all jira tickets assigned to me in current open sprint"
        intent = _detect_command_intent(query)
        self.assertEqual(intent['type'], 'jira')

    def test_jira_query_with_ticket_key(self):
        """Test that a query with a JIRA ticket key is detected as a jira intent"""
        query = "show me ticket PROJ-123"
        intent = _detect_command_intent(query)
        self.assertEqual(intent['type'], 'jira')

    def test_non_jira_query_with_filename(self):
        """Test that a query with a filename containing 'jira' is not detected as a jira intent"""
        query = "fix a bug in jira.py"
        intent = _detect_command_intent(query)
        self.assertNotEqual(intent['type'], 'jira')

    def test_general_chat_query(self):
        """Test that a general chat query is not detected as a jira intent"""
        query = "what is the weather today?"
        intent = _detect_command_intent(query)
        self.assertEqual(intent['type'], 'chat')

if __name__ == '__main__':
    unittest.main()
