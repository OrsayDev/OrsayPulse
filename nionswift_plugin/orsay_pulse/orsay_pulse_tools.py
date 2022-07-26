__author__ = "Yves Auad"
import numpy
import logging
from nion.utils import Event
import time
import threading

TIME_WAIT = 2

class PulseTools:
    def __init__(self):
        logging.info('Init OK.')
        self.__keithley_inst = Keithley(False)
        self.__arduino_inst = Arduino(False)
        self.__osc = Oscilloscope()
        self.__agi = Agilent(False)
        # self.__close = close_port_com
        
        self.property_changed_event = Event.Event()
        
        self.progress_percentage = 0
        self.__resistance_avg = 0
        self.__resistance_avg2 = 0
        self.__avg = 1
        self.pulse_width = 5 #in ms
        self.pulse_tension = 8 #in volts
        
    def progress_bar_loop(self, increment):
        for x in range(increment):
            self.progress_percentage += 1
            time.sleep(0.005)

    def pulse(self):
        threading.Thread(target=self.pulse_start, args=(),).start()

    def pulse_start(self):
        self.progress_percentage = 0
        #self.progress_percentage += 20
        self.progress_bar_loop(20)
        self.resistance_average = self.__keithley_inst.get_values(self.__avg)[0]
        #self.progress_percentage += 15
        self.progress_bar_loop(15)
        self.__arduino_inst.trigger_impulsion()
        #self.progress_percentage += 15
        self.progress_bar_loop(15)
        time.sleep(TIME_WAIT)
        #self.progress_percentage += 15
        self.progress_bar_loop(15)
        self.__arduino_inst.change_state(True)
        #self.progress_percentage += 15
        self.progress_bar_loop(15)
        self.resistance_average2 = self.__keithley_inst.get_values(self.__avg)[0]
        #self.progress_percentage = 95
        self.progress_bar_loop(20)
        self.__arduino_inst.reset()
        #self.progress_percentage = 100
        # self.__close.close_agilent(True)
        # self.__close.close_arduino(True)
        # self.__close.close_keithley(True)
        return None
    
    def resistance(self):
        threading.Thread(target=self.resistance_start, args=(),).start()
  
    
    def resistance_start(self):
        self.progress_percentage = 0
        self.progress_bar_loop(30)
        self.resistance_average = self.__keithley_inst.get_values(self.__avg)[0]
        #self.progress_percentage = 100
        self.progress_bar_loop(70)
        return None 


    @property
    def progress_percentage(self):
        return self.__progress_per

    @progress_percentage.setter #Setter
    def progress_percentage(self, val):
        self.__progress_per = val
        self.property_changed_event.fire("progress_percentage")

    @property #Getter
    def resistance_average(self):
        return format(self.__resistance_avg, '.1f')
    
    @resistance_average.setter #Setter
    def resistance_average(self, val):
        self.__resistance_avg = val
        self.property_changed_event.fire("resistance_average")
        
    @property #Getter
    def resistance_average2(self):
        return format(self.__resistance_avg2, '.1f')

    @resistance_average2.setter #Setter
    def resistance_average2(self, val):
        self.__resistance_avg2 = val
        self.property_changed_event.fire("resistance_average2")
    
    @property #Getter
    def averages(self):
        return str(self.__avg)
    
    @averages.setter #Setter
    def averages(self, val):
        self.__avg = int(val)
        
    @property #Getter
    def pulse_width(self):
        return str(self.__pulse_width)
    
    @pulse_width.setter #Setter
    def pulse_width(self, val):
        self.__pulse_width = int(val)
        self.__agi.set_width(self.__pulse_width)
        
    @property #Getter
    def pulse_tension(self):
        return str(self.__pulse_tension)
    
    @pulse_tension.setter #Setter
    def pulse_tension(self, val):
        self.__pulse_tension = int(val)
        self.__agi.set_tension(self.__pulse_tension)

class Agilent:
    def __init__(self,debug):
        
        self.sucessfull = False
        self.debug = debug
        
        if debug :
            self.sucessfull = True
        else: 
            import pyvisa
            try : 
                rm = pyvisa.ResourceManager()
                self.inst1 = rm.open_resource("GPIB0::5::0::INSTR")
            except pyvisa.errors.VisaIOError:
                self.inst = None
                logging.info("***Agilent***: Could not find instrument.")
        
    def values_ag(self):
        if not self.debug :
            self.inst1.write(":PULS:DOUB OFF")        # Mode Single-Pulse 
            self.inst1.write(":PULS:DEL 0.0MS")      # fixer le délai à 0
            self.inst1.write(":OUTPUT:POL POS")     # Fixer la polarisation positive
            self.inst1.write(":TRIG:SOUR EXT")      # Déclencher le pulse par une source externe 
            self.inst1.write(":OUTP 1") 
        pass
    
    def set_tension(self, ampl):
        self.inst1.write("VOLT %sV" % (ampl))
        
    def set_width(self, width):
        self.inst1.write(":PULS:WIDT %sMS" % (width))






# class close_port_com :
    
#     def __init__(self,debug):
        
#         self.sucessfull = False
#         self.debug = debug
        
        
#     def close_arduino(self):
#        return self.inst2.close()
       
#     def close_keithley(self):
#        return  self.inst.close()
        
#     def close_agilent(self):
#          return self.inst1.close()
             


class Arduino:
    def __init__(self,debug):
        
        self.sucessfull = False
        self.debug = debug
        
        if debug :
            self.sucessfull = True
        else: 
            import pyvisa
            try : 
                rm = pyvisa.ResourceManager()
                self.inst2 = rm.open_resource("ASRL3::INSTR")
            except pyvisa.errors.VisaIOError:
               self.inst = None
               logging.info("***Arduino***: Could not find instrument.")
               
    def trigger_impulsion(self):
        if not self.debug :
            self.inst2.write("REL_P\r")  # Mettre le relais en position pulse 
            time.sleep(TIME_WAIT)
            self.inst2.write("TRIG\r")   # Déclencher le pulse 
            time.sleep(TIME_WAIT)
          
        pass
    
    def change_state(self, state):
        if state:
            self.inst2.write("REL_M\r") #Closed
        else:
            self.inst2.write("REL_P\r") #Open
            
    def reset(self):
        self.inst2.write("RST\r")
        
        
        
class Oscilloscope:
    def __init__(self):
        pass



class Keithley:
    def __init__(self, debug):

        self.sucessfull = False
        self.debug = debug

        if debug:
            self.sucessfull = True
        else:
            import pyvisa
            try:
                rm = pyvisa.ResourceManager()
                self.inst = rm.open_resource("USB0::0x05E6::0x2614::4075638::0::INSTR", timeout = 300000)
                #self.beepkeithley(2400)
                self.sucessfull = True            
            except pyvisa.errors.VisaIOError:
                self.inst = None
                logging.info("***KEITHLEY***: Could not find instrument.")

    def get_values(self, avg):

        """Fonction qui initialise le keithley dans le but d'éffectuer la mesure de résistance"""

        if not self.debug:
            self.write("smua.sense=smua.SENSE_LOCAL")
            #☺self.write("PulseVMeasureI(smua, 0, 1, 20e-2, 50e-2, 10)")  # pulse de 10volts pendant 2ms
            self.write("PulseVMeasureI(smua, 0, 1, 20e-2, 50e-2, "+str(avg)+")")  # pulse de 10volts pendant 2ms
            sortie = self.query("printbuffer(1, smua.nvbuffer1.n,  smua.nvbuffer1.readings)")
            s = sortie.split(', ')
            r = []
            for i in range(avg):
                r.append(1 / float(s[i]))  # Calcul de la résistance aux bornes du keithley
            return (numpy.mean(r), numpy.std(r))
        else:
            val = (numpy.random.rand(), numpy.random.rand())
            return val

    def beepkeithley(self, frequence):
        self.write("beeper.beep(0.5, "+str(int(frequence))+")")

    def generate_pulse_message(self, volts, temps):
        return "PulseVMeasureI(smua, 0, 1, 20e-2, 50e-2, 10)"

    def query(self, message):
        if not self.debug:
            return self.inst.query(message)

    def write(self, message):
        if not self.debug:
            self.inst.write(message)

    def get_current(self):
        
        
        
        if self.debug:
            return numpy.random.rand()
        else:
            pass
        
        
        
        
        