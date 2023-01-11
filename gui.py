import gi

gi.require_version('Gtk', '3.0')
import logging

from gi.repository import GObject, Gtk

BUTTON_SPACING = 10


class PyATEMSwitcherGui():
    def __init__(self, config, switcher):
        self.log = logging.getLogger('GUI')
        self.config = config
        self.window = Gtk.Window()
        self.window.connect("destroy", Gtk.main_quit)
        self.switcher = switcher
        self.switcher.on_connect(self._switcher_connected)
        self.switcher.on_connect_attempt(self._switcher_connect_attempt)
        self.switcher.on_disconnect(self._switcher_disconnected)

        self.window.set_border_width(BUTTON_SPACING)

        self.header = Gtk.HeaderBar()
        self.header.props.title = 'PyATEMSwitcherGui: Idle'
        self.window.set_titlebar(self.header)

        self.buttons = {}
        self.box = None

        # TODO use connection hooks
        self._switcher_connected({})

    def _button_clicked(self, button, name):
        # TODO actually do something
        self.header.props.title = f'PyATEMSwitcherGui: {name}'
        self.log.info(f'Button {name} was pressed')

    def _switcher_connected(self, params):
        self.box = Gtk.FlowBox()
        self.box.set_column_spacing(BUTTON_SPACING)
        self.box.set_max_children_per_line(2)
        self.box.set_row_spacing(BUTTON_SPACING)
        self.box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.box.set_valign(Gtk.Align.START)

        # TODO get input list from switcher
        for i in range(1, 7):
            self.buttons[f'input{i}'] = Gtk.Button.new_with_label(
                f'input{i}'
            )
            self.buttons[f'input{i}'].connect(
                'clicked',
                self._button_clicked,
                f'input{i}',
            )
            self.box.add(self.buttons[f'input{i}'])

        self.window.add(self.box)

    def _switcher_connect_attempt(self, params):
        pass

    def _switcher_disconnected(self, params):
        if self.box is not None:
            self.window.remove(self.box)
        self.box = None
        self.buttons = {}

    def _switcher_ping(self):
        # TODO actually do something here
        self.log.debug('_switcher_ping()')
        return True

    def main_loop(self):
        # TODO connect to switcher
        self.window.show_all()
        GObject.timeout_add(500, self._switcher_ping)
        Gtk.main()
