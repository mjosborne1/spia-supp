import unittest
import lighter

endpoint = 'http://localhost:8080/fhir'

class TestLighter(unittest.TestCase):
    def test_validate_code(self):
        """
        Test that lighter validate_concept function works correctly with just the code 1299141009
        """
        data = lighter.validate_concept(endpoint=endpoint, code="1299141009")
        self.assertTrue(data[0])
        """
        Testing 26958001
        """        
        data = lighter.validate_concept(endpoint=endpoint, code="26958001")
        self.assertTrue(data[0])
        """
        Testing 26958001 with incorrect display "Any old garbage"
        """  
        data = lighter.validate_concept(endpoint=endpoint, code="26958001", display="Any old garbage")
        self.assertFalse(data[0])
        """
        Test validate_concept on "394952009" fails with an correct display "Any old garbage" |3-MT urine"
        """ 
        data = lighter.validate_concept(endpoint=endpoint, code="394952009", display="3-MT urine")
        self.assertFalse(data[0])
        """
        Test validate_concept passes using "171140005",display="Malaria screening"
        """
        data = lighter.validate_concept(endpoint=endpoint, code="171140005",display="Malaria screening")
        self.assertTrue(data[0])
        """
        Test validate_concept fails using "873871000168106",display="Glycomark test"
        """        
        data = lighter.validate_concept(endpoint=endpoint, code="873871000168106",display="Glycomark test")
        self.assertFalse(data[0])

        