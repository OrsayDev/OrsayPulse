# standard libraries
import gettext
from nion.swift import Panel
from nion.swift import Workspace

import threading

from nion.ui import Declarative
from nion.ui import UserInterface

from . import orsay_pulse_handler

_ = gettext.gettext

class handler:

    def __init__(self, instrument, document_controller):

        self.event_loop = document_controller.event_loop
        self.document_controller = document_controller
        self.instrument = instrument
        self.property_changed_event_listener = self.instrument.property_changed_event.listen(self.prepare_widget_enable)
        self.property_busy_event_listener = self.instrument.property_busy_event.listen(self.prepare_widget_disable)


    def init_handler(self):
        self.event_loop.create_task(self.do_enable(False, ['init_pb']))

    async def data_item_show(self, DI):
        self.document_controller.document_model.append_data_item(DI)

    async def data_item_remove(self, DI):
        self.document_controller.document_model.remove_data_item(DI)

    async def data_item_exit_live(self, DI):
        DI._exit_live_state()

    async def do_enable(self, enabled=True, not_affected_widget_name_list=None):
        for var in self.__dict__:
            if var not in not_affected_widget_name_list:
                if isinstance(getattr(self, var), UserInterface.Widget):
                    widg = getattr(self, var)
                    setattr(widg, "enabled", enabled)

    def prepare_widget_enable(self, value):
        self.event_loop.create_task(self.do_enable(True, ["init_pb"]))

    def prepare_widget_disable(self, value):
        self.event_loop.create_task(self.do_enable(False, ["init_pb"]))

    def prepare_free_widget_enable(self,
                                   value):  # THAT THE SECOND EVENT NEVER WORKS. WHAT IS THE DIF BETWEEN THE FIRST?
        self.event_loop.create_task(
            self.do_enable(True, ['init_pb']))

    def pool_current(self, widget):
        print('check')

    def pool_resistance(self, widget):
        self.instrument.resistance()

    def acquire_measurement(self, widget):
        self.instrument.pulse()
        
    def exit_measurement(self, widget):
        self.instrument.close()
    
    def init_measurement(self, widget):
        if self.instrument.init():
            self.init_pb.enabled = False
            self.event_loop.create_task(self.do_enable(True, ['init_pb']))
        

class View:

    def __init__(self, instrument):
        ui = Declarative.DeclarativeUI()

        #Keithley
        self.average_label = ui.create_label(text='Averages: ', name='average_label')
        self.average_le = ui.create_line_edit(text='@binding(instrument.averages)', name='average_le', width=50)

        self.average_row = ui.create_row(self.average_label, self.average_le, ui.create_stretch())
        
        
        self.average_resistance_label = ui.create_label(text='Resistance (before) (Ω): ', name='average_resistance')
        self.average_resistance = ui.create_label(text='@binding(instrument.resistance_average)', name='average_resistance')
        
        self.average_resistance2_label = ui.create_label(text=' Resistance (after) (Ω): ', name='average_resistance2')
        self.average_resistance2 = ui.create_label(text='@binding(instrument.resistance_average2)', name='average_resistance2')

        self.pulse_row = ui.create_row(self.average_resistance_label, self.average_resistance, ui.create_stretch())
        self.pulse_row2 = ui.create_row(self.average_resistance2_label, self.average_resistance2, ui.create_stretch())
        
        
        #Agilent
        self.get_larg_label = ui.create_label(text='Width (ms): ', name='get_larg_label')
        self.get_larg_pb = ui.create_line_edit(text='@binding(instrument.pulse_width)', name='get_larg_pb', width='50')

        self.larg_row = ui.create_row(self.get_larg_label, self.get_larg_pb, ui.create_stretch())
        
        
        self.get_ampl_label = ui.create_label(text='Ampli (V): ', name='get_ampl_label')
        self.get_ampl_pb = ui.create_line_edit(text='@binding(instrument.pulse_tension)', name='get_ampl_pb', width='50')

        self.ampl_row = ui.create_row(self.get_ampl_label, self.get_ampl_pb, ui.create_stretch())
        
        
        
        #Measurement tab
        self.get_resistance_pb = ui.create_push_button(text='Get resistance', name='get_resistance_pb',
                                                     on_clicked='pool_resistance', width=100)
        self.acquire_pb = ui.create_push_button(text='Pulse', name='acquire_pb',
                                                on_clicked='acquire_measurement',width=50)
        
        self.init_pb = ui.create_push_button(text='Init', name='init_pb',
                                                on_clicked='init_measurement',width=50)
        
        self.exit_pb = ui.create_push_button(text='Abort', name='exit_pb',
                                                on_clicked='exit_measurement',width=50)
        self.progress_bar = ui.create_progress_bar(name = 'progress_bar', value = '@binding(instrument.progress_percentage)', width=300)
        
        self.button_row = ui.create_row(self.init_pb,self.get_resistance_pb, self.acquire_pb,  self.exit_pb, ui.create_stretch())
        
        
        #Group manager
        self.d2_group = ui.create_group(title='Keithley', content=ui.create_column(
            self.average_row,self.pulse_row, self.pulse_row2, ui.create_stretch()))
        # , 
        
        self.d3_group = ui.create_group(title='Agilent', content=ui.create_column(
            self.larg_row, self.ampl_row , ui.create_stretch()))
        
        self.d4_group = ui.create_group(title='Measurement', content=ui.create_column(
            self.button_row, self.progress_bar, ui.create_stretch()))

        self.ui_view = ui.create_column(self.d2_group,self.d3_group, self.d4_group)
        
        
        
       

        

def create_panel(document_controller, panel_id, properties):
    instrument = properties["instrument"]
    ui_handler = handler(instrument, document_controller)
    ui_view = View(instrument)
    panel = Panel.Panel(document_controller, panel_id, properties)

    finishes = list()
    panel.widget = Declarative.construct(document_controller.ui, None, ui_view.ui_view, ui_handler, finishes)

    for finish in finishes:
        finish()
    if ui_handler and hasattr(ui_handler, "init_handler"):
        ui_handler.init_handler()
    return panel


def run(instrument) -> None:
    panel_id = "Orsay Pulse"  # make sure it is unique, otherwise only one of the panel will be displayed
    name = _("Orsay Pulse")
    Workspace.WorkspaceManager().register_panel(create_panel, panel_id, name, ["left", "right"], "left",
                                                {"instrument": instrument})
