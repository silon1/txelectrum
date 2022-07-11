import txe_client

import unittest
from unittest.mock import Mock, patch

import hashlib


def create_recv_side_effect(return_value):
    i = 0
    def side_effect(self, n):
        if i >= len(return_value):
            return b''
        result = return_value[i:i+n]
        i += n
        return result
    return side_effect

class TestCreateKeyPair(unittest.TestCase):

    @patch("txe_client.socket.socket")
    def test_normal_flow(self, mock_socket):
        password = "Password123"
        expected_pubkey = bytes(i for i in range(0x20))
        result = b"\x01\x00\x00\x00\x01\x20\x00\x00\x00" + expected_pubkey
        mock_socket.send = Mock()
        mock_socket.recv = Mock(side_effect=create_recv_side_effect(result))

        try:
            pubkey = txe_client.create_keypair(password)
        except: pass

        mock_socket.send.assert_called_once()
        self.assertEqual(pubkey, expected_pubkey)


if __name__ == "__main__":
    unittest.main()
