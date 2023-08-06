from pathlib import Path
try:
    import dbGtkUtils
    import ITkDButils
except ModuleNotFoundError:
    from itkdb_gtk import dbGtkUtils, ITkDButils

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk


def add_attachment_dialog():
    """Create the add attachment dialog."""
    dlg = Gtk.Dialog(title="Add Attachment")
    dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK)
    grid = Gtk.Grid(column_spacing=5, row_spacing=1)
    box = dlg.get_content_area()
    box.add(grid)

    lbl = Gtk.Label(label="File")
    lbl.set_xalign(0)
    grid.attach(lbl, 0, 0, 1, 1)

    lbl = Gtk.Label(label="Title")
    lbl.set_xalign(0)
    grid.attach(lbl, 0, 1, 1, 1)

    lbl = Gtk.Label(label="Description")
    lbl.set_xalign(0)
    grid.attach(lbl, 0, 2, 1, 1)

    dlg.fC = Gtk.FileChooserButton()
    grid.attach(dlg.fC, 1, 0, 1, 1)

    dlg.att_title = Gtk.Entry()
    grid.attach(dlg.att_title, 1, 1, 1, 1)

    dlg.att_desc = Gtk.Entry()
    grid.attach(dlg.att_desc, 1, 2, 1, 1)

    dlg.show_all()
    return dlg


class ShowAttachments(Gtk.Dialog):
    """Window to show attachments."""
    def __init__(self, title, session, attachments=[], parent=None):
        """Initialization."""
        super().__init__(title=title, transient_for=parent)
        self.session = session
        self.attachments = [A for A in attachments]
        self.init_window()

    def init_window(self):
        """Prepares the window."""
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        self.mainBox = self.get_content_area()
        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)

        dbGtkUtils.add_button_to_container(box, "Add attachment",
                                           "Click to add a new attachment.",
                                           self.add_attachment)

        dbGtkUtils.add_button_to_container(box, "Remove attachment",
                                           "Click to remove selected attachment.",
                                           self.remove_attachment)

        # the list of attachments
        tree_view = self.create_tree_view()
        self.mainBox.pack_start(tree_view, True, True, 0)
        for A in self.attachments:
            self.append_attachment_to_view(A)

        self.show_all()

    def create_tree_view(self, size=150):
        """Creates the tree vew with the attachments."""
        model = Gtk.ListStore(str, str, str, str)
        self.tree = Gtk.TreeView(model=model)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Attachment", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=1)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Description", renderer, text=2)
        self.tree.append_column(column)

        return scrolled

    def add_attachment(self, *args):
        """Add Attachment button clicked."""
        dlg = add_attachment_dialog()
        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            path = Path(dlg.fC.get_filename())
            A = ITkDButils.Attachment(path, dlg.att_title.get_text().strip(), dlg.att_desc.get_text().strip())
            self.append_attachment_to_view(A)
            self.attachments.append(A)

        dlg.hide()
        dlg.destroy()

    def append_attachment_to_view(self, A):
        """Insert attachment to tree view."""
        model = self.tree.get_model()
        model.append([A.path.name, A.title, A.desc, A.path.as_posix()])

    def remove_attachment(self, *args):
        """Remove selected attachment."""
        select = self.tree.get_selection()
        model, iter = select.get_selected()
        if iter:
            values = model[iter]
            for a in self.attachments:
                if a.path == values[3]:
                    rc = dbGtkUtils.ask_for_confirmation("Remove this attachment ?",
                                                         "{} - {}\n{}".format(a.title, a.desc, values[0]))
                    if rc:
                        self.attachments.remove(a)
                        model.remove(iter)

                    break
