import os
import sys
import hashlib
import functools
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

from tkinter import Tk, filedialog

import kivy

kivy.require('1.9.1')

kivy.Config.set('kivy', 'desktop', 1)
kivy.Config.set('input', 'mouse', 'mouse,disable_multitouch')
kivy.Config.set('graphics', 'width', '320')
kivy.Config.set('graphics', 'height', '320')

from kivy.app import App
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.listview import ListView
from kivy.uix.listview import ListItemLabel
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.image import Image

import slashlock

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ChooseDirectoryScreen(Screen):

    def _directory_selected(self, future):
        self.disabled = False

        save_dir = App.get_running_app().save_directory

        self.ids['save_directory_label'].text = ' '.join(
            ['Save in:', save_dir])

    def click_continue(self):
        sm = App.get_running_app().root.ids['screen_manager']
        sm.current = "file_name_screen"

    def _choose_directory(self):
        Tk().withdraw()  # Don't show the tk window
        # Set the current directory to where the file is located
        App.get_running_app().save_directory = filedialog.askdirectory(
            initialdir=os.path.dirname(App.get_running_app().filepath)
        )

    def choose_directory(self):
        self.disabled = True
        executor = ThreadPoolExecutor()

        future_result = executor.submit(self._choose_directory)
        future_result.add_done_callback(self._directory_selected)


class CryptoApp(App):

    file_status = 'unlocked'
    filename = StringProperty('')
    save_directory = StringProperty('')
    save_as = StringProperty('')
    lock_or_unlock = StringProperty('Lock')
    processing_status = StringProperty('')
    result_message = StringProperty('')
    _passphrase = StringProperty('')
    _metadata = None

    def build(self):
        build_file = resource_path('gui.kv')
        return Builder.load_file(build_file)

    @property
    def _screen_manager(self):
        return self.root.ids['screen_manager']

    def on_drop(self, *args):
        # Remove quotes that were inserted to replace spaces and hyphens
        sm = self._screen_manager
        if sm.current == 'drop_screen':

            self.filepath = unquote(args[1].decode('utf-8'))
            self.filename = os.path.basename(self.filepath)
            self.save_directory = os.path.dirname(self.filepath)

            self._metadata = slashlock._metadata_from_locked_file(
                self.filepath, self._passphrase)

            if self._metadata:
                self.file_status = 'locked'
                self.lock_or_unlock = 'Unlock'
                self.save_as = self._metadata.name.decode('utf-8')
            else:
                self.save_as = '.'.join([self.filename, 'locked'])

            sm = self.root.ids['screen_manager']
            sm.current = "choose_directory_screen"

    def randomize_name(self):
        """ Randomize the filename """
        self.save_as = slashlock.randomize_name()

    def run_lock_or_unlock(self):
        """ Call the correct method """

        self.processing_status = " ".join([
            "Saving",
            self.filename,
            'as',
            os.path.join(self.save_directory, self.save_as)])

        if self.file_status == 'unlocked':
            print("Calling lock")
            self._encrypt()
        else:
            print("Calling unlock")
            self._decrypt()

        sm = self.root.ids['screen_manager']
        sm.current = "processing_screen"

    def _processing_complete(self, result):
        """ Go to the processing complete screen """

        self.result_message = 'Successfully saved {} as {}'.format(
            self.filename,
            os.path.join(self.save_directory, self.save_as),
        )

        self._screen_manager.current = 'result_screen'

    def _encrypt(self):
        """ Encrypt the file """
        print('locking file...', end='')

        executor = ThreadPoolExecutor()
        future_result = executor.submit(functools.partial(
            slashlock.lock,
            self.filepath,
            self._passphrase,
            save_dir=self.save_directory,
            save_as=self.save_as,
        ))

        future_result.add_done_callback(self._processing_complete)

    def _decrypt(self):
        """ Encrypt the file """

        print('Unlocking file...', end='')

        executor = ThreadPoolExecutor()
        future_result = executor.submit(functools.partial(
            slashlock.unlock,
            self.filepath,
            self._passphrase,
            save_dir=self.save_directory,
            save_as=self.save_as,
        ))
        future_result.add_done_callback(self._processing_complete)
        print('Success!')

    def _reset(self, passphrase=False):
        """ Reset the application variables """

        self.file_status = 'unlocked'
        self.filename = ''
        self.save_directory = ''
        self.save_as = ''
        self.lock_or_unlock = 'Lock'
        self.processing_status = ''
        self._metadata = None
        self.result_message = ''

        if passphrase:
            self._passphrase = ''
        else:
            self._screen_manager.current = 'drop_screen'

    def set_passphrase(self):
        """ Set the passphrase """
        self._passphrase = self.root.ids[
            'set_passphrase_screen'].ids['passphrase'].text

        sm = self.root.ids['screen_manager']
        sm.current = "drop_screen"


def main():
    app = CryptoApp()
    app.title = 'Slashlock'
    Window.bind(on_dropfile=app.on_drop)
    app.run()

if __name__ == "__main__":
    main()
