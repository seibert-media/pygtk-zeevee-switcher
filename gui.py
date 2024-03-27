import gi

gi.require_version("Gtk", "3.0")
import logging
from threading import Lock

from gi.repository import Gdk, GObject, Gtk

BUTTON_SPACING = 5


class ZeeveeSwitcherGui:
    def __init__(self, config, switcher):
        self.log = logging.getLogger("GUI")
        self.config = config

        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path("style.css")
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(
            screen,
            cssProvider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER,
        )

        self.window = Gtk.Window()
        self.window.connect("destroy", self._exit)

        self.window.set_wmclass("pygtk-zeevee-switcher", "PyGTK-ZeeVee-Switcher")

        self.switcher = switcher
        self.switcher.on_connect(self._switcher_connected)
        self.switcher.on_disconnect(self._switcher_disconnected)
        self.switcher.on_connect(self._switcher_state_changed)
        self.switcher.on_receive(self._switcher_state_changed)

        self.window.set_border_width(BUTTON_SPACING)

        self.header = Gtk.HeaderBar()
        self.header.props.title = "SwitcherGui: Idle"
        self.window.set_titlebar(self.header)

        self.redraw_lock = Lock()
        self.box = None
        self.buttons = {}

    def _exit(self, *args, **kwargs):
        self.switcher.disconnect()
        Gtk.main_quit(*args, **kwargs)

    def _button_clicked(self, button, name):
        self.log.info(f"Button {name} was pressed")
        with self.redraw_lock:
            for btn in self.buttons:
                ctx = self.buttons[btn].get_style_context()
                if btn == name:
                    self.log.debug(f'{btn}.add_class("selected")')
                    ctx.add_class("preview")
                    self.switcher.trans(btn[3:])
                else:
                    self.log.debug(f'{btn}.remove_class("selected")')
                    ctx.remove_class("preview")

    def _switcher_connected(self, rc):
        log = logging.getLogger("GUI connected")

        log.debug(f"_switcher_connected({rc!r})")
        self.header.props.title = f"SwitcherGui: Active"

        with self.redraw_lock:
            if self.box is not None:
                log.debug("Removing old VBox from window")
                self.window.remove(self.box)
            self.window.show_all()
            self.box = None
            self.buttons = {}

            log.debug("Button state cleared, creating buttons")
            self.box = Gtk.VBox(spacing=BUTTON_SPACING)
            for zeevee_name, short_name in self.config['inputs'].items():
                log.debug(
                    f"Creating Button for {zeevee_name} as {short_name}"
                )
                btn = Gtk.Button.new_with_label(short_name)
                btn.connect(
                    "clicked",
                    self._button_clicked,
                    f"in_{zeevee_name}",
                )
                log.debug(f"Adding {zeevee_name} to FlowBox")
                self.buttons[f"in_{zeevee_name}"] = btn
                self.box.pack_start(btn, True, True, 0)

            log.debug("All buttons added, adding box to window")
            self.window.add(self.box)
            self.window.show_all()
            self.log.debug("done")

    def _switcher_disconnected(self, params):
        with self.redraw_lock:
            if self.box is not None:
                self.window.remove(self.box)
            self.box = None
            self.buttons = {}
            self.window.show_all()
        self.header.props.title = "SwitcherGui: Idle"

    def _switcher_state_changed(self, message):
        for btn in self.buttons:
            ctx = self.buttons[btn].get_style_context()
            if btn == f"in_{message}":
                ctx.add_class("program")
            else:
                ctx.remove_class("program")
            ctx.remove_class("preview")
            ctx.remove_class("selected")

    def main_loop(self):
        self.switcher.connect()
        self.window.show_all()
        Gtk.main()
