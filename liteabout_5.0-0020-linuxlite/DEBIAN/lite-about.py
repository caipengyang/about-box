#!/usr/bin/env python3
import json
import os

import gi
import subprocess
import requests
from datetime import datetime
from base64 import b64encode

import const

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk


class AboutLinuxLiteWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="About Linux Lite")
        self.set_border_width(10)
        self.set_resizable(False)
        # self.set_default_size(600, 400)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # init stack layout
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(200)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)

        logo = Gtk.Image()
        logo.set_from_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'linux_lite_dark_logo.png'))
        pixbuf = logo.get_pixbuf()
        scaled_buf = pixbuf.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR)
        logo.set_from_pixbuf(scaled_buf)
        grid.attach(logo, 2, 0, 2, 1)

        label = Gtk.Label()
        label.set_markup(const.ABOUT_SYSTEM.strip())
        label.set_selectable(False)
        grid.attach(label, 0, 0, 5, 10)

        check_for_update_button = Gtk.Button.new_with_label("Check For Update")
        check_for_update_button.connect("clicked", self.on_check_for_update_click)
        grid.attach(check_for_update_button, 0, 10, 1, 1)

        system_information_button = Gtk.Button.new_with_label("System Information")
        system_information_button.connect("clicked", self.on_system_information_click)
        grid.attach_next_to(system_information_button, check_for_update_button, Gtk.PositionType.RIGHT, 1, 1)

        take_screenshot_button = Gtk.Button.new_with_label("Screenshot")
        take_screenshot_button.connect("clicked", self.on_take_screenshot_click)
        grid.attach_next_to(take_screenshot_button, system_information_button, Gtk.PositionType.RIGHT, 1, 1)

        stack.add_titled(grid, "system", "System")

        grid = Gtk.Grid(column_homogeneous=True, column_spacing=100)
        label = Gtk.Label()
        label.set_markup("<big>Licence GPLv2</big>")
        grid.attach(label, 0, 0, 1, 1)

        label = Gtk.Label()
        label.set_text(const.GPL2_CONTENT.strip())
        label.set_margin_left(20)
        label.set_margin_right(20)
        label.set_selectable(False)
        label.select_region(0, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(5)
        scrolled_window.set_min_content_height(220)
        # there is always the scrollbar (otherwise: AUTOMATIC - only if needed
        # - or NEVER)
        scrolled_window.set_policy(
            Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        scrolled_window.add_with_viewport(label)
        grid.attach(scrolled_window, 0, 1, 1, 10)

        label = Gtk.Label()
        label.set_markup("<big>%s</big>" % datetime.now().year)
        grid.attach(label, 0, 11, 1, 1)

        stack.add_titled(grid, "licence", "Licence")
        # add the label to the scrolledwindow
        # label.set_size(scrolled_window.get_default_size())

        grid = Gtk.Grid(column_homogeneous=True, column_spacing=100, row_spacing=5)

        for (index, uri) in enumerate((
                'https://www.linuxliteos.com/',
                'https://www.linuxliteos.com/forums/',
                'https://www.linuxliteos.com/manual/',
                'https://www.linuxliteos.com/screenshots/',)):
            link_button = Gtk.LinkButton(uri, label=uri)
            grid.attach(link_button, 0, index, 1, 1)

        label = Gtk.Label()
        label.set_markup(const.LINUX_LITE_COMMUNITY.strip())
        label.set_selectable(False)
        label.select_region(0, 0)
        grid.attach(label, 0, 4, 1, 1)
        stack.add_titled(grid, "about", "About Us")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        grid = Gtk.Grid(column_homogeneous=True, column_spacing=100)
        grid.attach(stack_switcher, 1, 5, 1, 1)

        vbox.pack_start(grid, True, True, 0)
        vbox.pack_start(stack, True, True, 0)

    def on_check_for_update_click(self, button):
        subprocess.call("/usr/bin/lite-updates", stdin=None, stdout=None, stderr=None, shell=False)

    def on_system_information_click(self, button):
        subprocess.call("hardinfo", stdin=None, stdout=None, stderr=None, shell=False)

    def on_take_screenshot_click(self, button):
        size = self.get_size()
        pixbuf = Gdk.pixbuf_get_from_window(self.get_window(), 0, 0, size[0], size[1])
        file_name = "screen_shot_%s.png" % datetime.now().strftime("%Y%m%d%H%M%S")
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
        pixbuf.savev(path, "png", [], [])
        with open(path, "rb") as a_file:
            headers = {"Authorization": "Client-ID 081eb604a665799"}
            url = "https://api.imgur.com/3/upload"

            response = requests.post(
                url,
                headers=headers,
                data={
                    'image': b64encode(a_file.read()),
                    'type': 'base64',
                    'name': file_name,
                    'title': 'linux screenshot:' + file_name
                }
            )
            if response.ok:
                data = json.loads(response.content)["data"]
                os.system("xdg-open %s" % data["link"])

            else:
                md = Gtk.MessageDialog(parent=self,
                                       flags=Gtk.DialogFlags.MODAL,
                                       type=Gtk.MessageType.ERROR,
                                       buttons=Gtk.ButtonsType.OK,
                                       message_format="%s:%s" % (response.status_code, response.content))
                md.run()


win = AboutLinuxLiteWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
