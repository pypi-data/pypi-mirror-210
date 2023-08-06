# == UNIT TEST testregion.py ==

"""
Unit tests for the region.Region class.
"""

import unittest

# 1A. Import the Region class
from ..region import Region

class TestRegion(unittest.TestCase):

    # -- Setting the stage --
    
    # The setUpClass method is invoked only once at the beginning of the testing.
    # Put initialisation code here that applies to all tests.
    @classmethod
    def setUpClass(cls):
        # The correctly formatted strings are constant so we can set them up only once
        # as class variables.
        cls.goodbed = "chr1\t15\t25\tgood\t7.2\t+"
        cls.goodgff = "chr1\tmysrc\tgood\t16\t25\t7.2\t+\t.\t."

    # 1B. The setUp method is invoked before each testing method.
    # Use it to create objects/variables "afresh", open files etc.
    def setUp(self):
        # create an empty region
        self.empty = Region()
        
        # create a good region
        self.r = Region("chr1", 15, 25, "good", 7.2, "+")
    
    # -- The testing methods --
    
    # The names of these methods must begin with `test`.
    # Each method should test only one particular functionality.
    # To compare observed and expected values, make use of the 
    # various `assertXXXX` methods of the `unittest.TestCase` class.
    # The test methods are invoked automatically by the 
    # `main` method (see below). The order of invocation is undefined.
    # NEVER write test methods that somehow depend on each other!

    # 2. Test __init__
    def test_init(self):
        # 2A. Properly initialised region
        self.assertEqual(self.r.chrom, "chr1")
        self.assertEqual(self.r.start, 15)
        self.assertEqual(self.r.end, 25)
        self.assertEqual(self.r.name, "good")
        self.assertEqual(self.r.score, 7.2)
        self.assertEqual(self.r.strand, "+")
        
        # 2B. Automatic corrections
        r = Region("chr2", 30, 15, "swap", strand = "X")
        self.assertEqual(r.start, 15)
        self.assertEqual(r.end, 30)
        self.assertEqual(r.strand, ".")

        ### Additional assignment: test an empty Region
        self.assertEqual(self.empty.chrom, "chrUn")
        self.assertEqual(self.empty.start, 0)
        self.assertEqual(self.empty.end, 0)
        self.assertEqual(self.empty.name, ".")
        self.assertEqual(self.empty.score, 0.0)
        self.assertEqual(self.empty.strand, ".")

    # 3. Test reading from a BED-formatted string
    def test_from_bed(self):
        # 3A. Empty string, all-whitespace string, comment
        for line in ("", " \t ", "# comment"):
            self.assertFalse(self.r.from_bed(line))

        # 3B. Check number of fields
        with self.assertRaises(ValueError, msg="Too few fields"):
            self.r.from_bed("chr\t123")

        # 3C. Correct format
        ok = self.empty.from_bed(self.goodbed)
        self.assertTrue(ok)
        ### Additional assignment
        # self.empty must be equal to self.r now (the same data were read)
        self.assertEqual(self.empty, self.r)

        ### Additional assignment
        # check invalid integer fields
        with self.assertRaises(ValueError, msg="invalid literal for int() with base 10: 'joe'"):
            self.r.from_bed("chr\t1\tjoe")

    # 4. Test writing GFF-formatting string
    def test_to_gff(self):
        gffstr = self.r.to_gff(src="mysrc")
        self.assertEqual(gffstr, self.goodgff)

    # 5. Test equality
    def test_equal(self):
        """test (in)equality of two Region objects"""
        er = Region("chr1", 15, 25, "good", 7.2, "+")
        self.assertEqual(self.r, er)
        dr = Region("chr1", 15, 25, "good", 3.3, "-")
        self.assertNotEqual(self.r, dr)

    # 6. Test region size
    def test_size(self):
        self.assertEqual(self.r.size, 10)

    # *** Homework tests ***

    # NOTE: these tests are _NOT_ copied into the "skel" version of `testregion.py`

    # X3. Test reading from a GFF-formatted string
    def test_from_gff(self):
        # X3A. Empty string, all-whitespace string, comment
        for line in ("", " \t ", "# comment", "##gff_version 2"):
            self.assertFalse(self.r.from_gff(line))

        # X3B. Check number of fields
        with self.assertRaises(ValueError, msg="Too few fields"):
            self.r.from_gff("chr\tsrc\t123")

        # X3C. Correct format
        ok = self.empty.from_gff(self.goodgff)
        self.assertTrue(ok)
        ### Additional assignment
        # self.empty must be equal to self.r now (the same data were read)
        self.assertEqual(self.empty, self.r)

        ### Additional assignment
        # check invalid integer fields
        with self.assertRaises(ValueError, msg="invalid literal for int() with base 10: 'joe'"):
            self.r.from_gff("chr\tsrc\tbadregion\t1\tjoe")

    # X4. Test writing BED-formatting string
    def test_to_bed(self):
        bedstr = self.r.to_bed()
        self.assertEqual(bedstr, self.goodbed)

    # *** End of homework tests ***

    # -- After testing --
    
    # 1C. The tearDown method is invoked after each testing method has been run.
    # Use it to clean up the remnants of tests, close files.
    # It is used less often than its pendant setUp .
    def tearDown(self):
        pass

    # The tearDownClass method is invoked after the whole testing has finished.
    # It can be used to clean up things that were set up by setUpClass
    # at the very beginning.
    @classmethod
    def tearDownClass(cls):
        pass


# 2C. Run the unit tests
if __name__ == "__main__":
    unittest.main()

