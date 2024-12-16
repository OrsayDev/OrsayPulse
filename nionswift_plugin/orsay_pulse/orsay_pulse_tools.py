__author__ = "Yves Auad"
import numpy
import logging
import time
from nion.utils import Event

class PulseTools:
    def __init__(self):
        logging.info('Init OK.')
        self.__keithley_inst = Keithley(False)
        self.__arduino_inst = Arduino()
        self.__osc = Oscilloscope()
        self.__agi = Agilent()

        self.property_changed_event = Event.Event()

    def acquire(self):
        self.__keithley_inst.get_resistance_average(10)
        self.property_changed_event.fire("resistance_average")

    @property #Getter
    def resistance_average(self):
        return self.__keithley_inst.resistance_average

    @property
    def offset_voltage(self):
        offset_voltage = self.__keithley_inst.query("print(smua.source.levelv)")
        return float(offset_voltage)

    @offset_voltage.setter
    def offset_voltage(self, value):
        if float(value) < 20:
            self.__keithley_inst.set_offset_value(float(value))
        else:
            logging.info(f'***PULSE***: Offset voltage must be <20V.')
        self.property_changed_event.fire("offset_voltage")

    @property
    def offset_voltage_enable(self):
        response = self.__keithley_inst.query("print(smua.source.output)")
        return True if int(float(response)) == 1 else False

    @offset_voltage_enable.setter
    def offset_voltage_enable(self, value):
        if value:
            self.__keithley_inst.write("smua.source.output = smua.OUTPUT_ON")
        else:
            self.__keithley_inst.write("smua.source.output = smua.OUTPUT_OFF")
        self.property_changed_event.fire("offset_voltage_enable")






class Agilent:
    def __init__(self):
        pass


class Arduino:
    def __init__(self):
        pass

class Oscilloscope:
    def __init__(self):
        pass

class Keithley:
    def __init__(self, debug):

        self.sucessfull = False
        self.debug = debug
        self.resistance_average = None

        if debug:
            self.sucessfull = True
        else:
            import pyvisa
            try:
                rm = pyvisa.ResourceManager()
                self.inst = rm.open_resource("USB0::0x05E6::0x2614::4075638::0::INSTR", timeout = 300000)
                self.sucessfull = True
            except pyvisa.errors.VisaIOError:
                self.inst = None
                logging.info("***KEITHLEY***: Could not find instrument.")

    def set_offset_value(self, offset):
        # Configure the SMU for voltage source mode
        self.write("smua.source.func = smua.OUTPUT_DCVOLTS")  # Set to voltage source mode

        # Set the voltage offset
        self.write(f"smua.source.levelv = {offset}")  # Apply the voltage offset

        # Enable the output
        self.write("smua.source.output = smua.OUTPUT_ON")


    def get_resistance_average(self, avg: int):

        """Fonction qui initialise le keithley dans le but d'éffectuer la mesure de résistance"""

        if not self.debug:
            self.write("smua.sense=smua.SENSE_LOCAL")
            self.write("PulseVMeasureI(smua, 0, 1, 20e-2, 50e-2, 10)")  # pulse de 10volts pendant 2ms
            sortie = self.query("printbuffer(1, smua.nvbuffer1.n,  smua.nvbuffer1.readings)")
            s = sortie.split(', ')
            r = []
            for i in range(avg):
                r.append(1 / float(s[i]))  # Calcul de la résistance aux bornes du keithley
            logging.info(f"***KEITHLEY***: The resistance is: {numpy.mean(r)} ohms. STD: {numpy.std(r)}%")
            self.resistance_average = numpy.mean(r)
            return numpy.mean(r), numpy.std(r)
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