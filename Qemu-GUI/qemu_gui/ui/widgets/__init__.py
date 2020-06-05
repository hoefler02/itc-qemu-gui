from PySide2.QtWidgets import *
from PySide2.QtGui import QPixmap                                           # pylint: disable=no-name-in-module
from PySide2.QtCore import Qt                                               # pylint: disable=no-name-in-module


from qmp_ui import QmpCommand, QmpDataType                                  # pylint: disable=import-error
from qmp_ui.utils import build_command                                      # pylint: disable=import-error
from pyqmp import QEMUMonitorProtocol 

import ui.compiled.resources_rc                                             # pylint: disable=import-error
from ui.compiled.preferences_ui import Ui_Preferences                       # pylint: disable=import-error

from app_utils.settings import SettingsJSON

import json
import logging
logger = logging.getLogger(__name__)

def toggle_disabled(input_widget: QWidget) -> None:                          # pylint: disable=undefined-variable
    """
    Toggle a widget's enabled value.

    :param input_widget: widget to toggle
    :type input_widget: QWidget
    """
    if input_widget.isEnabled():
        input_widget.setDisabled(True)
    else:
        input_widget.setDisabled(False)


class CommandForm(QWidget):                                                     # pylint: disable=undefined-variable
    """
    A dynamcially generated form for constructing and issues commands over QMP.

    :param command: The commmand data structure
    :type command: QmpCommand
    :param monitor: Connection to the QMP server.
    :type monitor: QEMUMonitorProtocol
    """
    def __init__(self, command: QmpCommand, monitor: QEMUMonitorProtocol):
        QWidget.__init__(self)                                                  # pylint: disable=undefined-variable
        self.setWindowTitle(command.command + " Command")
        self.setMinimumWidth(500)
        self.setWindowIcon(QPixmap(":/images/qemu.png"))
        self.command = command
        self.monitor = monitor
        self.inputs = dict()  # used to get the input values later on
        self.nested = dict()  # used to map for the final json command string

        # nested function because why not
        def build_input_row(arg_name: str, arg: QmpDataType, nested: str = None) -> QHBoxLayout:    # pylint: disable=undefined-variable
            """
            Dynamically generates an input row for building command input forms. Should be considered private to CommandForm Constructor.

            :param arg_name: name of the arg, used as the label
            :param arg: the arg data structure, used to determine the proper input field types, params, etc.
            :param nested: helps keep track of the JSON structure for executing the command by tracking nested objects
            """
            input_layout = QFormLayout()                                      # pylint: disable=undefined-variable
            if arg.optional:
                label = QCheckBox(arg_name)                                    # pylint: disable=undefined-variable
            else:
                label = QLabel(arg_name)                                       # pylint: disable=undefined-variable
            field_class = None
            if arg.meta_type == "object":
                # this will be nested, start a new vertical layout
                nested_vbox = QVBoxLayout()                                     # pylint: disable=undefined-variable
                
                for memeber in arg.members:
                    nested_vbox.addLayout(build_input_row(memeber, arg.members[memeber]))
                    self.nested[memeber] = arg_name # used to map for fields to objects in final json command string
                input_layout.addRow(label, nested_vbox)                
                return input_layout

            # otherwise we should not need to nest objects, except for arrays potentially
            elif arg.meta_type == "enum":
                input_field = QComboBox()                                      # pylint: disable=undefined-variable
                input_field.addItems(arg.values)
                field_class = QComboBox                                         # pylint: disable=undefined-variable
            elif arg.meta_type == "builtin":
                if arg.python_type == int:
                    input_field = QSpinBox()                                    # pylint: disable=undefined-variable
                    field_class = QSpinBox                                      # pylint: disable=undefined-variable
                elif arg.python_type == str:
                    input_field = QLineEdit()                                   # pylint: disable=undefined-variable
                    field_class = QLineEdit                                     # pylint: disable=undefined-variable
                elif arg.python_type == bool:
                    input_field = QCheckBox()                                   # pylint: disable=undefined-variable
                    field_class = QCheckBox                                     # pylint: disable=undefined-variable
                else:
                    logger.debug("Uncaught builtin: {}".format(str(arg)))
                    input_field = QLineEdit()                                   # pylint: disable=undefined-variable            
            elif "array" in arg.meta_type:
                #TODO Handle arrays
                logger.debug("Array arg: {}".format(str(arg)))
                input_field = QLineEdit()                                       # pylint: disable=undefined-variable
                field_class = QLineEdit                                         # pylint: disable=undefined-variable
                print(arg)
                # this is probably going to need to be
                # a button for adding and removing new
                # entries. Probably need to write 
                # a custom widget

            else:
                logger.debug("Uncaught type: {}".format(str(arg)))
                #TODO Handle uncaught (if any)
                input_field = QLineEdit()                                       # pylint: disable=undefined-variable
                field_class = QLineEdit                                         # pylint: disable=undefined-variable

            input_field.setObjectName(arg_name )
            self.inputs[arg_name] = field_class  # store the field name and type for dynamic extraction
            if isinstance(label, QCheckBox):                                    # pylint: disable=undefined-variable
                input_field.setDisabled(True)
                label.stateChanged.connect(lambda: toggle_disabled(input_field))
            input_layout.addRow(label, input_field)
            return input_layout

        vbox = QVBoxLayout() # pylint: disable=undefined-variable
        form_vbox = QVBoxLayout() # pylint: disable=undefined-variable
        button_hbox = QHBoxLayout() # pylint: disable=undefined-variable
        for arg in command.args.members:
            raw_arg = command.args.members[arg]
            form_vbox.addLayout(build_input_row(arg, raw_arg))
        execute_button = QPushButton("Execute") # pylint: disable=undefined-variable
        execute_button.clicked.connect(self.execute)
        button_hbox.addWidget(execute_button)  # TODO might not need an hbox, this will probably only be one button
        form_vbox.addStretch()
        vbox.addLayout(form_vbox)
        vbox.addLayout(button_hbox)
        widget = QWidget() # pylint: disable=undefined-variable
        widget.setLayout(vbox)
        scroll_area = QScrollArea() # pylint: disable=undefined-variable
        scroll_area.setMinimumHeight(300)
        scroll_area.setMaximumHeight(600)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidget(widget)
        master_vbox = QVBoxLayout() # pylint: disable=undefined-variable
        master_vbox.addWidget(scroll_area)
        self.setLayout(master_vbox)

    def execute(self):
        """
        Executes the command by compiling user input into a JSON string and sending it to the QMP server.
        Results and the raw JSON string are displayed in the command form window.
        """
        logger.debug("============== Execute {} ===============".format(self.command.command))
        command_json = dict()
        command_args = dict()
        # TODO does not handle nested objects of multiple levels

        #build dicts for nested entries
        for item in self.nested:
            command_args[self.nested[item]] = dict()
        for item in self.inputs:
            item_class = self.inputs[item]
            nested = item in self.nested
            child = self.findChild(item_class, item) # item class, item name
            if not child.isEnabled():
                continue
            if item_class == QComboBox: # pylint: disable=undefined-variable
                if nested:
                    # getting self.nested[item] gets that item's parent
                    command_args[self.nested[item]][item] = child.currentText()
                else:
                    command_args[item] = child.currentText()
            elif item_class == QSpinBox: # pylint: disable=undefined-variable
                if nested:
                    command_args[self.nested[item]][item] = child.value()
                else:
                    command_args[item] = child.value()
            elif item_class == QLineEdit: # pylint: disable=undefined-variable
                if nested:
                    command_args[self.nested[item]][item] = child.text()
                else:
                    command_args[item] = child.text()
            elif item_class == QCheckBox: # pylint: disable=undefined-variable
                if nested:
                    command_args[self.nested[item]][item] = child.isChecked()
                else:
                    command_args[item] = child.isChecked()
            # logger.debug("{}: {}{}".format(item, command_args[item], type(command_args[item])))

        command_json['execute'] = self.command.command
        command_json['arguments'] = command_args
        logger.debug(str(command_json))
        result = self.monitor.cmd_obj(command_json)
        logger.debug(result)
        logger.debug("============== End {} ===============".format(self.command.command))
        # raw cmd json
        if self.findChild(QTextBrowser, "cmd_json_field") is not None: # pylint: disable=undefined-variable
            self.findChild(QTextBrowser, "cmd_json_field").setText(json.dumps(command_json, indent=4)) # pylint: disable=undefined-variable
        else:
            cmd_label = QLabel("Command JSON") # pylint: disable=undefined-variable
            cmd_text = QTextBrowser() # pylint: disable=undefined-variable
            cmd_text.setObjectName("cmd_json_field")
            cmd_text.setMinimumHeight(200)
            cmd_text.setText(json.dumps(command_json, indent=4))
            self.layout().addWidget(cmd_label)
            self.layout().addWidget(cmd_text)

        # raw output json
        if self.findChild(QTextBrowser, "results_field") is not None: # pylint: disable=undefined-variable
            self.findChild(QTextBrowser, "results_field").setText(json.dumps(result, indent=4)) # pylint: disable=undefined-variable
        else:
            result_label = QLabel("Result JSON") # pylint: disable=undefined-variable
            result_text = QTextBrowser() # pylint: disable=undefined-variable
            result_text.setObjectName("results_field")
            result_text.setMinimumHeight(200)
            result_text.setText(json.dumps(result, indent=4))
            self.layout().addWidget(result_label)
            self.layout().addWidget(result_text)

class PreferencesWidget(QWidget): # pylint: disable=undefined-variable
    """
    Settings ui. Build ui dynamically based on entries in the application settings json file.

    :param settings: Settings object from the main window.
    """
    def __init__(self, settings: SettingsJSON):

        QWidget.__init__(self) # pylint: disable=undefined-variable
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.settings_object = settings

        # action mapping
        self.ui.preferences_list.itemClicked.connect(self.__handle_settings_display)

        # default to displaying the host settings
        self.ui.preferences_list.setCurrentRow(1)
        self.__handle_settings_display(self.ui.preferences_list.currentItem())

    def __handle_settings_display(self, item):
        # remove the current layout by assigning it to someone else
        QWidget().setLayout(self.ui.detail_widget.layout()) # pylint: disable=undefined-variable
        logger.debug("{} selected".format(item.text()))
        if item.text() == "General":
            self.__display_general_settings()
        elif item.text() == "Qemu Hosts":
            self.__display_host_settings()

    def __display_host_settings(self):
        """
        Display settings details for Qemu Hosts
        """
        def save():
            """
            Applies settings updates and writes them to a file
            """
            hosts = self.settings_object.settings['Qemu Hosts']
            new_settings = dict()
            new_settings['default'] = self.ui.detail_widget.findChild(QComboBox, 'default_host').currentText() # pylint: disable=undefined-variable
            for host in hosts:
                if host == "default":
                    continue
                new_settings[host] = {
                    "port": self.ui.detail_widget.findChild(QSpinBox, '{}_port'.format(host)).value(), # pylint: disable=undefined-variable
                    "host": self.ui.detail_widget.findChild(QLineEdit, '{}_host'.format(host)).text(), # pylint: disable=undefined-variable
                    }
            logging.debug("Old Settings: {}".format(str(hosts)))
            logging.debug("New Settings: {}".format(str(new_settings)))
            self.settings_object.set_setting("Qemu Hosts", new_settings) 
            alert = QMessageBox(self) # pylint: disable=undefined-variable
            alert.setWindowTitle("Settings Changed")
            alert.setText("Settings Saved!")
            alert.show()            

        hosts = self.settings_object.settings['Qemu Hosts'] 
        default_select_hbox = QHBoxLayout() # pylint: disable=undefined-variable
        default_select_hbox.addWidget(QLabel("Default")) # pylint: disable=undefined-variable
        default_combo = QComboBox() # pylint: disable=undefined-variable
        items = list(hosts.keys())
        items.remove("default")
        default_combo.addItems(items)
        default_combo.setObjectName("default_host")
        default_select_hbox.addWidget(default_combo)
        vbox = QVBoxLayout() # pylint: disable=undefined-variable
        vbox.addLayout(default_select_hbox)
        for host in hosts:
            if host == "default":
                continue
            form = QFormLayout() # pylint: disable=undefined-variable
            options_vbox = QVBoxLayout() # pylint: disable=undefined-variable

            port_field = QSpinBox() # pylint: disable=undefined-variable
            port_field.setObjectName("{}_port".format(host))
            port_field.setMaximum(65535)
            port_field.setValue(hosts[host]["port"])

            host_field = QLineEdit() # pylint: disable=undefined-variable
            host_field.setText(hosts[host]["host"])
            host_field.setObjectName("{}_host".format(host))


            options_vbox.addWidget(port_field)
            options_vbox.addWidget(host_field)
            form.addRow(QLabel(host), options_vbox)  # pylint: disable=undefined-variable
            vbox.addLayout(form)

            save_btn = QPushButton("Save") # pylint: disable=undefined-variable
            save_btn.clicked.connect(save)
            vbox.addWidget(save_btn)
        
        self.ui.detail_widget.setLayout(vbox)

    def __display_general_settings(self):
        # TODO not a priority, 
        pass

        
        