/*---------------------------------------------
 * JuMEG Eventcode
 * sending eventcodes (TTL signals) as digital markers to MEG/EEG system
 * using  Arduino MEGA 
 * --------------------------------------------
 * @author   F.Boers (f.boers@fz-juelich.de)
 * FZJ-INM4-MEG
 * --- v1.00  05.2017
 * update 19.08.2017  
 * --- v1.01  19.10.2017
 * update 05.12.2017 
 * add button for sending startcode manually
 * --- v1.02 23.02.2018
 * update 23.02.2018 
 * bug fixes
 *---------------------------------------------
 * TTL Output 16bit
 * 4D MEG system first  8bit labeld as eventcode 0-255
 * 4D MEG system second 8bit labeld as triggercode 256 - X00FF
 * eventcode 0-255 
 * ---> Port C0-7  Pin 37,36,35,34,33,32,31,30
 * triggercode 256 -X00FF 
 * --->Port A Pin 22,23,24,25,26,27,28,29 
 *  
 * dependencies:
 * Timer5 and micros()
 * DirectIO for sending 16bit event and trigger code; 
 *  
 *----------------------------------------------
 *  Start Code Button
 *  use Pin 4 
 *  conncet +5V via Button --> Pin4 and 10k-> GRND
 *----------------------------------------------
* example:
  switch-on eventcode for limited time:
  send byte code via usb port:  7 byte array
  e.g.: 111,255,1,b0,b1,b2,b3   -> b0-b3: duration
  
  -> present TTL eventcode 255+256 for 1024 ms
     111,255,1,0,3,0,0  
  -> present eventcode "forever" arduino is running or recived different switch on/off commnad
     111,255,2,0,b0,b1,b2,b3
   
  switch-off eventcode
  -> send command via usb programmer port: 112,0
     will switch off TTL eventcode set to zero

  sending sequence of event [1,2,4] and trigger codes [5,6,7] for 1024ms each
     211,12,0,3,0,0,1,0,2,0,4,0,0,5,0,6,0,7
     211: cmd 
     12: number of bytes
     last 4 bytes duration in ms

  checking for vendor id for getting the correct arduino connection:
  e.g /dev/ttyACM[0...N]???
     123,123,123,123,123,123,123,0
     return 123 
 *--------------------------------------------- 
*/
  

char data_buffer[122] = {};      

#include <TimerFive.h>
#include <DirectIO.h>

#define BAUDRATE 115200
#define TIMER5_INTERVALL_US 200
#define SEQ_MAX_DATA_COUNTS 122

#define START_CODE 128
#define START_CODE_DURATION_MS 200;

#define PIN_START_CODE 4 // pin connected to front panel button to send event start code (eg.128)
#define PIN_STATUS 5     // switch on LED during sending event/trigger code

bool startcode_isOn=false;

//-- TRIGGER CODE use MEGA Port A  8-bit pin 22,23,24,25,26,27,28,29
//-- EVENT CODE   use MEGA Port C  8-bit pin 37,36,35,34,33,32,31,30

/*----------------------------------------------------- 
 * serial command code 
 * to send event codes 8bit/TTL
 *----------------------------------------------------- 
 * present trigger code
 *----------------------------------------------------- 
 * switch on  event code : 111,code,duration,0
 * switch off event code : 112,0
 *-----------------------------------------------------
 * SendSeq
 *----------------------------------------------------- 
 * send code/trigger seq (16bit) : 
 * 211,data_counts,duration,code[0],trigger[0],code[1],trigger[1],...,code[data_counts-1],trigger[data_counts-1]
 *-----------------------------------------------------
 * switch off event code : 112,0
 *----------------------------------------------------- 
*/
 
//--- serial comunication 
struct CMD_KEYS{
//--- present  
static const uint8_t eventcode_switch_on  = 111;
static const uint8_t eventcode_switch_off = 112;
static const uint8_t eventcode_vendor_id  = 123;
static const uint8_t eventcode_seq        = 211;
};

static const CMD_KEYS CmdKeys;

//-------------------------------------------------------
// EventCode Class
//-------------------------------------------------------
class EventCode{
 
 //--- Class Member Variables
 //--- These are initialized at startup
 
  volatile unsigned long  _time_end;   // end time of eventcode 
  
//--- init DirectIO Event Ccode ports C; 
  OutputPort<PORT_C> _portEVENT_CODE; 
//--- init DirectIO Trigger Code ports A;
  OutputPort<PORT_A> _portTRIGGER_CODE;

 public:
  uint8_t     eventcode;      // eventcode
  uint8_t     triggercode;    // triggercode
  uint16_t    clear_code;     // code to clear all 8 event and 3 trigger bits
  
  unsigned long duration;   // duration of eventcode 0-> forever
  volatile bool isOn;       // milliseconds of off-time
  bool          verbose;    // e.g. print info
         
 //--- Constructor - creates a EventCode 
 //--- and initializes the member variables and state
 
  EventCode(){
     _time_end   = 0;
   
     eventcode   = 0; // -> connceted to trigger bit 0-7
     triggercode = 0; // -> connceted to trigger bit 8-15
     clear_code  = 0;
     duration    = 0;
     isOn        = false; 

    }// end of EventCode
 
  void SwitchOn(){
       unsigned long combined_code = eventcode + (triggercode<< 11); //<<12
        
       _portEVENT_CODE   = eventcode;   // set eventcode bit0-7
       _portTRIGGER_CODE = triggercode; // set trigger code/bits
       
       _time_end    = (unsigned long) micros() + duration * 1000;
       isOn         = true;
       digitalWrite(PIN_STATUS,HIGH);
       //Serial.print("-> ON: ");
       //Serial.println(code);
   }// end of SwitchOn
   
  void Update(){
    if ( ( isOn == true ) &&( duration >0 ) )
     { 
      if ( (unsigned long) micros() > (unsigned long)_time_end )
        { SwitchOff(); }
     } // else if isOn
   }// end of Update

  void SwitchOff(){
     _portEVENT_CODE   = clear_code ;  // set eventcode bit0-7
     _portTRIGGER_CODE = clear_code ;  // set trigger code/bits
     _time_end         = 0;
     isOn              = false; 
     digitalWrite(PIN_STATUS,LOW);
    // Serial.println("OFF");
   } // end of SwitchOff

};// end of EventCode cls


//-------------------------------------------------------
// EventCodeSeq Class
//-------------------------------------------------------
class EventCodeSeq{
 
//--- Class Member Variables
//--- These are initialized at startup
 
   volatile unsigned long  _time_end;   // end time of eventcode 
  
//--- init DirectIO Event Ccode ports C; 
   OutputPort<PORT_C> _portEVENT_CODE; 
//--- init DirectIO Trigger Code ports A;
   OutputPort<PORT_A> _portTRIGGER_CODE;

public:
  uint16_t    clear_code;     // code to clear all 8 event and 3 trigger bits
  
  unsigned long duration;    // duration of eventcode 0-> forever
  unsigned long default_duration; // duration of eventcode 0-> forever
  unsigned long data_counts;      // number of seq code (event and trigger)
  
  volatile unsigned long data_index;// index in buffer
  volatile bool isOn;          // milliseconds of off-time
  bool          mode;          // mode true -> seq mode  

  char data[SEQ_MAX_DATA_COUNTS]= {};
       

 EventCodeSeq(){
     _time_end   = 0;   
     clear_code  = 0;
     duration    = 0;
     default_duration = 15;
     isOn        = false; 
     data[SEQ_MAX_DATA_COUNTS] = {};
     data_index  = 0;
     data_counts = 0;
     
    }// end of EventCode

 void SendSEQ(){
       // unsigned long combined_code = data[data_index] + (data[++data_index]<< 11); //<<12
       if ( data_index + 1 < data_counts){ 
           _portEVENT_CODE   = data[data_index];   // set eventcode bit0-7
           data_index++;
           _portTRIGGER_CODE = data[data_index];  // set trigger code/bits
           _time_end    = (unsigned long) micros() + duration * 1000;
           isOn         = true;
           digitalWrite(PIN_STATUS,HIGH);
           data_index++;
           }
       else{
            Reset();
           }       
  }// end of SendSEQ
   
  void Update(){
    if ( ( isOn == true ) &&( duration >0 ) )
     { 
      if ( (unsigned long) micros() > (unsigned long)_time_end )
        { SendSEQ(); }
     } // else if isOn
     
   }// end of Update

  void Reset(){
     _portEVENT_CODE   = clear_code ;  // set eventcode bit0-7
     _portTRIGGER_CODE = clear_code ;  // set trigger code/bits
     _time_end         = 0;
     isOn              = false; 
     data_counts       = 0;
     data_index        = 0;
     digitalWrite(PIN_STATUS,LOW);
    // Serial.println("OFF");
   } // end of reset_seq

};// end of EventCodeSeq cls



//--- init eventcode class
EventCode    eventcode;
EventCodeSeq eventcode_seq;

void EventCodeHandler(){
  if (eventcode_seq.isOn==true)
     { eventcode_seq.Update(); }
  else{ eventcode.Update(); }
  }


//-------------------------------------------------------------
// setup
//---------------------------------------------------------------
void setup() {


 Serial.begin(BAUDRATE);
 Serial.flush();
 pinMode(PIN_START_CODE,INPUT);
 pinMode(PIN_STATUS,OUTPUT);
 
//--- Timer5  
 Timer5.initialize(TIMER5_INTERVALL_US);  // initialize timer5
 Timer5.disablePwm(44);
 Timer5.disablePwm(45);
 Timer5.disablePwm(46);
 Timer5.attachInterrupt( EventCodeHandler ); 
} // end of setup

//---------------------------------------------
// MAIN LOOP  
//---------------------------------------------
void loop() {
     if (digitalRead( PIN_START_CODE ) and (!eventcode.isOn))
        { send_start_code(); }
     check_serialEvent();// e.g use with IRQ
     //eventcode.Update(); // use with Timer5 IRQ
      
} // end of loop

//---------------------------------------------
// send_start_code  
//---------------------------------------------
void send_start_code(){
     eventcode.eventcode   = START_CODE;
     eventcode.triggercode = 0;
     eventcode.duration    = START_CODE_DURATION_MS;
     eventcode.SwitchOn();
}        

//---------------------------------------------
// check_serialEvents  
//---------------------------------------------
void check_serialEvent(){
uint8_t cmd;
uint8_t i;
bool VENDOR_ID_REQUEST;

while ( Serial.available() >=7 )
 {  
   cmd = Serial.read();

   switch( cmd ){
     
      case CmdKeys.eventcode_switch_on : // 111,255,255,dtD0,dtD1,dtD2,dtD3
           eventcode.eventcode     = Serial.read();
           eventcode.triggercode   = Serial.read();
           eventcode.duration      = 0;
           for(i=0;i<4;i++){eventcode.duration |= ((unsigned long) Serial.read() << (i*8));}
           eventcode.SwitchOn();
           break;
           
      case CmdKeys.eventcode_switch_off : // 112,0,0,0,0,0,0
           eventcode.SwitchOff();
           break;
           
      case CmdKeys.eventcode_vendor_id:// 123,123,123,123,123,123,123,0
           VENDOR_ID_REQUEST=true;
           for (i=1;i<6;i++)
             {
               if ( CmdKeys.eventcode_vendor_id != Serial.read())
                  { Serial.println(99);  VENDOR_ID_REQUEST=false;break;}
             } // for                     
           if ( VENDOR_ID_REQUEST== true){ Serial.println(CmdKeys.eventcode_vendor_id);delay(1000); }
           break;
      
      case CmdKeys.eventcode_seq: //211,10,0,0,0,0,1,0,2,0,3,0,4,0,5,0
           eventcode_seq.Reset();
           eventcode_seq.data_counts = Serial.read(); // max 128
           Serial.read(); // dummy 
           for(i=0;i<4;i++){eventcode_seq.duration |= ((unsigned long) Serial.read() << (i*8));}
          
           if (eventcode_seq.data_counts > SEQ_MAX_DATA_COUNTS )
              { eventcode_seq.data_counts = SEQ_MAX_DATA_COUNTS;}
           Serial.readBytes( eventcode_seq.data, eventcode_seq.data_counts); 
          
           if (eventcode_seq.duration == 0 )
            { eventcode_seq.duration = eventcode_seq.default_duration;}
           
           eventcode_seq.SendSEQ();
           break;
           
     } // end switch
     
     Serial.flush();
   }// while serial
}// end of check_serialEvent


