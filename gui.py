import gi

gi.require_version('Gtk', '3.0')
import logging

from gi.repository import GObject, Gtk, Gdk

BUTTON_SPACING = 10


class PyATEMSwitcherGui():
    def __init__(self, config, switcher):
        self.log = logging.getLogger('GUI')
        self.config = config

        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path('style.css')
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(
            screen,
            cssProvider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        self.window = Gtk.Window()
        self.window.connect("destroy", self._exit)

        self.switcher = switcher
        self.switcher.on_connect(self._switcher_connected)
        self.switcher.on_connect_attempt(self._switcher_connect_attempt)
        self.switcher.on_disconnect(self._switcher_disconnected)
        self.switcher.on_receive(self._switcher_state_changed)

        self.window.set_border_width(BUTTON_SPACING)

        self.header = Gtk.HeaderBar()
        self.header.props.title = 'PyATEMSwitcherGui: Idle'
        self.window.set_titlebar(self.header)

        self.box = None
        self.buttons = {}

    def _exit(self, *args, **kwargs):
        self.switcher.disconnect()
        Gtk.main_quit(*args, **kwargs)

    def _button_clicked(self, button, name):
        self.log.info(f'Button {name} was pressed')
        for btn in self.buttons:
            ctx = self.buttons[btn][0].get_style_context()
            if btn == name:
                self.log.debug(f'{btn}.add_class("selected")')
                ctx.add_class('selected')
                self.switcher.trans(self.buttons[btn][1])
            else:
                self.log.debug(f'{btn}.remove_class("selected")')
                ctx.remove_class('selected')

    def _switcher_connected(self, params):
        log = logging.getLogger('GUI connected')

        log.debug(f'_switcher_connected({params})')
        log.info(f'Connected to "{params.atemModel}" @ {params.ip}')
        self.header.props.title = f'{params.atemModel} @ {params.ip}'

        inputs = {}
        for idx,i in enumerate(params.inputProperties):
            if not i.shortName:
                break
            log.debug(f'Creating Button for {i.shortName} of type {i.externalPortType}: {i.longName}')
            btn = Gtk.Button.new_with_label(
                i.longName
            )
            btn.connect(
                'clicked',
                self._button_clicked,
                f'in_{i.shortName}',
            )
            log.debug(f'Adding {i.shortName} to FlowBox')
            self.buttons[f'in_{i.shortName}'] = (btn, idx)
            inputs.setdefault(str(i.externalPortType), []).append(btn)

        log.debug(repr(inputs))

        log.debug('Creating vertically stacked box as container')
        self.box = Gtk.VBox(spacing=BUTTON_SPACING)

        for input_type in ('hdmi', 'sdi', 'internal'):
            if input_type not in inputs:
                continue

#            log.debug(f'Creating FlowBox for {input_type} buttons')
#            flowbox = Gtk.VBox()
#            flowbox.set_column_spacing(BUTTON_SPACING)
#            flowbox.set_max_children_per_line(2)
#            flowbox.set_row_spacing(BUTTON_SPACING)
#            flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
#            flowbox.set_valign(Gtk.Align.START)

            for btn in inputs[input_type]:
                self.box.pack_start(btn, True, True, 0)
            #self.box.pack_start(flowbox, True, True, 0)

        log.debug('All FlowBoxes added, adding box to window')
        self.window.add(self.box)
        self.window.show_all()
        self.log.debug('done')

    def _switcher_connect_attempt(self, params):
        self.header.props.title = 'PyATEMSwitcherGui: Connecting ...'

    def _switcher_disconnected(self, params):
        if self.box is not None:
            self.window.remove(self.box)
        self.box = None
        self.buttons = {}
        self.header.props.title = 'PyATEMSwitcherGui: Not connected'

    def _switcher_state_changed(self, params):
        source = params['switcher'].programInput[0].videoSource
        sn = params['switcher'].inputProperties[source].shortName
        for btn in self.buttons:
            ctx = self.buttons[btn][0].get_style_context()
            if btn == f'in_{sn}':
                ctx.add_class('program')
            else:
                ctx.remove_class('program')
            ctx.remove_class('selected')

    def main_loop(self):
        self.switcher.connect()
        self.window.show_all()
        Gtk.main()
