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

    def measure_all(self):
        self.property_changed_event.fire("measure_voltage")
        self.property_changed_event.fire("measure_current")

    @property
    def measure_voltage(self):
        return self.__keithley_inst.measure('v')

    @property
    def measure_current(self):
        return self.__keithley_inst.measure('i')

    @property #Getter
    def resistance_average(self):
        return self.__keithley_inst.resistance_average

    @property
    def source_voltage(self):
        return self.__keithley_inst.get_source_voltage()

    @source_voltage.setter
    def source_voltage(self, value):
        if float(value) < 20:
            self.__keithley_inst.set_source_voltage(float(value))
        else:
            logging.info(f'***PULSE***: Offset voltage must be <20V.')
        self.property_changed_event.fire("source_voltage")

    @property
    def source_voltage_enable(self):
        return self.__keithley_inst.get_offset_voltage_enable()

    @source_voltage_enable.setter
    def source_voltage_enable(self, value: bool):
        self.__keithley_inst.set_offset_voltage_enable(value)
        self.property_changed_event.fire("source_voltage_enable")






class Agilent:
    def __init__(self):
        pass


class Arduino:
    def __init__(self):
        pass

class Oscilloscope:
    def __init__(self):
        pass

#This is for the Keithley sourcemeter series 26XX
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
                self.debug = True

    def get_source_voltage(self):
        offset_voltage = self.query("print(smua.source.levelv)")
        return float(offset_voltage)

    def set_source_voltage(self, offset):
        self.write("smua.source.func = smua.OUTPUT_DCVOLTS")  # Set to voltage source mode
        self.write(f"smua.source.levelv = {offset}")  # Apply the voltage offset
        self.write("smua.source.output = smua.OUTPUT_ON") # Enable the output

    def measure(self, type: str):
        if type == 'v':
            return float(self.query("print(smua.measure.v())"))
        elif type == 'i':
            return float(self.query("print(smua.measure.i())"))
        else:
            logging.info("***KEITHLEY***: Measurement used incorrect parameters. Please use only 'v' or 'i'.")

    def get_offset_voltage_enable(self):
        response = self.query("print(smua.source.output)")
        return True if int(float(response)) == 1 else False

    def set_offset_voltage_enable(self, value):
        if value:
            self.write("smua.source.output = smua.OUTPUT_ON")
        else:
            self.write("smua.source.output = smua.OUTPUT_OFF")


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
        else:
            return numpy.random.uniform(1, 20)

    def write(self, message):
        if not self.debug:
            self.inst.write(message)