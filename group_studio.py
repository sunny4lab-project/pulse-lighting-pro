import tkinter as tk
from tkinter import ttk, messagebox
from studio import Studio
from patch_engine import Fixture, Patch

class GroupStudio(Studio):
    def __init__(self, root):
        super().__init__(root)
        self.patch=Patch()
        tabs=next(w for w in root.winfo_children() if isinstance(w,ttk.Notebook))
        panel=ttk.Frame(tabs,padding=12)
        tabs.add(panel,text="Individual / Groups")
        ttk.Label(panel,text="Independent fixture simulation",font=("Arial",20,"bold")).pack(anchor="w")
        ttk.Label(panel,text="Simulation only: this workspace does not send physical DMX.").pack(anchor="w")
        self.fields={}
        for name,default in [("Name","Head 1"),("Group","Front"),("Universe","1"),("Address","1"),("Footprint","16"),("Offsets","Dimmer:1,Pan:2,Tilt:3")]:
            row=ttk.Frame(panel); row.pack(fill="x")
            ttk.Label(row,text=name,width=15).pack(side="left")
            v=tk.StringVar(value=default); self.fields[name]=v
            ttk.Entry(row,textvariable=v,width=50).pack(side="left")
        ttk.Button(panel,text="Add fixture",command=self.add_fixture).pack(anchor="w")
        self.table=ttk.Treeview(panel,columns=("group","universe","address","dimmer","pan","tilt"),show="tree headings",selectmode="extended",height=8)
        self.table.heading("#0",text="Fixture")
        for k in ("group","universe","address","dimmer","pan","tilt"):
            self.table.heading(k,text=k.title()); self.table.column(k,width=90)
        self.table.pack(fill="both",expand=True)
        self.group_name=tk.StringVar(value="All")
        row=ttk.Frame(panel); row.pack(fill="x")
        ttk.Entry(row,textvariable=self.group_name).pack(side="left")
        ttk.Button(row,text="Select group",command=self.select_group).pack(side="left")
        self.channel=tk.StringVar(value="Dimmer")
        ttk.Combobox(row,textvariable=self.channel,values=["Dimmer","Pan","Tilt","Red","Green","Blue","White"],state="readonly",width=12).pack(side="left")
        self.level=tk.IntVar(value=0)
        tk.Scale(row,from_=0,to=255,orient="horizontal",variable=self.level).pack(side="left")
        ttk.Button(row,text="Apply to selection",command=self.apply_level).pack(side="left")
        ttk.Button(row,text="Blackout",command=lambda:self.set_black(True)).pack(side="left")
        ttk.Button(row,text="Restore preview",command=lambda:self.set_black(False)).pack(side="left")
    def add_fixture(self):
        try:
            d={k:v.get() for k,v in self.fields.items()}
            channels={k.strip():int(v) for k,v in (s.split(":") for s in d["Offsets"].split(","))}
            self.patch.add(Fixture(d["Name"],int(d["Universe"]),int(d["Address"]),int(d["Footprint"]),channels,d["Group"]))
            self.refresh_table()
        except Exception as e: messagebox.showerror("Patch",str(e))
    def select_group(self):
        self.table.selection_set(self.patch.group(self.group_name.get()))
    def apply_level(self):
        try:
            self.patch.set_level(self.table.selection(),self.channel.get(),self.level.get())
            self.refresh_table()
        except Exception as e: messagebox.showerror("Control",str(e))
    def set_black(self,value):
        self.patch.blackout=value
        self.refresh_table()
    def refresh_table(self):
        selected=self.table.selection()
        self.table.delete(*self.table.get_children())
        frames=self.patch.frames()
        for n,f in self.patch.fixtures.items():
            values=[frames[f.universe][f.address+f.channels[k]-2] if k in f.channels else "-" for k in ("Dimmer","Pan","Tilt")]
            self.table.insert("","end",iid=n,text=n,values=(f.group,f.universe,f.address,*values))
        self.table.selection_set(selected)

if __name__=="__main__":
    root=tk.Tk()
    GroupStudio(root)
    root.mainloop()
