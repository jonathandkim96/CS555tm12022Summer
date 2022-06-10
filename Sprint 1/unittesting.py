import unittest
import sprint1


class functionTest(unittest.TestCase):
    ######################### Chaitanya Pawar's Code #########################
    def test_userstory01(self):
        result01 = ['ERROR: INDIVIDUAL: US01: 5: I6: Jon /Barathaon/ has a Birthday on 2050-07-10 which occurs in the future', 'ERROR: INDIVIDUAL: US01: 10: I11: Olenna /Tully/ has a Deathday on 2222-10-28 which occurs in the future',
                    'ERROR: FAMILY: US01: 2: F3: Marriage Day 2090-06-20 between Jamie /Lanaster/ (ID: I7) and Cercie /Tyrell/ (ID: I8) occurs in the future']
        self.assertEqual(sprint1.US01(), result01)

    def test_userstory02(self):
        result02 = [
            'ERROR: INDIVIDUAL: US02: 1: I2: Ted /Robinson/ has a birthday on 1990-06-08 which is after his marriage date 1950-05-10']
        self.assertEqual(sprint1.US02(), result02)
    
    ######################### End of Chaitanya Pawar's Code #########################


if __name__ == '__main__':
    unittest.main()