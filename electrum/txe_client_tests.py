import txe_client

import unittest
from unittest.mock import MagicMock, patch
import io
import hashlib

LOCALHOST = '127.0.0.1'
PORT = 51841

class TestCreateKeyPair(unittest.TestCase):

    @patch("txe_client.socket.socket")
    def test_normal_flow(self, mock_socket):
        # setup
        password = "Password123"
        password_digest = hashlib.sha1(password.encode()).digest()
        expected_message = b"\x01\x00\x00\x00\x01\x14\x00\x00\x00" + password_digest
        expected_pubkey = bytes(i for i in range(0x20))
        response = io.BytesIO(b"\x01\x00\x00\x00\x01\x20\x00\x00\x00" + expected_pubkey)

        mock_socket.return_value = mock_socket
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.recv = MagicMock(side_effect=response.read)

        # action
        pubkey = txe_client.create_keypair(password)

        # assert
        mock_socket.assert_called_once()
        mock_socket.connect.assert_called_once_with((LOCALHOST, PORT))
        mock_socket.send.assert_called_once_with(expected_message)
        self.assertEqual(pubkey, expected_pubkey)


if __name__ == "__main__":
    unittest.main()
