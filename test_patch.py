import unittest
from patch_engine import Fixture, Patch
from fixture_library import allocate

class PatchTests(unittest.TestCase):
    def setUp(self):
        self.p=Patch()
        self.p.add(Fixture("Front 1",1,1,16,{"Dimmer":1,"Pan":2},"Front"))
        self.p.add(Fixture("Rear 1",1,17,16,{"Dimmer":1,"Pan":2},"Rear"))
    def test_overlap(self):
        with self.assertRaises(ValueError):
            self.p.add(Fixture("Conflict",1,16,16,{"Dimmer":1}))
    def test_group(self):
        self.p.blackout=False
        self.p.set_level(self.p.group("Front"),"Dimmer",200)
        frame=self.p.frames()[1]
        self.assertEqual((frame[0],frame[16]),(200,0))
    def test_blackout(self):
        self.p.set_level(["Front 1"],"Dimmer",255)
        self.assertEqual(self.p.frames()[1][0],0)
    def test_boundary(self):
        self.assertEqual(allocate(32,20)[25],(2,1))
    def test_invalid(self):
        with self.assertRaises(ValueError):
            self.p.add(Fixture("Invalid",1,510,16,{"Dimmer":1}))

if __name__=="__main__":
    unittest.main()
