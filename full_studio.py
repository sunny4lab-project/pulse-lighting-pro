import tkinter as tk
from tkinter import ttk
import time
from group_studio import GroupStudio
from automation import Director, SCENES

class FullStudio(GroupStudio):
    def __init__(self,root):
        super().__init__(root)
        self.director=Director()
        tabs=next(w for w in root.winfo_children() if isinstance(w,ttk.Notebook))
        panel=ttk.Frame(tabs,padding=20)
        tabs.add(panel,text="Auto lighting")
        ttk.Label(panel,text="Service director — simulation",font=("Arial",22,"bold")).pack(anchor="w")
        ttk.Label(panel,text="Rule-based preview; no live audio input or physical output.").pack(anchor="w")
        self.auto_mode=tk.StringVar(value="Manual")
        self.cue=tk.StringVar(value="Sermon")
        self.energy=tk.DoubleVar(value=0)
        for label,var,values in [("Mode",self.auto_mode,["Manual","Auto","Hybrid"]),("Service cue",self.cue,list(SCENES))]:
            ttk.Label(panel,text=label).pack(anchor="w")
            ttk.Combobox(panel,textvariable=var,values=values,state="readonly").pack(anchor="w")
        ttk.Label(panel,text="Simulated audio energy").pack(anchor="w")
        ttk.Scale(panel,from_=0,to=1,variable=self.energy).pack(fill="x")
        self.preview=tk.Canvas(panel,height=220,bg="#101827")
        self.preview.pack(fill="x",pady=15)
        self.summary=ttk.Label(panel,text="")
        self.summary.pack(anchor="w")
        self.auto_tick()
    def auto_tick(self):
        self.director.mode=self.auto_mode.get()
        self.director.select(self.cue.get())
        v=self.director.suggest(self.energy.get(),time.monotonic())
        c=self.preview;c.delete("all")
        if v:
            color="#%02x%02x%02x"%tuple(v[k] for k in ("Red","Green","Blue"))
            w=max(320,c.winfo_width())
            for i in range(16):
                x=(i+.5)*w/16
                dx=(v["Pan"]-128)*2
                c.create_polygon(x,10,x+dx-18,190,x+dx+18,190,fill=color,stipple="gray50")
            self.summary.configure(text=str(v))
        else:self.summary.configure(text="Manual mode — automation inactive")
        self.r.after(100,self.auto_tick)

if __name__=="__main__":
    root=tk.Tk()
    FullStudio(root)
    root.mainloop()
