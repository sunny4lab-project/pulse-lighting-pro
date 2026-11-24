"""Offline scene automation. Produces suggestions, never sends DMX."""
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Scene:
    name: str
    rgb: tuple
    intensity: int
    movement: int

SCENES = {
    "Prayer": Scene("Prayer",(65,55,180),70,0),
    "Praise": Scene("Praise",(230,90,30),160,20),
    "Worship": Scene("Worship",(50,75,210),100,8),
    "Sermon": Scene("Sermon",(255,225,190),180,0),
    "Offering": Scene("Offering",(180,100,40),120,8),
    "Closing": Scene("Closing",(255,240,210),150,0),
}

class Director:
    def __init__(self):
        self.mode="Manual"
        self.cue="Sermon"
        self.energy=0.0
    def select(self,cue):
        if cue not in SCENES: raise ValueError("Unknown cue")
        self.cue=cue
    def suggest(self, rms=0.0, seconds=0.0):
        if self.mode=="Manual": return None
        if self.mode not in ("Auto","Hybrid"): raise ValueError("Invalid mode")
        if not math.isfinite(rms) or not math.isfinite(seconds): raise ValueError("Invalid input")
        self.energy=.9*self.energy+.1*max(0,min(1,rms))
        s=SCENES[self.cue]
        movement=round(s.movement*self.energy*math.sin(seconds*.5))
        return dict(zip(("Red","Green","Blue"),s.rgb)) | {"Dimmer":s.intensity,"Pan":128+movement,"Tilt":128}
