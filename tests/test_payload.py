import unittest
from unittest.mock import patch
from agent.mqtt_client import build_command_payload
from agent.esp32_tools import set_digital_output

class PayloadTests(unittest.TestCase):
    def test_payload(self):
        self.assertEqual(build_command_payload("abc", "digital_write", pin=25,
            state="high", duration_seconds=10), {"command_id": "abc", "action": "digital_write",
            "pin": 25, "state": "high", "duration_seconds": 10})

    def test_no_duration(self):
        self.assertNotIn("duration_seconds", build_command_payload("abc", "digital_write",
            duration_seconds=None))

    @patch("agent.esp32_tools.send_command")
    def test_tool(self, command):
        set_digital_output(25, "high", 10)
        command.assert_called_once_with("digital_write", pin=25, state="high", duration_seconds=10)

    @patch("agent.esp32_tools.send_command")
    def test_invalid_pin(self, command):
        self.assertFalse(set_digital_output(34, "high")["success"])
        command.assert_not_called()

if __name__ == "__main__": unittest.main()
