import unittest
import sprint2


class functionTest(unittest.TestCase):
    ######################### Chaitanya Pawar's Code #########################
    def test_userstory09(self):
        result09 = ['ERROR: FAMILY: US09: 3: I9: Father\'s death date 1920-09-08 before birthdate of child 1975-11-11',
                    'ERROR: FAMILY: US09: 4: I10: Mother\'s death date 1947-03-25 before birthdate of child 1947-09-11']
        self.assertEqual(sprint2.US09(), result09)

    def test_userstory10(self):
        result10 = ['ERROR: FAMILY: US10: 0: I2: Father\'s birth date 1990-06-08 less than 14 years of marriage date 1950-05-10',
                    'ERROR: FAMILY: US10: 3: I8: Mother\'s birth date 1947-09-11 less than 14 years of marriage date 1960-10-17',
                    'ERROR: FAMILY: US10: 4: I11: Father\'s birth date 1920-09-12 less than 14 years of marriage date 1923-02-10']
        self.assertEqual(sprint2.US10(), result10)
    
    ######################### End of Chaitanya Pawar's Code #########################


if __name__ == '__main__':
    unittest.main()