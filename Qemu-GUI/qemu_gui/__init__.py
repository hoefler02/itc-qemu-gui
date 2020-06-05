import sys
import logging
import webbrowser
import json

from PySide2.QtWidgets import QApplication, QMainWindow, QListWidget, QMessageBox, QTreeWidgetItem, QAction, QFileDialog # pylint: disable=no-name-in-module
from PySide2.QtCore import QFile, QDir # pylint: disable=no-name-in-module

from ui.compiled.main_ui import Ui_MainWindow # pylint: disable=import-error
from ui.widgets import CommandForm, PreferencesWidget # pylint: disable=import-error

from qmp_ui import QmpCommand, QmpDataType, QmpEvent, QmpSchema # pylint: disable=import-error

from pyqmp import QEMUMonitorProtocol

from app_utils.settings import SettingsJSON

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        default_settings = {
            "Qemu Hosts":{
                "default": "ICDH",
                "ICDH": {
                    "port": 5103,
                    "host": "172.18.0.2"
                },
                
            },
            "general":{

            }
        }
        self.settings = SettingsJSON(default_settings, "qemu-gui")
        self.prefernces_ui = PreferencesWidget(self.settings)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.events = None
        self.commands = None
        self.data_types = None
        
        # populate the UI
        default_host = self.settings.settings['Qemu Hosts'][self.settings.settings['Qemu Hosts']['default']]
        self.monitor, self.schema = self.connect_qemu(default_host['host'], default_host['port'])

        # for build command/event
        self.command_popup = None
        self.command = None
        self.ui.build_event_btn.clicked.connect(self.build_command)
        self.ui.build_cmd_btn.clicked.connect(self.build_command)


        self.ui.event_list.addItems(self.events)
        self.ui.event_list.itemClicked.connect(self.view_item_detail)
        self.ui.event_list.sortItems()
        self.ui.cmd_list.addItems(self.commands)
        self.ui.cmd_list.itemClicked.connect(self.view_item_detail)
        self.ui.cmd_list.sortItems()

        # set the action hooks                 # note, use lambda to pass a function call with args, otherwise pass the function object
        self.ui.cmd_search_btn.clicked.connect(lambda: self.search_item_list(self.ui.cmd_search_field.text(), 
                                                                             self.commands,
                                                                             self.ui.cmd_list))
        self.ui.event_search_btn.clicked.connect(lambda: self.search_item_list(self.ui.event_search_field.text(), 
                                                                               self.events,
                                                                               self.ui.event_list))
        self.ui.cmd_search_field.returnPressed.connect(lambda: self.search_item_list(self.ui.cmd_search_field.text(), 
                                                                             self.commands,
                                                                             self.ui.cmd_list))
        self.ui.event_search_field.returnPressed.connect(lambda: self.search_item_list(self.ui.event_search_field.text(), 
                                                                               self.events,
                                                                               self.ui.event_list))

        # Menu Items
        self.ui.actionPreferences.setMenuRole(QAction.AboutRole)
        self.ui.actionPreferences.triggered.connect(self.prefernces_ui.show)

        self.ui.actionQMP_Reference.triggered.connect(lambda: webbrowser.open_new_tab("https://www.qemu.org/docs/master/qemu-qmp-ref.html"))
        self.ui.actionDump_Schema.triggered.connect(self.dump_schema)

        # Update the status bar with the number of commands available
        self.ui.statusbar.showMessage("Ready. {} Commands and {} Events parsed.".format(len(self.commands), len(self.events)))

    def connect_qemu(self, host: str, port: int):
        """
        Connects to a running Qemu instances that supports QMP
        """
        monitor = QEMUMonitorProtocol(address=(host, port))  # icdh sim must be running first
        monitor.connect()
        schema = QmpSchema(monitor.cmd(name="query-qmp-schema"))
        self.events = schema.get_events()
        self.commands = schema.get_commands()
        # TODO self.data_types = schema. Data types viewer needed?
        return (monitor, schema)

    def search_item_list(self, search_string: str, item_list: list, qt_list: QListWidget):
        """
        Searches a list of items for matching text, then displayes the items in the specified qt_list.
        """
        matched = list()

        for item in item_list:
            if search_string.lower() in item.lower():
                matched.append(item)
        qt_list.clear()
        qt_list.addItems(matched)
        qt_list.sortItems()
        self.ui.statusbar.showMessage("Showing {} of {} items".format(len(matched), len(item_list)))

    def view_item_detail(self, item):
        """
        Displays a treeview of a command/event's argument/return types
        """
        # nested functions? Because why not!
        def build_data_type(arg_name, arg_data):
            if arg_data.members == None: # base data type
                try:
                    return QTreeWidgetItem(None, [arg_name, str(arg_data.optional), arg_data.meta_type, str(arg_data.python_type).split(" ")[1].strip(">").replace("'", ""), str(arg_data.values)])
                except IndexError:
                    return QTreeWidgetItem(None, [arg_name, str(arg_data.optional), arg_data.meta_type, str(arg_data.python_type).split(" ")[0].strip("><").replace("'", ""), str(arg_data.values)])

            # nested data type
            arg_item = QTreeWidgetItem(None, [arg_name, str(arg_data.optional), arg_data.meta_type, str(arg_data.python_type).split(" ")[1].strip(">").replace("'", ""), str(arg_data.values)])
            for member in arg_data.members:
                # try:
                arg_item.insertChild(0, build_data_type(member, arg_data.members[member]))
                # except TypeError: # handle the case where the members entry is a one element array instead of a dict
                #     for entry in arg_data.members:
                #         if entry['type'] in ['str', 'int', 'bool']: # if the type is a builin
                #             arg_item.insertChild(0, QTreeWidgetItem(None, [entry['name'], "builtin", entry['type'], "None"]))
                #         else:
                #             arg_item.insertChild(0, build_data_type(entry['name'], entry))
            return arg_item

        item = item.text()
        if item in self.commands:
            item = self.schema.get_command(item)
            self.command = item
            self.ui.build_cmd_btn.setDisabled(False)
            self.ui.build_event_btn.setDisabled(True)
            self.ui.cmd_detail.clear()
            ret_type = QTreeWidgetItem(None, ["Returns","", "object", "dict", "None"])
            args = QTreeWidgetItem(None, ["Arguments","", "object", "dict", "None"])
            
            if (item.ret_type.members is not None) and (len(item.ret_type.members) > 0):
                for ret in item.ret_type.members:
                    arg_data = item.ret_type.members[ret]
                    arg_item = build_data_type(ret, arg_data)
                    ret_type.insertChild(0, arg_item)
            elif item.ret_type.meta_type == 'builtin':
                arg_item = build_data_type(item.ret_type.name, item.ret_type)
                ret_type.insertChild(0, arg_item)
            else:
                ret_type.insertChild(0, QTreeWidgetItem(None, ["None","", "", "", ""]))
                logger.debug("raw ret: {}".format(item.ret_type))
            
            if (item.args.members is not None) and (len(item.args.members) > 0):
                for arg in item.args.members:
                    arg_data = item.args.members[arg]
                    arg_item = build_data_type(arg, arg_data)
                    args.insertChild(0, arg_item)
            elif item.args.meta_type == 'builtin':
                arg_item = build_data_type(item.args.name, item.args)
                args.insertChild(0, arg_item) 
            else:
                args.insertChild(0, QTreeWidgetItem(None, ["None","", "", "", ""]))
                logger.debug("raw args: {}".format(item.args))
            
            self.ui.cmd_detail.insertTopLevelItem(0, ret_type)
            self.ui.cmd_detail.insertTopLevelItem(1, args)
            self.ui.cmd_detail.expandAll()

        elif item in self.events:
            item = self.schema.get_event(item)
            # NOTE: the commented out code here is for enabling the ability to execute events. 

            # self.command = item
            # self.ui.build_event_btn.setDisabled(False)
            # self.ui.build_cmd_btn.setDisabled(True)
            self.ui.event_detail.clear()
            ret_type = QTreeWidgetItem(None, ["Returns", "", "object", "dict", "None"])
            args = QTreeWidgetItem(None, ["Arguments", "", "object", "dict", "None"])

            # if (item.ret_type is not None) and (len(item.ret_type.members) > 0):
            #     for ret in item.ret_type.members:
            #         arg_data = item.ret_type.members[ret]
            #         arg_item = build_data_type(ret, arg_data)
            #         ret_type.insertChild(0, arg_item)
            # else:
            #     ret_type.insertChild(0, QTreeWidgetItem(None, ["None", "", "", ""]))    
            
            if (item.args.members is not None) and (len(item.args.members) > 0):
                for arg in item.args.members:
                    arg_data = item.args.members[arg]
                    arg_item = build_data_type(arg, arg_data)
                    ret_type.insertChild(0, arg_item)
            else:
                ret_type.insertChild(0, QTreeWidgetItem(None, ["None", "", "", ""]))

            self.ui.event_detail.insertTopLevelItem(0, ret_type)
            # self.ui.event_detail.insertTopLevelItem(1, args)
            self.ui.event_detail.expandAll()
        else:
            pass

    def build_command(self):
        """
        Brings up the build command window
        """
        self.command_popup = CommandForm(self.command, self.monitor)
        self.command_popup.show()

    def dump_schema(self):
        """
        Dumps the QMP schema into a json file.
        """
        save_dialog = QFileDialog()
        file_name = save_dialog.getSaveFileName(self, 'Dump Schema', filter="*.json")[0] # this return a tuple of the name and filters
        if ".json" not in file_name: # add the extension if needed
            file_name += ".json"
        schema_dump = open(file_name,'w')
        json.dump(self.schema.raw_schema, schema_dump, indent=4)
        schema_dump.close()

        
def main():  # will be used as entry point for package when packaged for deployment
    app = QApplication(sys.argv)
    if (len(app.arguments()) > 1) and (app.arguments()[1] == "--debug"):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    