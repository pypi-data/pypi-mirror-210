import webview
import os
import sys

from .api import NodeApi, PequenaApi

_window = None

base_directory = None
if os.name == 'posix':  # for *nix systems
    base_directory = os.path.join(os.path.expanduser('~'), '.pywebview')
elif os.name == 'nt':  # for Windows
    base_directory = os.path.join(os.environ['APPDATA'], 'pywebview')

exposed_fcs = []


def expose_functions(*fc):
    for f in fc:
        exposed_fcs.append(f)


def init_window(src="client/index.html", window_name="Hello World!", width=800, height=600,
                x=None, y=None, resizable=True, fullscreen=False, min_size=(200, 100),
                hidden=False, frameless=False, easy_drag=True,
                minimized=False, on_top=False, confirm_close=False, background_color='#FFFFFF',
                transparent=False, text_select=False, zoomable=False, draggable=False):
    global _window
    _window = webview.create_window(title=window_name, url=src, width=width, height=height,
                                    x=x, y=y, resizable=resizable, fullscreen=fullscreen, min_size=min_size,
                                    hidden=hidden, frameless=frameless, easy_drag=easy_drag,
                                    minimized=minimized, on_top=on_top, confirm_close=confirm_close, background_color=background_color,
                                    transparent=transparent, text_select=text_select, zoomable=zoomable, draggable=draggable)
    return _window


def start_window(port=None, debug=True):
    _window.expose_class(PequenaApi())
    _window.expose_class(NodeApi())
    for fc in exposed_fcs:
        _window.expose(fc)
    webview.start(gui='edgechromium', debug=debug,
                  http_port=port, storage_path=base_directory)
