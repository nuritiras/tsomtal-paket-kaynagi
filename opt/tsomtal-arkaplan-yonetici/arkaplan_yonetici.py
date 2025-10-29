#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import sys

# .deb paketi için düzeltilmiş yol:
HELPER_SCRIPT_PATH = "/opt/tsomtal-arkaplan-yonetici/arkaplan_helper.sh"

class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title("TSOMTAL Arkaplan Yöneticisi")
        self.set_default_size(450, 300)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        try:
            self.set_icon_name("tsomtal-arkaplan")
        except GLib.Error:
            print("İkon bulunamadı, ancak program çalışmaya devam edecek.")

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        link_button = Gtk.LinkButton(
            "https://tsomtal.meb.k12.tr/",
            label="TSOMTAL (Okul Web Sitesi)"
        )
        main_box.pack_start(link_button, False, False, 5)

        main_box.pack_start(Gtk.Separator(), False, False, 10)

        self.file_chooser = Gtk.FileChooserButton(
            title="Kilitlenecek Arkaplan Resmini Seçin",
        )
        image_filter = Gtk.FileFilter()
        image_filter.set_name("Resim Dosyaları")
        image_filter.add_mime_type("image/jpeg")
        image_filter.add_mime_type("image/png")
        image_filter.add_mime_type("image/webp")
        self.file_chooser.add_filter(image_filter)
        
        main_box.pack_start(Gtk.Label(label="Kilitlenecek Resmi Seçin:"), False, False, 0)
        main_box.pack_start(self.file_chooser, False, False, 5)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        lock_button = Gtk.Button(label="Arkaplanı Kilitle")
        lock_button.get_style_context().add_class("suggested-action")
        lock_button.connect("clicked", self.on_lock_clicked)
        
        unlock_button = Gtk.Button(label="Kilidi Kaldır")
        unlock_button.get_style_context().add_class("destructive-action")
        unlock_button.connect("clicked", self.on_unlock_clicked)

        button_box.pack_start(lock_button, True, True, 0)
        button_box.pack_start(unlock_button, True, True, 0)
        
        main_box.pack_end(button_box, False, False, 10)

    def on_lock_clicked(self, widget):
        file_uri = self.file_chooser.get_uri()

        if file_uri is None:
            self.show_message("Hata", "Lütfen önce bir resim dosyası seçin.", "error")
            return

        command = ["pkexec", HELPER_SCRIPT_PATH, "lock", file_uri]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.show_message("Başarılı", "Arkaplan başarıyla kilitlendi.\nOturumu kapatıp açın.")
        except subprocess.CalledProcessError as e:
            if "User dismissed" in e.stderr:
                print("Kullanıcı parola girmeyi iptal etti.")
            else:
                self.show_message("Hata", f"İşlem başarısız oldu: {e.stderr}", "error")

    def on_unlock_clicked(self, widget):
        command = ["pkexec", HELPER_SCRIPT_PATH, "unlock"]
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.show_message("Başarılı", "Arkaplan kilidi başarıyla kaldırıldı.\nOturumu kapatıp açın.")
        except subprocess.CalledProcessError as e:
            if "User dismissed" in e.stderr:
                print("Kullanıcı parola girmeyi iptal etti.")
            else:
                self.show_message("Hata", f"İşlem başarısız oldu: {e.stderr}", "error")

    def show_message(self, title, message, msg_type="info"):
        dialog_type = Gtk.MessageType.INFO
        if msg_type == "error":
            dialog_type = Gtk.MessageType.ERROR
        
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0, message_type=dialog_type,
            buttons=Gtk.ButtonsType.OK, text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="tr.tsomtal.arkaplan-yonetici", **kwargs)
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self)
        self.window.show_all()
        self.window.present()

if __name__ == "__main__":
    app = Application()
    sys.exit(app.run(sys.argv))
