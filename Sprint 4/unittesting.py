import unittest
import sprint4


class functionTest(unittest.TestCase):
    ######################### Chaitanya Pawar's Code #########################
    def test_userstory25(self):
        result25 = ['ERROR: INDIVIDUAL: US25: No unique first name in family for name: Robert /Robinson/',
                    'ERROR: INDIVIDUAL: US25: No unique first name in family for name: Jon /Barathaon/',
                    'ERROR: INDIVIDUAL: US25: No unique first name in family for name: Cate /Tim/']
        self.assertEqual(sprint4.US25(), result25)

    def test_userstory26(self):
        result26 = ['ERROR: INDIVIDUAL: US26: No corresponding entries for Robb /Stark/ in the corresponding family records',
                    'ERROR: FAMILY: US26: No corresponding entries for Husband Name: Ned Stark and Wife Name: Cate Laniaster in the corresponding individual records']
        self.assertEqual(sprint4.US26(), result26)
    
    ######################### End of Chaitanya Pawar's Code #########################


if __name__ == '__main__':
    unittest.main()