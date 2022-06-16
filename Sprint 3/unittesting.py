import unittest
import sprint3


class functionTest(unittest.TestCase):
    ######################### Chaitanya Pawar's Code #########################
    def test_userstory17(self):
        result17 = [
            'ERROR: FAMILY: US17: 7:  F8: Parent I13 is married to their child : I17']
        self.assertEqual(sprint3.us17(), result17)

    def test_userstory18(self):
        result18 = ['ERROR: FAMILY: US18: 0:  F1: Siblings I2 and I1 are married',
                    'ERROR: FAMILY: US18: 9:  F10: Siblings I16 and I17 are married']
        self.assertEqual(sprint3.us18(), result18)
    
    ######################### End of Chaitanya Pawar's Code #########################


if __name__ == '__main__':
    unittest.main()