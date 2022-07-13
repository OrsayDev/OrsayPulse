__author__ = "Yves Auad"
import numpy
import logging
from nion.utils import Event

class PulseTools:
    def __init__(self):
        logging.info('Init OK.')
        self.__keithley_inst = Keithley(True)
        self.__arduino_inst = Arduino(True)
        self.__osc = Oscilloscope()
        self.__agi = Agilent(True)

        self.property_changed_event = Event.Event()

    def pulse(self):
        self.property_changed_event.fire("resistance_average")
        return None

    @property #Getter
    def resistance_average(self):
        val = self.__keithley_inst.get_values(10)
        return str(val[0])






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
                self.beepkeithley(2400)
                self.sucessfull = True
            except pyvisa.errors.VisaIOError:
                self.inst = None
                logging.info("***KEITHLEY***: Could not find instrument.")

    def get_values(self, avg):

        """Fonction qui initialise le keithley dans le but d'éffectuer la mesure de résistance"""

        if not self.debug:
            self.write("smua.sense=smua.SENSE_LOCAL")
            self.write("PulseVMeasureI(smua, 0, 1, 20e-2, 50e-2, 10)")  # pulse de 10volts pendant 2ms
            sortie = self.query("printbuffer(1, smua.nvbuffer1.n,  smua.nvbuffer1.readings)")
            s = sortie.split(', ')
            r = []
            for i in range(avg):
                r.append(1 / float(s[i]))  # Calcul de la résistance aux bornes du keithley
            logging.info("\n\nla résistance de votre système vaut :", numpy.mean(r), "ohms. Avec une erreur de:", numpy.std(r), "%")
            return (numpy.mean(r), numpy.std(r))
        else:
            val = (numpy.random.rand(), numpy.random.rand())
            logging.info(f'***KEITHLEY***: {val}')
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