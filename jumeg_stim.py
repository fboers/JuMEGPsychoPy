#!/usr/bin/env python3


from contextlib import contextmanager
from psychopy import visual, core, event

#--- MEG FB send eventcode ia arduino
from jumeg_psycho_eventcode  import JuMEG_Psycho_EventCode 

__version__="2020-02-11-001"

class JuMEG_Psycho_IOD(object):
    """ Image Onset Detection (IOD)
        white rectangle at the screen bottom left or right
    """
    def __init__(self,**kwargs):
        super().__init__()
        self._win     = None
        self._img     = None
        self._img_back= None
        self._isInit  = False
        self._isOn    = False
       #---
        self.width           = 100.0
        self.height          = 50.0
        self.position        = (0.0,0.0)
        self.unit            = "pix"
        self._auto_position  = "LR"  # Lower Right
        self._auto_positions = ['LR','LL','UR','UL']
       #---
        self.colorSpace = "rgb"
        self.color      = (1.0,1.0,1.0) # -1.0 < > 1.0
        self.color_back = (-1.0,-1.0,-1.0) 
        
       #---
        self._autoDraw    = False
        self.ToggleOffKey = None # "8"
       #---
        self._update_fron_kwargs(**kwargs)
     
   #---
    @property
    def win(self): return self._win
   #---
    @property
    def isInit(self): return self._isInit
   #---
    @property
    def isOn(self): return self._isOn
   #---
    @property
    def auto_position(self): return self._auto_position
    @auto_position.setter
    def auto_position(self,v):
        if v in self._auto_positions:
           self._auto_position = v
    
    @property
    def autoDraw(self): return self._autoDraw
    @autoDraw.setter
    def autoDraw(self,v):
        if self._img:
           self._img.setAutoDraw(v)
           self._autoDraw=v
    
    def _update_fron_kwargs(self,**kwargs):
    
        self._win           = kwargs.get("win",self._win)
    
        self.width          = kwargs.get("width",self.width)
        self.height         = kwargs.get("height",self.height)
        self.position       = kwargs.get("position",self.position)
        self.unit           = kwargs.get("unit",self.unit)
        self.colorSpace     = kwargs.get("iod_colorSpace",self.colorSpace)
        self.color          = kwargs.get("iod_color",self.color)
        
        self._autoDraw      = kwargs.get("autoDraw",self._autoDraw)
        self._auto_position = kwargs.get("auto_position",self._auto_position)
        self.ToggleOffKey   = kwargs.get("ToggleOffKey",self.ToggleOffKey)
        
    def draw(self,autoDraw=True,**kwargs):
        """
        
        :param win:
        :param position:
        :param autoDraw:
        :return:
        """
        if not self._isInit:
           self.init(**kwargs)
        
        self._img_back.setAutoDraw(False)
        
        self._img.setAutoDraw(autoDraw)
        self._img.draw()
        self._isOn = True
        
    def hide(self,autoDraw=True,**kwargs):
        """
         hide IOD: draw with backgroug color
         e.g. black (-1.0,-1.0,-1.0)
        
        :param win:
        :param position:
        :param autoDraw:
        :return:
        """
        if not self._isInit:
           self.init(**kwargs)
        self._img.setAutoDraw(False)
        
        self._img_back.setAutoDraw(autoDraw)
        self._img_back.draw()
        self._isOn = False
       
        
    def _calc_auto_position(self):
        #-- LR
        dy = -2.0
        dh = 2.0
        dx = 2.0
        dw = -2.0
        #--- ypos lower/upper
        if self.auto_position.startswith('U'):
            dy = 2.0
            dh = -2.0
        #--- xpoy left/right
        if self.auto_position.endswith('L'):
            dx = -2.0
            dw = 2.0
        dxpos = self.win.size[0] / dx + (self.width / dw)
        dypos = self.win.size[1] / dy + (self.height / dh)
        self.position = (dxpos,dypos)
        return self.position
    
    def calc_auto_position(self,position=None):
        """
        
        :param position: "LR","LL","UR","UL", (X,Y), None
        
        :return: 
           iod position
        """
        if position:
           if isinstance(position,(str)): 
              if position in self.auto_positions:
                 self.auto_position = position
                 return self._calc_auto_position()
           else:
              self.position = position
        else:  
           self._calc_auto_position()
        return self.position

    def init(self,**kwargs):
        """
        
        :param win:
        :param position:
        :return:
        """
        self._update_fron_kwargs(**kwargs)
        self._isInit = False
        self._isOn   = False
        self.calc_auto_position(position=kwargs.get("position",None))
        
        if not self.win:
           return False
        
        self._img = visual.Rect(self.win,
                                width   = self.width,
                                height  = self.height,
                                units   = self.unit,
                                pos     = self.position,
                                autoDraw= self.autoDraw)
        self._img.lineColor  = self.color
        self._img.fillColor  = self.color
        self._img.colorSpace = self.colorSpace
       #---
        if not self.color_back:
           self.color_back = self.win.color
           
        self._img_back = visual.Rect(self.win,
                                width   = self.width,
                                height  = self.height,
                                units   = self.unit,
                                pos     = self.position,
                                autoDraw= self.autoDraw)
        
        self._img_back.lineColor  = self.color_back
        self._img_back.fillColor  = self.color_back
        self._img_back.colorSpace = self.colorSpace
        
        self._isInit = True
        return True 


class JuMEGStim(object):
    """
     Example
     --------
        from jumeg_stim import JuMEGStim
         
         clock = core.Clock()

         jSTIM = JuMEGStim()
         win   = jSTIM.win
         img   = visual.TextStim(win,text='JuMEG TEST IOD', pos = (0,0), color = (1,1,1), bold=True)
    
        #---draw img with IOD, press <8> to flip
         with jSTIM.present(eventcode=16):
              img.draw()
              img.setAutoDraw(True) # set all AutDraw=True

        #--- wait for stimulus time
         print("---> press one key to exit: {}".format(jSTIM.ExitKeys))
         while True:
               if jSTIM.ExitOnKeyPress():
               return

    
         img.setAutoDraw(False)
         win.flip()

         core.wait( 1.0 )
    
         jSTIM.close()
         core.quit()  
         
    """
    def __init__(self,**kwargs):
        super().__init__()
        self._IOD     = JuMEG_Psycho_IOD(ToggleOffKey="8")
        self._EVC     = JuMEG_Psycho_EventCode()
        self.ExitKeys = ["q","esc","escape"]
        self.clock    = core.Clock()
        self.timeout_sec = 0.50
        self._status     = False
        self.duration_ms = 200
        self._win        = None
        self._size       = [1920,1200]
        self._parameter  = {"monitor":"MEG","units":"pix","fullscr":True,"screen":1,
                            "useFBO":True,"color":(-1.0,-1.0,-1.0)}
        self.init(**kwargs)
   #---
    @property
    def win(self): return self._win
    @property
    def status(self): return self._status
 
    @property
    def size(self): return self._size
    @property
    def parameter(self): return self._parameter
    @property
    def EventCode(self): return self._EVC
    @property
    def IOD(self): return self._IOD
    
    def close(self):
        try:
          self._win.close()
        except:
          print("---> ERROR in JuMEGStim Class => can not close WIN")
          
    def _update_from_kwargs(self,**kwargs):
        """
        

        Parameters
        ----------
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.duration_ms= kwargs.get("duration_ms",self.duration_ms)
        self.timeout_sec= kwargs.get("timeout_sec",self.timeout_sec)
        self._size      = kwargs.get("size",self._size)
        for k in self._parameter.keys():
            self._parameter[k] = kwargs.get(k,self._parameter[k])
            
        
    def ExitOnKeyPress(self):
        """
        True if key pressed <ESC> <q>
        """
        if event.getKeys(self.ExitKeys):
           self._status = False
           return True
        return False

    def _init_win(self,**kwargs):
        """
        size=[1920,1200]
        parameter= {monitor="MonitorINM3",units="deg",fullscr=True,screen=0,useFBO=True,
                                 color=(-1.0,-1.0,-1.0)}


        self._win = visual.Window([1920,1200],monitor="MonitorINM3",units="deg",fullscr=True,screen=0,useFBO=True,
                                 color=(-1.0,-1.0,-1.0))

        :param kwargs:
        :return:
        """
        self._update_from_kwargs(**kwargs)
           
        self._win = visual.Window(self.size,**self.parameter)
        
   #---
    def init(self,**kwargs):
        
        event.clearEvents()
        
        if self.EventCode.open():
           self.EventCode.sendEventCode(eventcode=255,duration_ms=5000)
        if "win" in kwargs:
           self._win = kwargs.get("win")
        else:
           self._init_win(**kwargs)
                
        kwargs["win"] = self.win
        self.IOD.init( **kwargs )
        
        self.IOD.hide()
        self.win.mouseVisible = False
        self.win.flip()
        
        self._status = True
    
    
    def WaitForIODOnScreen(self):
        t0 = self.clock.getTime()
      #--- wait for till image is on screen ...
        keys=[self.IOD.ToggleOffKey]
        keys.extend(self.ExitKeys)
        #pressedKeys = event.waitKeys(maxWait=self.timeout_sec, keyList=keys, modifiers=False, timeStamped=False, clearEvents=False)
     
        pressedKeys = event.waitKeys(maxWait=self.timeout_sec, keyList=keys, modifiers=False, timeStamped=False, clearEvents=False)
        # print("---> wait for pressedKeys: {}".format(pressedKeys))
        if pressedKeys:
          #  print("---> keys: {}".format(pressedKeys))
           if self.IOD.ToggleOffKey not in pressedKeys:
              print("---> <WaitForIODOnScreen> key pressed: {}".format(pressedKeys))
              self._status = False
        else:
           print("---> TimeOut")
        
    def WaitForSec(self,twait,tstart=None):
        """
        

        Parameters
        ----------
        twait : TYPE
            DESCRIPTION.n time to wait in sec
            
        tstart: start time <None>
        
        Returns
        -------
        bool
            DESCRIPTION.

        """
        if not tstart:
           tstart = self.clock.getTime()
        while True:
              if (self.clock.getTime() - tstart > twait):
                 return True
              if self.ExitOnKeyPress():     
                 return False
              if not self.status:
                 return False
            
    @contextmanager
    def present(self,eventcode=None,duration_ms=200,wait=None):
        """   

        Parameters
        ----------
        eventcode : TYPE, optional
            DESCRIPTION. The default is None.
        duration_ms : TYPE, optional
            DESCRIPTION. The default is 200.
        wait : TYPE, optional
            DESCRIPTION. The default is None.
        finalflip : TYPE, optional
            DESCRIPTION. The default is True.

        Yields
        ------
        TYPE
            DESCRIPTION.

       
        Example
        --------
         from jumeg_stim import JuMEGStim
         
         clock = core.Clock()

         jSTIM = JuMEGStim()
         win   = jSTIM.win
         img   = visual.TextStim(win,text='JuMEG TEST IOD', pos = (0,0), color = (1,1,1), bold=True)
    
        #---draw img with IOD, press <8> to flip
         with jSTIM.present(eventcode=16):
              img.draw()
              img.setAutoDraw(True) # set all AutDraw=True

        #--- wait for stimulus time
         print("---> press one key to exit: {}".format(jSTIM.ExitKeys))
         while True:
               if jSTIM.ExitOnKeyPress():
               return

         img.setAutoDraw(False)
         win.flip()

         core.wait( 1.0 )
    
         jSTIM.close()
         core.quit()
       
        """
                
        event.clearEvents()
        
        yield # do your stuff here
        
        self.IOD.draw(autoDraw=True)
        if eventcode:
           # print(" --> sending eventcode:  {}".format(eventcode) )
           self.EventCode.sendEventCode(eventcode=eventcode,duration_ms=self.duration_ms)
           
        self.win.flip() # show images & IOD pattern
        t0 = self.clock.getTime()
        self.WaitForIODOnScreen()
        
        self.IOD.hide() # draw IOD pattern in black
        
        self.win.flip() # remove IOD pattern
      
        if wait:
           self.WaitForSec(wait,tstart=t0)
          
            
def test():   
    """ run test """         
    clock = core.Clock()

    jSTIM = JuMEGStim()
    win   = jSTIM.win  
    
    info      = "JuMEG Test IOD       Hide IOD: <8>      Quit: <q>"
    txt_param = {"pos":(0.0,0.0),"color":(1,1,1),"bold":True,"units":"pix","height":40.0,"wrapWidth":450}   
    img       = visual.TextStim(win,text=info, **txt_param)
    code_img  = 16
    
    fix       = visual.TextStim(win,text='+',  **txt_param)
    code_fix  = 32
    
    #jSTIM.EventCode.sendEventCode(eventcode=255,duration_ms=1000)
  
   #--- wait for stimulus time
    print("---> press one key to exit: {}".format(jSTIM.ExitKeys))
    
    event.clearEvents()
    
   #---draw img with IOD, press <8> to flip
    while jSTIM.status:
          with jSTIM.present(eventcode=code_img,wait=2.0):
               img.draw()
               img.setAutoDraw(True) # set all AutDraw=True
          
          if not jSTIM.status: break
          
          img.setAutoDraw(False)
          with jSTIM.present(eventcode=code_fix,wait=1.0):
               fix.draw()
               fix.setAutoDraw(True) # set all AutDraw=True
          fix.setAutoDraw(False) # set all AutDraw=True

    
    img.setAutoDraw(False)
    win.flip()

    core.wait( 1.0 )
    
    jSTIM.close()
    core.quit()

if __name__ =="__main__":
   test()
 
