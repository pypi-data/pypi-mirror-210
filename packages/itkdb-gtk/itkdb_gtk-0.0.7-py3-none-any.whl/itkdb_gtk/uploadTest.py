#!/usr/bin/env python3
"""GUI to upload tests."""
import argparse
import json
import sys
from pathlib import Path

try:
    import dbGtkUtils
    import ITkDBlogin
    import ITkDButils
    from ShowComments import ShowComments
    from ShowAttachments import ShowAttachments
    from ShowDefects import ShowDefects

except ModuleNotFoundError:
    from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils
    from itkdb_gtk.ShowComments import ShowComments
    from itkdb_gtk.ShowAttachments import ShowAttachments
    from itkdb_gtk.ShowDefects import ShowDefects

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def create_json_data_editor(data):
    """Create a dialog to show the JSon file."""
    dlg = Gtk.Dialog(title="Test Data")
    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)

    dlg.set_property("height-request", 500)
    box = dlg.get_content_area()
    value = dbGtkUtils.DictDialog(data)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(value)
    box.pack_start(scrolled, True, True, 10)

    dlg.show_all()
    return value, dlg


def check_data(data):
    """Checks validity of JSon data.

    Args:
    ----
        data (): The json data

    Returns
    -------
        boolean: True if valid, False otherwise.

    """
    errors = []
    missing = []
    if "component" not in data:
        errors.append("Need reference to component, hex string")
        missing.append("component")

    if "testType" not in data:
        errors.append("Need to know test type, short code")
        missing.append("testType")

    if "institution" not in data:
        errors.append("Need to know institution, short code")
        missing.append("institution")

    if "results" not in data:
        errors.append("Need some test results")
        missing.append("results")

    return errors, missing


class UploadTest(dbGtkUtils.ITkDBWindow):
    """Collects information to upload a test and its attachments."""

    def __init__(self, session, payload=None, attachment=None):
        """Initialization.

        Args:
        ----
            session: ITkDB session
            payload: path of test file
            attachment: an Attachment object.

        """
        self.payload = payload
        self.data = None
        self.attachments = []
        self.comments = []
        self.defects = []
        if attachment is not None:
            if isinstance(attachment, ITkDButils.Attachment):
                if attachment.path is not None:
                    self.attachments.append(attachment)
            else:
                print("Wrong attachment: {}".format(attachment))

        global gtk_runs
        if gtk_runs:
            super().__init__(session=session, title="Upload Test", gtk_runs=gtk_runs)
            self.init_window()

    def init_window(self):
        """Creates the Gtk window."""
        # Initial tweaks
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Upload Tests"

        # Active buttin in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test_gui)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, True, False, 0)

        # The test file widgets
        lbl = Gtk.Label(label="Test file")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)

        self.testF = Gtk.FileChooserButton()
        self.testF.set_tooltip_text("Click to select JSon test file.")

        grid.attach(self.testF, 1, 0, 1, 1)
        self.testF.connect("file-set", self.on_test_file)

        # This is to show/edit the test file data
        btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="view-paged-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        btn.set_tooltip_text("Click to view/edit test data.")
        btn.connect("clicked", self.show_data)
        grid.attach(btn, 2, 0, 1, 1)

        # Object Data
        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)

        self.entrySN = Gtk.Entry()
        grid.attach(self.entrySN, 1, 1, 1, 1)

        # Test type
        lbl = Gtk.Label(label="Test Type")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 2, 1, 1)

        self.entryTest = Gtk.Entry()
        grid.attach(self.entryTest, 1, 2, 1, 1)

        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)
        dbGtkUtils.add_button_to_container(box, "Attachments",
                                           "Click to edit attachments.",
                                           self.edit_attachments)

        dbGtkUtils.add_button_to_container(box, "Comments",
                                           "Click to edit comments.",
                                           self.edit_comments)

        dbGtkUtils.add_button_to_container(box, "Defects",
                                           "Click to edit defects.",
                                           self.edit_defects)

        dbGtkUtils.add_button_to_container(box, "Upload Test",
                                           "Click to upload test.",
                                           self.upload_test_gui)

        # The text view
        frame = self.create_text_view()
        self.mainBox.pack_start(frame, True, True, 0)

        self.show_all()

        if self.payload:
            the_path = Path(self.payload).expanduser().resolve()
            if the_path.exists():
                ifile = Path(self.payload).expanduser().resolve().as_posix()
                self.testF.set_filename(ifile)
                self.on_test_file(self.testF)

            else:
                print("Input file does not exists: {}".format(self.payload))

        if len(self.attachments):
            dC = [A for A in self.attachments]
            self.attachments.clear()
            for A in dC:
                self.append_attachment_to_view(A)

    def get_test_institute(self):
        """Select an institue."""
        dlg = Gtk.Dialog(title="Select Institution.", flags=0)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.add(box)

        box.pack_start(Gtk.Label(label="Select an Institute"), False, True, 0)

        combo = self.create_institute_combo()
        box.pack_start(combo, False, True, 5)

        dlg.show_all()
        rc = dlg.run()

        out = None
        if rc == Gtk.ResponseType.OK:
            out = self.get_institute_from_combo(combo)

        dlg.hide()
        dlg.destroy()
        return out

    def on_test_file(self, fdlg):
        """Test file browser clicked."""
        fnam = fdlg.get_filename()

        # The file exists by definition
        try:
            self.data = json.loads(open(fnam).read())
            errors, missing = check_data(self.data)

            if len(missing):
                self.write_message("Some keys are missing in the JSon file.\n")
                self.write_message("{}\n".format("\n".join(['\t'+line for line in missing])))

                if "institution" in missing and len(missing) == 1:
                    site = self.get_test_institute()
                    if site:
                        self.data["institution"] = site
                        self.write_message("Setting Institution to {}\n".format(self.data["institution"]))

                else:
                    dbGtkUtils.complain("Invalid JSON file\n{}".format('\n'.join(errors)), fnam)

            self.entrySN.set_text(self.data["component"])
            self.entryTest.set_text(self.data["testType"])
            self.comments = self.data.get("comments", [])
            self.defects = self.data.get("defects", [])

        except Exception as E:
            self.data = None
            self.write_message("Cannot load file {}\n".format(fnam))
            self.write_message("{}\n".format(str(E)))

    def show_data(self, *args):
        """Show data button clicked."""
        if self.data is None:
            return

        value, dlg = create_json_data_editor(self.data)
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            self.data = value.values

        dlg.hide()
        dlg.destroy()

    def edit_attachments(self, *args):
        """Edit test attachmetns."""
        SA = ShowAttachments("Test Attachments", self.session, self.attachments, parent=self)
        response = SA.run()
        if response == Gtk.ResponseType.OK:
            self.attachments = SA.attachments

        SA.hide()
        SA.destroy()

    def edit_comments(self, *args):
        """Edit test comments."""
        SC = ShowComments("Test Comments", self.comments, self)
        rc = SC.run()
        if rc == Gtk.ResponseType.OK:
            self.comments = SC.comments

        SC.hide()
        SC.destroy()

    def edit_defects(self, *args):
        """Edit test defects."""
        SD = ShowDefects("Test Defects", self.defects, self)
        rc = SD.run()
        if rc == Gtk.ResponseType.OK:
            self.defects = SD.defects

        SD.hide()
        SD.destroy()

    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        self.upload_test()

    def upload_test(self):
        """Uploads test and attachments."""
        if self.data is None:
            self.write_message("No data available to upload\n")
            return

        self.data["comments"] = self.comments
        self.data["defects"] = self.defects
        rc = ITkDButils.upload_test(self.session, self.data, self.attachments)
        if rc:
            ipos = rc.find("The following details may help:")
            msg = rc[ipos:]
            dbGtkUtils.complain("Failed uploading test", msg)

        else:
            self.write_message("Upload successfull")
            dbGtkUtils.ask_for_confirmation("Upload successfull", "")


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--test-file", help="Name of json file with test data")
    parser.add_argument("--component-id", help="Override component code")
    parser.add_argument("--raw_data", help="Raw data file", default=None)
    parser.add_argument("--attachment", help="Attachment to upload with the test", default=None)
    parser.add_argument("--attach_title", default=None, type=str, help="The attachment description")
    parser.add_argument("--attach_desc", default="", type=str, help="The attachment description")
    parser.add_argument("--verbose", action="store_true", help="Print what's being sent and received")

    args = parser.parse_args()

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    # Start GUI
    UpT = UploadTest(client,
                     payload=args.test_file,
                     attachment=ITkDButils.Attachment(args.attachment,
                                                      args.attach_title,
                                                      args.attach_desc))

    if gtk_runs:
        UpT.present()
        UpT.connect("destroy", Gtk.main_quit)
        try:
            Gtk.main()

        except KeyboardInterrupt:
            print("Arrrgggg!!!")

    else:
        # Think
        pass

    dlg.die()


if __name__ == "__main__":
    main()
