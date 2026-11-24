import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from fixture_library import load_profile, match_profiles, allocate
from app import App

class Studio(App):
    def __init__(self, root):
        style=ttk.Style(root)
        style.theme_use("clam")
        root.configure(bg="#101827")
        style.configure(".", background="#182235", foreground="#e2e8f0", fieldbackground="#26354a", font=("Arial",11))
        style.configure("TButton", padding=8)
        style.map("TButton", background=[("active","#365477")])
        style.configure("TNotebook.Tab", padding=(18,10))
        super().__init__(root)
        root.title("Pulse Lighting Pro | 0.2 Studio")
        root.geometry("1180x820")
        self.profiles=[]
        self.matches=[]
        tabs=next(w for w in root.winfo_children() if isinstance(w,ttk.Notebook))
        panel=ttk.Frame(tabs,padding=18)
        tabs.add(panel,text="Fixture intelligence")
        ttk.Label(panel,text="FIXTURE INTELLIGENCE",font=("Arial",22,"bold")).pack(anchor="w")
        ttk.Label(panel,text="Offline profile matching • Suggestions only • Verify against fixture manual").pack(anchor="w",pady=8)
        bar=ttk.Frame(panel); bar.pack(fill="x")
        ttk.Button(bar,text="Import fixture JSON",command=self.import_profiles).pack(side="left")
        self.query=tk.StringVar()
        self.footprint=tk.StringVar()
        ttk.Label(bar,text="Model / manufacturer").pack(side="left",padx=8)
        ttk.Entry(bar,textvariable=self.query,width=24).pack(side="left")
        ttk.Label(bar,text="Channels").pack(side="left",padx=8)
        ttk.Entry(bar,textvariable=self.footprint,width=6).pack(side="left")
        ttk.Button(bar,text="Find matches",command=self.search).pack(side="left",padx=8)
        self.results=ttk.Treeview(panel,columns=("model","type","mode","channels"),show="headings",height=10)
        for k,w in [("model",260),("type",220),("mode",200),("channels",80)]:
            self.results.heading(k,text=k.title()); self.results.column(k,width=w)
        self.results.pack(fill="both",expand=True,pady=12)
        self.results.bind("<<TreeviewSelect>>",self.details)
        self.detail=tk.Text(panel,height=10,bg="#101827",fg="#e2e8f0",wrap="word")
        self.detail.pack(fill="x")
        ttk.Button(panel,text="Preview address allocation for selected mode",command=self.preview_patch).pack(anchor="w",pady=8)
        ttk.Label(panel,text="Unknown fixture? Record its LCD model, channel mode and manual. Never scan unknown DMX channels live.",wraplength=950).pack(anchor="w")
    def import_profiles(self):
        for path in filedialog.askopenfilenames(filetypes=[("Fixture JSON","*.json")]):
            try: self.profiles.append(load_profile(path))
            except Exception as e: messagebox.showerror("Import",str(e))
        self.search()
    def search(self):
        try:
            footprint=int(self.footprint.get()) if self.footprint.get().strip() else None
            self.matches=match_profiles(self.profiles,self.query.get(),footprint)
            self.results.delete(*self.results.get_children())
            for i,(_,p,m) in enumerate(self.matches):
                self.results.insert("","end",iid=str(i),values=(p["manufacturer"]+" / "+p["name"],", ".join(p["categories"]),m["name"],m["footprint"]))
        except Exception as e: messagebox.showerror("Search",str(e))
    def selected(self):
        s=self.results.selection()
        return self.matches[int(s[0])] if s else None
    def details(self,event=None):
        selected=self.selected()
        if not selected: return
        _,p,m=selected
        self.detail.delete("1.0","end")
        self.detail.insert("end","UNVERIFIED PROFILE: "+p["name"]+"\n"+ "\n".join(f"{i+1}: {c}" for i,c in enumerate(m["channels"])))
    def preview_patch(self):
        selected=self.selected()
        if not selected: return
        try:
            _,p,m=selected
            addresses=allocate(self.count.get(),m["footprint"])
            self.detail.delete("1.0","end")
            self.detail.insert("end","PREVIEW ONLY — no output or patch changes\n"+"\n".join(f"Fixture {i+1}: Universe {u}, Address {a}" for i,(u,a) in enumerate(addresses)))
        except Exception as e: messagebox.showerror("Patch preview",str(e))

if __name__=="__main__":
    root=tk.Tk()
    Studio(root)
    root.mainloop()
