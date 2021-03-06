# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from __future__ import print_function

from time import sleep, time
from unittest import TestCase

from pyqrllib import pyqrllib


class TestHash(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestHash, self).__init__(*args, **kwargs)

    def test_xmss(self):
        HEIGHT = 6

        seed = pyqrllib.ucharVector(48, 0)
        xmss = pyqrllib.Xmss(seed=seed, height=HEIGHT)

        # print("Seed", len(seed))
        # print(pyqrllib.bin2hstr(seed, 48))
        #
        # print("PK  ", len(xmss.getPK()))
        # print(pyqrllib.bin2hstr(xmss.getPK(), 48))
        #
        # print("SK  ", len(xmss.getSK()))
        # print(pyqrllib.bin2hstr(xmss.getSK(), 48))

        self.assertIsNotNone(xmss)
        self.assertEqual(xmss.getHeight(), HEIGHT)

        message = pyqrllib.ucharVector([i for i in range(32)])
        # print("Msg ", len(message))
        # print(pyqrllib.bin2hstr(message, 48))

        # Sign message
        signature = bytearray(xmss.sign(message))

        # print("Sig ", len(signature))
        # print(pyqrllib.bin2hstr(signature, 128))
        #
        # print('----------------------------------------------------------------------')
        # Verify signature
        start = time()
        for i in range(1000):
            self.assertTrue(pyqrllib.Xmss.verify(message,
                                                 signature,
                                                 xmss.getPK()))
        end = time()
        # print(end - start)

        # Touch the signature
        signature[100] += 1
        self.assertFalse(pyqrllib.Xmss.verify(message,
                                              signature,
                                              xmss.getPK()))
        signature[100] -= 1
        self.assertTrue(pyqrllib.Xmss.verify(message,
                                             signature,
                                             xmss.getPK()))

        # Touch the message
        message[2] += 1
        self.assertFalse(pyqrllib.Xmss.verify(message,
                                              signature,
                                              xmss.getPK()))
        message[2] -= 1
        self.assertTrue(pyqrllib.Xmss.verify(message,
                                             signature,
                                             xmss.getPK()))
