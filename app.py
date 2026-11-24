import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket, struct, json, time, math

class Engine:
    def __init__(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); self.serial=None; self.seq=0
    def send(self, frames, mode, host, base):
        for i, frame in enumerate(frames):
            if mode=='Art-Net':
                self.seq=self.seq%255+1
                packet=b'Art-Net\0'+struct.pack('<H',0x5000)+struct.pack('>H',14)+bytes([self.seq,0])+struct.pack('<H',base+i)+struct.pack('>H',512)+frame
                self.sock.sendto(packet,(host,6454))
            elif mode=='ENTTEC USB Pro' and i==0:
                data=b'\0'+frame; self.serial.write(b'\x7e\x06'+struct.pack('<H',len(data))+data+b'\xe7')
    def close(self):
        if self.serial: self.serial.close(); self.serial=None

class App:
    def __init__(self, root):
        self.r=root; root.title('Pulse Lighting Pro | 0.1'); root.geometry('1000x740'); self.engine=Engine(); self.armed=False; self.black=True; self.scenes={}; self.fixtures=[]; self.start=time.monotonic()
        self.mode=tk.StringVar(value='Simulation'); self.host=tk.StringVar(value='127.0.0.1'); self.base=tk.IntVar(value=0); self.port=tk.StringVar(); self.effect=tk.StringVar(value='Static'); self.status=tk.StringVar(value='Simulation — output disarmed'); self.count=tk.IntVar(value=32); self.width=tk.IntVar(value=12)
        self.values={k:tk.IntVar(value=v) for k,v in [('Pan',128),('Tilt',128),('Dimmer',0),('Red',255),('Green',255),('Blue',255),('White',0)]}; self.mapping={k:tk.IntVar(value=0) for k in self.values}
        top=ttk.Frame(root,padding=10); top.pack(fill='x'); ttk.Label(top,text='PULSE LIGHTING PRO',font=('Arial',22,'bold')).pack(side='left'); ttk.Button(top,text='BLACKOUT',command=self.blackout).pack(side='right'); ttk.Button(top,text='Restore',command=self.restore).pack(side='right')
        tabs=ttk.Notebook(root); tabs.pack(fill='both',expand=True,padx=10); live=ttk.Frame(tabs,padding=12); patch=ttk.Frame(tabs,padding=12); out=ttk.Frame(tabs,padding=12); tabs.add(live,text='Live control'); tabs.add(patch,text='Fixture patch'); tabs.add(out,text='Output / integrations')
        self.canvas=tk.Canvas(live,height=190,bg='#111827',highlightthickness=0); self.canvas.pack(fill='x'); controls=ttk.Frame(live); controls.pack(fill='x');
        for i,(k,v) in enumerate(self.values.items()):
            f=ttk.Frame(controls); f.grid(row=0,column=i,sticky='nsew'); controls.columnconfigure(i,weight=1); ttk.Label(f,text=k).pack(); tk.Scale(f,from_=255,to=0,variable=v,length=170).pack()
        ttk.Combobox(live,textvariable=self.effect,values=['Static','Slow sweep','Circle'],state='readonly').pack(anchor='w'); self.scene=tk.StringVar(); row=ttk.Frame(live); row.pack(fill='x',pady=8); ttk.Entry(row,textvariable=self.scene).pack(side='left'); ttk.Button(row,text='Save scene',command=self.save_scene).pack(side='left'); ttk.Button(row,text='Recall scene',command=self.recall).pack(side='left'); ttk.Button(row,text='Export project',command=self.export).pack(side='left'); ttk.Button(row,text='Import project',command=self.load).pack(side='left')
        ttk.Label(patch,text='Enter verified channel offsets (1-based); 0 = unsupported. No automatic identification in this build.',wraplength=750).pack(anchor='w');
        for label,var in [('Fixture count',self.count),('Channels per fixture',self.width),*self.mapping.items()]:
            f=ttk.Frame(patch); f.pack(fill='x',pady=3); ttk.Label(f,text=label,width=24).pack(side='left'); ttk.Entry(f,textvariable=var,width=8).pack(side='left')
        ttk.Button(patch,text='Apply verified patch',command=self.apply).pack(anchor='w'); self.patchinfo=ttk.Label(patch,text='No verified fixtures patched'); self.patchinfo.pack(anchor='w')
        for label,var in [('Output mode',self.mode),('Art-Net destination IP',self.host),('Art-Net first universe (0-based)',self.base),('ENTTEC serial port',self.port)]:
            f=ttk.Frame(out); f.pack(fill='x',pady=5); ttk.Label(f,text=label,width=34).pack(side='left'); (ttk.Combobox(f,textvariable=var,values=['Simulation','Art-Net','ENTTEC USB Pro'],state='readonly') if var is self.mode else ttk.Entry(f,textvariable=var)).pack(side='left')
        ttk.Button(out,text='Arm physical output',command=self.arm).pack(anchor='w'); ttk.Button(out,text='Disarm',command=self.disarm).pack(anchor='w'); ttk.Label(out,text='Planned: RDM discovery, sACN, MIDI/OSC, ProPresenter, OBS, WING, audio analysis and remote control.',wraplength=700).pack(anchor='w',pady=20); ttk.Label(root,textvariable=self.status).pack(fill='x'); root.protocol('WM_DELETE_WINDOW',self.quit); self.tick()
    def apply(self):
        if self.armed: return messagebox.showerror('Patch','Disarm first')
        try:
            n,w=self.count.get(),self.width.get(); m={k:v.get() for k,v in self.mapping.items()}; used=[v for v in m.values() if v]; assert 1<=n<=256 and 1<=w<=512 and all(0<=v<=w for v in m.values()) and len(set(used))==len(used) and m['Dimmer']>0
            per=512//w; self.fixtures=[(i//per,(i%per)*w,dict(m)) for i in range(n)]; self.patchinfo.config(text=f'{n} fixtures / {self.fixtures[-1][0]+1} universes'); self.black=True
        except Exception: messagebox.showerror('Patch','Invalid mapping. Unique offsets and a verified dimmer channel required.')
    def arm(self):
        if self.armed: return
        try:
            mode=self.mode.get(); assert mode!='Simulation' and self.fixtures; assert 0<=self.base.get()<=32767 and self.base.get()+self.fixtures[-1][0]<=32767
            if mode=='ENTTEC USB Pro':
                assert self.fixtures[-1][0]==0; import serial; self.engine.serial=serial.Serial(self.port.get(),57600,timeout=.1,write_timeout=.1)
            else: socket.inet_aton(self.host.get())
            self.config=(mode,self.host.get(),self.base.get()); self.black=True; self.armed=True; self.status.set('Armed — blackout active')
        except Exception as e: self.engine.close(); messagebox.showerror('Output',str(e) or 'Check patch, universe count and output settings')
    def blackout(self): self.black=True
    def restore(self): self.black=False
    def frames(self):
        frames=[bytearray(512) for _ in range(self.fixtures[-1][0]+1)] if self.fixtures else []; t=time.monotonic()-self.start
        for i,(u,a,m) in enumerate(self.fixtures):
            for k,offset in m.items():
                if not offset: continue
                v=self.values[k].get()
                if self.black and k=='Dimmer': v=0
                if not self.black and self.effect.get()!='Static' and k in ('Pan','Tilt') and (k=='Pan' or self.effect.get()=='Circle'): v=max(0,min(255,int(v+25*math.sin(t*.6+i*.15+(1.57 if k=='Tilt' else 0)))))
                frames[u][a+offset-1]=v
        return frames
    def disarm(self):
        self.black=True
        if self.armed:
            try: self.engine.send(self.frames(),*self.config)
            except Exception as e: self.status.set('Blackout transmission failed: '+str(e))
        self.armed=False; self.engine.close(); self.status.set('Disarmed — verify physical lights')
    def tick(self):
        if self.armed:
            try: self.engine.send(self.frames(),*self.config)
            except Exception as e: self.disarm(); self.status.set('Output error: '+str(e))
        c=self.canvas; c.delete('all'); w=max(300,c.winfo_width()); n=min(len(self.fixtures) or 32,32); rgb='#%02x%02x%02x'%tuple(self.values[k].get() for k in ('Red','Green','Blue'))
        for i in range(n):
            x=(i+.5)*w/n; c.create_oval(x-6,15,x+6,27,fill='#64748b',outline='');
            if not self.black and self.values['Dimmer'].get():
                dx=(self.values['Pan'].get()-128)*.4; c.create_polygon(x,27,x+dx-12,155,x+dx+12,155,fill=rgb,stipple='gray50')
        c.create_text(w/2,177,text='2D SIMULATION — not a calibrated stage view',fill='white'); self.r.after(33,self.tick)
    def save_scene(self):
        if self.scene.get(): self.scenes[self.scene.get()]={'values':{k:v.get() for k,v in self.values.items()},'effect':self.effect.get()}
    def recall(self):
        s=self.scenes.get(self.scene.get());
        if s:
            for k,v in s['values'].items(): self.values[k].set(v)
            self.effect.set(s['effect'])
    def export(self):
        p=filedialog.asksaveasfilename(defaultextension='.json');
        if p:
            with open(p,'w') as f: json.dump({'scenes':self.scenes,'count':self.count.get(),'width':self.width.get(),'mapping':{k:v.get() for k,v in self.mapping.items()}},f,indent=2)
    def load(self):
        if self.armed: return
        p=filedialog.askopenfilename();
        if p:
            try:
                with open(p) as f: d=json.load(f)
                self.count.set(int(d['count'])); self.width.set(int(d['width'])); self.scenes=d['scenes'];
                for k,v in self.mapping.items(): v.set(int(d['mapping'].get(k,0)))
                self.fixtures=[]; self.apply()
            except Exception as e: messagebox.showerror('Import',str(e))
    def quit(self): self.disarm(); self.r.destroy()
if __name__=='__main__':
    root=tk.Tk(); App(root); root.mainloop()
