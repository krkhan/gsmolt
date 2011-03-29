#!/usr/bin/env python

import sys
import time
import webbrowser

sys.path.append('/usr/share/smolt/client')

import gtk
import smolt
import smolt_config

class GSmolt:
    def __init__(self):
        filename = 'gsmolt.xml'
        self.builder = gtk.Builder()
        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)

        self.setup_treeview_host()
        self.setup_treeview_device()

    def connect_treeview_with_model(self, treeview, colno):
        col = treeview.get_column(colno)
        cell = gtk.CellRendererText()
        col.pack_start(cell)
        col.add_attribute(cell, 'text', colno)

    def setup_treeview_host(self):
        treeview = self.builder.get_object('treeview_host')
        self.connect_treeview_with_model(treeview, 0)
        self.connect_treeview_with_model(treeview, 1)

    def setup_treeview_device(self):
        treeview = self.builder.get_object('treeview_device')
        self.connect_treeview_with_model(treeview, 0)
        self.connect_treeview_with_model(treeview, 1)
        self.connect_treeview_with_model(treeview, 2)
        self.connect_treeview_with_model(treeview, 3)

    def gather_data(self):
        self.hardware = smolt.Hardware()

    def populate_host_table(self):
        liststore = self.builder.get_object('liststore_host')
        for row in self.hardware.hostIter():
            liststore.append(row)

    def populate_device_table(self):
        liststore = self.builder.get_object('liststore_device')
        for VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, \
                Driver, Type, Description in self.hardware.deviceIter():
            row = (Bus, Driver, Type, Description)
            liststore.append(row)

    def populate_distribution_data(self):
        textbuffer = self.builder.get_object('textbuffer_distribution')
        textbuffer.set_text('No distribution-specific data yet')

    def send_data(self):
        # try:
        time_before = time.time()
        retvalue, self.pub_uuid, self.admin = self.hardware.send(smolt.smoonURL)
        time_after = time.time()
        duration = time_after - time_before
        if retvalue == 0:
            print 'Submission took %d seconds' % duration
            self.on_submission_completed()
        else:
            print 'Submission failed after %d seconds' % duration
            self.on_submission_failed()
        # except TypeError:
        #     self.on_submission_failed()

    def run(self):
        self.gather_data()
        self.populate_host_table()
        self.populate_device_table()
        self.populate_distribution_data()

        window = self.builder.get_object('window_main')
        window.show_all()

        gtk.main()

    def on_submission_completed(self):
        url = smolt.get_profile_link(smolt.smoonURL, smolt.getPubUUID())
        window = self.builder.get_object('window_main')
        message = ('<b>Your profile was sent successfully!</b>\n'
                   'Your profile is available at <a href="%(url)s">this</a> link.\n'
                   'Your profile admin password is:\n'
                   '<i>%(password)s</i>' % {'url':url, 'password':self.admin})

        dialog = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_INFO,
                    gtk.BUTTONS_CLOSE, message)
        dialog.set_property('use-markup', True)
        dialog.run()
        dialog.destroy()

    def on_submission_failed(self):
        print 'Failed'

    def on_action_sendprofile_activate(self, widget, data=None):
        self.send_data()

    def on_action_mypage_activate(self, widget, data=None):
        url = smolt.get_profile_link(smolt.smoonURL, smolt.getPubUUID())
        webbrowser.open(url)

    def on_action_privacypolicy_activate(self, widget, data=None):
        dialog = self.builder.get_object('privacypolicydialog')
        dialog.run()

    def on_action_about_activate(self, widget, data=None):
        dialog = self.builder.get_object('aboutdialog')
        dialog.run()

    def on_action_exit_activate(self, widget, data=None):
        gtk.main_quit()

    def on_privacypolicydialog_response(self, widget, responseid, data=None):
        dialog = self.builder.get_object('privacypolicydialog')
        dialog.hide()

    def on_aboutdialog_response(self, widget, responseid, data=None):
        dialog = self.builder.get_object('aboutdialog')
        dialog.hide()

    def on_window_main_delete_event(self, widget, data=None):
        gtk.main_quit()

if __name__ == "__main__":
    app = GSmolt()
    app.run()

