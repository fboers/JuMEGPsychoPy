#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 10:49:29 2017
@author: fboers
update 11.12.2020 for py3, fb
"""

from warnings import warn
import os,time,glob,serial
import numpy as np

__version__='2020-02-11-001'

class JuMEG_Psycho_EventCode(object):
      def __init__(self,port='/dev/ttyACM0',baudrate=115200,startcode=128,duration_ms=200,duration_seq_ms=10,verbose=False):
          """ 
          sending digital eventcodes (TTL) via Arduino (MEGA)
          default setings (LINUX):
                  baudrate    = 115200
                  duration_ms = 200
                  startcode   = 128
                  port        = '/dev/ttyACM0'
           -> will find arduino port via VENDOR_ID_CODE (123)
              https://github.com/wiseman/arduino-serial/blob/master/arduinoserial.py
              https://github.com/vascop/Python-Arduino-Proto-API-v2/blob/master/arduino/arduino.py

          Example:
          --------
          # psychopy
          
          from psychopy import core, event, clock
          from psychopy.hardware import keyboard

          from jumeg_psycho_eventcode  import JuMEG_Psycho_EventCode 
          evc = JuMEG_Psycho_EventCode (verbose=True)
          
          defaultKeyboard = keyboard.Keyboard()

          t     = 10.0 # s
          tms   = 10000
          code  = 255
          twait = True
          clk   = core.Clock()
          timer = core.CountdownTimer()
  
          if evc.open():
             print("---> start  sending eventcode: {} for {} s\n  -> press <Esc> to quit".format(code,t))
             evc.sendEventCode(eventcode=code,duration_ms=tms)
   
             timer.add(t)
   
             while twait and timer.getTime() > 0:
                   if defaultKeyboard.getKeys(keyList=["escape"]):
                      twait = False

             print("---> done sending eventcode: {} s".format(t))

          else:
             print("---> ERROR can not send eventcode")
          core.quit()
          """

          self.__baudrate_list=( ['9600','19200','38400','57600','115200','230400','500000','576000','921600','1000000','1152000',
                                  '1500000','2000000','2500000','3000000','3500000','4000000'])
          self.__comport_list = []

          #--- parameter
          self.__param={
                        'ComPort':port,'baudrate':baudrate,'port_pattern':'/dev/ttyACM[0-9]*',
                        'find_port':True,
                        'duration_ms':duration_ms,'duration_seq_ms':duration_seq_ms,'startcode':startcode, 
                        'vendor_id_code':123,'vendor_id_repetition':7,
                        'send_byte_code':True,'verbose': verbose,
                        'cmd_code_switch_on' : 111,
                        'cmd_code_switch_off': 112,
                        'cmd_code_send_seq'  : 211,
                        'test_seq_code'      : '211,1000,255,128,64,32,16,8,4,2,1,2048,1024,512,256'
                       }

          self.__serial     = None
          self.__byte_array_size = 7
          self.verbose      = False
          
          self.__isConnected= False
         
            
      def __str__(self):
          return "Arduino is on port %s at %d baudrate" %(self.ComPort,self.serial.baudrate)

      def __del__(self):
          if self.isConnected:
             self.close()  
    
     #--- Getter / Setter / Properties
      @property             
      def baudrate_list(self): return self.__baudrate_list
     #---  
      @property
      def comport_list(self):
          self.__comport_list = glob.glob( self.port_pattern )   
          print(" --> checking ports for Arduino-Event/Trigger-Code: ")
          print(" --> port pattern: " +self.port_pattern)
          print(" --> ports: {}\n".forma(self.__comport_list))
          return self.__comport_list
     #---
      @property
      def isConnected(self): return self.__isConnected
     #---  
      @property
      def parameter(self): return self.__param     
      @parameter.setter
      def parameter(self,v):
          self.__param=v     
     #---
      @property 
      def serial(self): return self.__serial
     #---
      @property
      def ComPort(self): return self.__param['ComPort']
      @ComPort.setter
      def ComPort(self,v):
          self.__param['ComPort']=v
     #---
      @property
      def port_pattern(self): return self.__param['port_pattern']
      @port_pattern.setter
      def port_pattern(self,v):
          self.__param['port_pattern']=v      
     #---
      @property    
      def baudrate(self): return self.__param['baudrate']
      @baudrate.setter  
      def baudrate(self,v):
          self.__param['baudrate']=v     
     #---
      @property    
      def duration_ms(self): return self.__param['duration_ms']
      @duration_ms.setter
      def duration_ms(self,v):
          self.__param['duration_ms']=v      
     #---
      @property    
      def duration_seq_ms(self):
          return self.__param['duration_seq_ms']
      @duration_seq_ms.setter
      def duration_seq_ms(self,v):
          self.__param['duration_seq_ms']=v      
     #---
      @property
      def startcode(self):
          return self.__param['startcode']
      @startcode.setter
      def startcode(self,v):
          self.__param['startcode']=v
     #---
      @property    
      def vendor_id_code(self): return self.__param['vendor_id_code']
      @vendor_id_code.setter
      def vendor_id_code(self,v):
          self.__param['vendor_id_code']=v
     #---
      @property
      def vendor_id_repetition(self): return self.__param['vendor_id_repetition']
      @vendor_id_repetition.setter 
      def vendor_id_repetition(self,v):
          self.__param['vendor_id_repetition']=v
     #---
      @property
      def send_byte_code(self): return self.__param['send_byte_code']
      @send_byte_code.setter
      def send_byte_code(self,v):
          self.__param['send_byte_code']=v      
     #---
      @property
      def cmd_code_switch_on(self): return self.__param['cmd_code_switch_on']
      @cmd_code_switch_on.setter
      def cmd_code_switch_on(self,v):
          self.__param['cmd_code_switch_on']=v      
     #---
      @property
      def cmd_code_switch_off(self): return self.__param['cmd_code_switch_off']   
      @cmd_code_switch_off.setter
      def cmd_code_switch_off(self,v):
          self.__param['cmd_code_switch_off']=v
     #---     
      @property
      def cmd_code_send_seq(self): return self.__param['cmd_code_send_seq']
      @cmd_code_send_seq.setter
      def cmd_code_send_seq(self,v):
          self.__param['cmd_code_send_seq']=v
     #---
      @property
      def verbose(self): return self.__param['verbose']
      @verbose.setter
      def verbose(self,v):
          self.__param['verbose']=v
     #---
      @property
      def test_seq_code(self): return self.__param['test_seq_code']
      @test_seq_code.setter
      def test_seq_code(self,v):
          self.__param['test_seq_code']=v
     #---
      @property
      def find_port(self): return self.__param['find_port']
      @find_port.setter
      def find_port(self,v):
          self.__param['find_port']=v  
     #---  
      @property  
      def vendor_id_code_array(self):
          return np.zeros( self.vendor_id_repetition,dtype=np.byte)+self.vendor_id_code
       
    #----------------    
      def __open(self,port=None,baudrate=None):
          if port:
             self.ComPort = port     
          if baudrate:
             self.baudrate = baudrate     
          print("---> Open: Event/Trigger Code connection ...")
          print(' --> Arduino start open connection')
          print('  -> port: ' + self.ComPort + ' baudrate: '+ str(self.baudrate))
          self.__close_comport()
          self.__isConnected=False 
          try:
              self.__serial = serial.Serial(self.ComPort,int(self.baudrate))       
              time.sleep(2)
              if self.__serial:
                 self.__isConnected=True
              print('---> done Arduino is connected: {}\n'.format(self.isConnected))
          except:
              warn('---> EEROR can not connected to Arduino port: {} !!!\n'.format(port))
              
          return self.__isConnected
      
      def open(self,port=None,baudrate=None):
          if port:
             self.ComPort = port     
          if baudrate:
             self.baudrate = baudrate 
          if self.find_port:
              self.findArduinoPort()
          else:   
             self.__open()
             
          if self.isConnected:
             self.serial.flushInput()
             self.serial.flushOutput()
             self.sendSwitchOff() 
          return self.isConnected

      def __close_comport(self):
          try:
              if self.isConnected:
                 self.sendSwitchOff() 
                 time.sleep(1)
                 self.serial.close()
                 time.sleep(1)
                 self.__isConnected = False
                 print('---> done Arduino connection closed\n'          )
          except:
                 self.__isConnected = False
                 
      def close(self):
          print("---> Close: Event/Trigger Code connection ...")
          print(" --> Arduino closing connection ...")
          self.__close_comport()
        
      def getIdCode(self):
          """ 
              check if <event/trigger code arduino> is connected to the port
              return arduino vendor id e.g: 123 for 7 times
          """ 
          self.write_bytes( bytearray( self.vendor_id_code_array ) ) 
          time.sleep(1)
          id = self.serial.readline()
          time.sleep(1)
          self.serial.flushOutput()
          if self.verbose:
             print( " -->ID code : %d"%(int(id)) )
          return int(id)
       
      def findArduinoPort(self):
          ports = glob.glob( self.port_pattern )   
          print(" --> Find Arduino Port Event/Trigger-Code: ")
          print(" --> checking ports ...")
          print(" --> ports:  {}".format(ports))
          
          for port in ports:
              print("\n ---> " +port)
              try:
                  self.__open(port=port)
                  self.serial.timeout=1.0
                  if self.isConnected:
                     id = self.getIdCode()
                     if ( id == self.vendor_id_code ):
                        print(" --> found Arduino@Port: " + self.ComPort +" -> Vendor ID: %d" %(id))
                        self.serial.timeout=None
                        return self.ComPort
                     else:
                        self.close() 
              except:
                 self.__isConnected = False
                 warn('!!! ---> ERROR in connecting to port: '+ port )
          return self.isConnected
         
      def write_bytes(self,v):
          if self.__isConnected:
           # d=bytes(bytearray([111,255,255,0,0,0,0])  
             self.serial.write(bytes(v))
             self.serial.flushOutput()
          else:
             warn("  -> ERROR write bytes to Arduino => Serial conncetion is closed\n")
             
      def number2byte( self,v ):
          """ 
             input  : int
             output : numpy byte array size:4 
             example: 2048+255 => [255,8,0,0]
          """   
          b  = np.zeros(4,dtype=np.uint8)
          mask = np.uint8(255)
          b[0] = v & mask
          b[1] = (v >>  8) & mask
          b[2] = (v >> 16) & mask
          b[3] = (v >> 24) & mask
          return b
      
      def send(self,eventcode=0,duration_ms=-1): 
           
          if not eventcode:
             eventcode = 0
             
          if duration_ms ==-1:
             duration_ms = self.duration_ms 
         #--- send as byte 
          if self.send_byte_code:
             db      = np.zeros( self.__byte_array_size,dtype=np.uint8)
             db[0]   = self.cmd_code_switch_on
             db[1:3] = self.number2byte(eventcode)[0:2]
             db[3:]  = self.number2byte(duration_ms)
             #print "test"
             #print db
            #db=bytes(bytearray([111,255,255,0,0,0,0])
             self.write_bytes( bytearray( db ) )
             if self.verbose:
                print("---> DONE Send: ")
                print("  -> eventcode %d" % (eventcode))
                print("  -> duration [ms] %d" % (duration_ms))
                #print bytearray(db)
                print("\n")
          else:
         #--- send as string  no bytearray(t implemented !!!! 
             warn(" --> Warning Arduino setup can only read bytes!!!\n")
              # self.write( self.__SWITCH_ON_CODE_STR+','+str(eventcode)+','+str(duration_ms) + ',0' )
              
      def sendEventCode(self,eventcode=0,duration_ms=-1) :
          self.send(eventcode=eventcode,duration_ms=duration_ms)
          
      def sendSeq(self,seq=None,duration_seq_ms=-1):
          '''
          send event code seq 
          cmd,number of codes, codes low,high byte .., duration 2 byte
          '''
          if not seq:
              return
          
          if duration_seq_ms ==-1:
             duration_seq_ms = self.duration_seq_ms 
     #--- send as byte 
          if self.send_byte_code:
            #--- arduino 7 byte offset for usual cmds 
             mask     = np.uint8(255)
             seq_ar   = np.array([seq],dtype=np.int).flatten()
             cnt      = len(seq)
             db       = np.zeros(7 + cnt*2,dtype=np.uint8)
             db[0]    = self.cmd_code_send_seq
             db[1]    = np.uint8(cnt*2) # 2 x cnt -> Low/High bytes->Eventcode & Trigger             
             db[3:7]  = self.number2byte( duration_seq_ms) # 6,7 = 0
             db[7::2] = seq_ar & mask 
             db[8::2] = (seq_ar >> 8 ) & mask
           
             self.write_bytes( bytearray(db) ) 
             if self.verbose:
                print("---> DONE send SEQ: ")
                print( seq )            
                print (db  )           
                print("\n")
           
      def sendCmdList(self,cmd_str):
          print(" --> send cmd list:")
          print("  -> "+ cmd_str)
          cmd = [int(i) for i in cmd_str.split(',')]
          if cmd[0] == self.cmd_code_switch_on:
             dt=-1
             if len(cmd)>2: 
                dt=cmd[2]
             self.send(eventcode=cmd[1],duration_ms=dt)
          elif cmd[0] == self.cmd_code_send_seq:
             self.sendSeq(seq=cmd[2:],duration_seq_ms=cmd[1])
            
          elif cmd[0] == self.cmd_code_switch_off:
             self.sendSwitchOff()        
         
      def sendStartCode(self,startcode=None,duration_ms=-1):
          if not startcode:
             startcode=self.startcode 
          self.send(eventcode=startcode,duration_ms=duration_ms) 
          if self.verbose:
             print( " --> DONE send start code: %d" %(startcode)   )
        
      def sendTestSEQCode(self,code=None,trigger=None,duration_ms=0):
          self.sendCmdList( str(self.cmd_code_send_seq) +','+ self.test_seq_code )
        
          if self.verbose:
             print (" --> DONE send Test SEQ Code: " +self.test_seq_code    )
         
      def sendSwitchOff(self):
          """https://stackoverflow.com/questions/31975356/python-arduino-serial-communication"""
          self.write_bytes(bytearray([self.cmd_code_switch_off,0,0,0,0,0,0]) )           
          if self.verbose:
             print( " --> DONE send StopCode & switch off"   )
      def sendStopCode(self):
          self.sendSwitchOff()   

if __name__ == "__main__":
    import time
    evc   = JuMEG_Psycho_EventCode(verbose=True)
    t     = 10.0 # s
    tms   = 10000
    code  = 255
      
    if evc.open():
       print("---> start  sending eventcode: {} for {} s\n  -> press <Esc> to quit".format(code,t))

       evc.sendEventCode(eventcode=255,duration_ms=tms)
       time.sleep(t)

       print("---> done sending eventcode ")

    else:
       warn("---> ERROR can not send eventcode")


'''
ipy test
from psycho.hardware.jumeg_psycho_eventcode import JuMEG_Psycho_EventCode
evc=JuMEG_Psycho_EventCode()
evc.findArduinoPort()
import serial
com=serial.Serial('/dev/ttyACM0',115200)
com.flush()
-> send code trigger:255 response:255
don=bytes(bytearray([111,255,255,0,0,0,0]))
com.write(don)
-> switch off
doff=bytes(bytearray([112,0,0,0,0,0,0]))
com.write(doff)
-> vendor id
vid=bytes(bytearray([123,123,123,123,123,123,123]))
com.write(vid)
com.readline()
-> out : '123\r\n'
id=np.zeros(7,dtype=np.byte)+123
bvid=bytes(bytearray(id))
com.write(bvid)
com.readline()
-> out : '123\r\n'
'''
