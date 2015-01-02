#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -*- coding: utf-8 -*-
#
# Florian Roth

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

import os
import exiftransformer
import traceback


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Error(FloatLayout):
    message = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(TabbedPanel):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    txt_filename = ObjectProperty(None)
    txt_log = ObjectProperty(None)
    target_set = False
    location_set = False
    locations = []

    def dismiss_popup(self):
        self._popup.dismiss()

    def on_dropfile(self, filename):
        print filename

    def load(self, path, filename):
        #with open(os.path.join(path, filename[0])) as stream:
        #    self.text_input.text = stream.read()
        if filename:
            self.txt_filename.text = filename[0]
            self.target_set = True
            self.dismiss_popup()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select image file or directory", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def set_location(self, location):
        if not location in self.locations:
            self.log("Adding '%s' to EXIF locations" % location)
            self.locations.append(location)
            self.location_set = True
        else:
            self.log("Removing '%s' to EXIF locations" % location)
            self.locations.remove(location)
            if len(self.locations) < 1:
                self.location_set = False

    def run_transform(self):
        # Check if target set
        if not self.target_set:
            self.show_error("Set image file or directory")
            return 0
        elif not self.location_set:
            self.show_error("Set fake EXIF location")
            return 0
        try:
            self.log("Starting transformation ...")
            transformer = exiftransformer.EXIFTransformer(self.txt_filename.text, self.locations, self)
            transformer.execute()
            self.log("Transformation completed.")
            self.log("---------------------------------------------")
        except Exception,e:
            self.log(traceback.format_exc())

    def show_error(self, message):
        content = Error(message=message, cancel=self.dismiss_popup)
        self._popup = Popup(title="Error", content=content, size_hint=(0.3, 0.3))
        self._popup.open()

    def log(self, message):
        self.txt_log.text += "\n%s" % message

class Narsil(App):
    pass

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('Error', cls=Error)

if __name__ == '__main__':
    Narsil().run()