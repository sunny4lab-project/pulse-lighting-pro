"""Validated individual fixture patch and frame rendering, independent of GUI."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Fixture:
    name: str
    universe: int
    address: int
    footprint: int
    channels: dict
    group: str = "All"

class Patch:
    def __init__(self):
        self.fixtures = {}
        self.levels = {}
        self.blackout = True

    def add(self, fixture):
        f = fixture
        if not f.name or f.name in self.fixtures:
            raise ValueError("Fixture name must be unique")
        if not 1 <= f.universe <= 32768 or not 1 <= f.address <= 512 or not 1 <= f.footprint <= 513-f.address:
            raise ValueError("Invalid universe or footprint")
        offsets = list(f.channels.values())
        if "Dimmer" not in f.channels or len(offsets)!=len(set(offsets)) or any(type(x) is not int or not 1<=x<=f.footprint for x in offsets):
            raise ValueError("Unique verified offsets and dimmer required")
        for other in self.fixtures.values():
            if other.universe==f.universe and f.address<other.address+other.footprint and other.address<f.address+f.footprint:
                raise ValueError("DMX address overlap")
        self.fixtures[f.name]=f
        self.levels[f.name]={k:0 for k in f.channels}

    def set_level(self, names, channel, value):
        if type(value) is not int or not 0<=value<=255:
            raise ValueError("DMX level must be 0–255")
        names=list(names)
        if any(n not in self.fixtures or channel not in self.levels[n] for n in names):
            raise ValueError("Unknown fixture or unsupported channel")
        for n in names:
            self.levels[n][channel]=value

    def group(self, name):
        return [f.name for f in self.fixtures.values() if name=="All" or f.group==name]

    def frames(self):
        result={}
        for n,f in self.fixtures.items():
            frame=result.setdefault(f.universe,bytearray(512))
            for k,offset in f.channels.items():
                frame[f.address+offset-2]=0 if self.blackout and k=="Dimmer" else self.levels[n][k]
        return result
