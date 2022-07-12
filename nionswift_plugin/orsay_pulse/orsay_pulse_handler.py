# standard libraries
import gettext
from nion.swift import Panel
from nion.swift import Workspace
import time
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


    def init_handler(self):
        self.event_loop.create_task(self.do_enable(True, ['']))

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

    def pool_pulse(self, widget):
        pass

    def acquire_measurement(self, widget):
        self.instrument.acquire()

class View:

    def __init__(self, instrument):
        ui = Declarative.DeclarativeUI()

        #Gain group
        self.get_current_label = ui.create_label(text='Current (mA): ', name='get_current_label')
        self.get_current_pb = ui.create_push_button(text='Get current', name='get_current_pb', on_clicked='pool_current')

        self.current_row = ui.create_row(self.get_current_label, self.get_current_pb, ui.create_stretch())

        self.get_pulse_label = ui.create_label(text='Pulse (ms): ', name='get_pulse_label')
        self.get_pulse_pb = ui.create_push_button(text='Get pulse', name='get_pulse_pb',
                                                    on_clicked='pool_pulse')
        self.average_resistance = ui.create_label(text='@binding(instrument.resistance_average)', name='average_resistance')

        self.pulse_row = ui.create_row(self.get_pulse_label, self.get_pulse_pb, self.average_resistance, ui.create_stretch())

        self.d2_group = ui.create_group(title='Keithley', content=ui.create_column(
            self.current_row, self.pulse_row, ui.create_stretch()))

        self.acquire_pb = ui.create_push_button(text='Acquire', name='acquire_pb',
                                                on_clicked='acquire_measurement')


        self.ui_view = ui.create_column(self.d2_group, self.acquire_pb)

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