import json
from pyqmp import QEMUMonitorProtocol
# pylint: disable=import-error
from qmp_ui.exceptions import *
import sys

import logging

logger = logging.getLogger(__name__)


class QmpCommand:
    """
    Data Wrapper for QMP Commands

    :param command: QMP recognized command string
    :type command: str
    :param ret_type: QMP return type definition
    :type ret_type: QmpDataType
    :param args: QMP command argument definition
    :type args: QmpDataType
    """
    def __init__(self, command: str, ret_type: 'QmpDataType', args: 'QmpDataType'):
        self.command = command
        self.ret_type = ret_type
        self.args = args

    def __str__(self):
        return "command:{}, ret_type: <{}>, args: <{}>".format(self.command, self.ret_type, self.args)

    def __repr__(self):
        return self.__str__()

class QmpDataType:
    """
    Data Wrapper for QMP Data Types

    :param name: QMP Data Type name string
    :type name: str
    :param meta_type: QMP meta-type
    :type meta_type: str
    :param python_type: the corresponding Python data type
    :type python_type: callable
    :param values: list of acceptable values
    :type values: list
    :param members: dictionary of nested member QmpDataTypes
    :type members: dict
    :param optional: whether or not this type is optional
    :type optional: bool 
    """
    def __init__(self, name: str, meta_type: str, python_type: callable, values: list=None, members: dict=None, optional: bool=False):
        self.name = name
        self.meta_type = meta_type
        self.python_type = python_type
        self.values = values
        self.members = members
        self.optional = optional

    def __str__(self):
        return("name: {}, meta_type: {}, python_type: {}, values: {}, members: {}".format(self.name, 
                                                                                          self.meta_type, 
                                                                                          self.python_type, 
                                                                                          self.values, 
                                                                                          self.members))

    def __repr__(self):
        return self.__str__()

class QmpEvent(QmpCommand):
    """
    Data Wrapper for QMP Events

    :param event: QMP recognized event string
    :type event: str
    :param ret_type: QMP return type definition
    :type ret_type: QmpDataType
    :param args: QMP event argument definition
    :type args: QmpDataType
    """
    def __init__(self, command: str, ret_type: 'QmpDataType', args: 'QmpDataType'):
        super().__init__(command, ret_type, args=args)

class QmpSchema:
    """
    Abstraction layer for dynamically generating all supported QMP commands.

    :param qmp_schema_dict: QMP Schema provided by the QMP Python library.
    :type qmp_schema_dict: dict
    """

    def __init__(self, qmp_schema_dict: dict):
        self.commands = dict()
        self.types = dict() # TODO a get method
        self.events = dict()

        self.raw_schema = qmp_schema_dict['return'] # strip off the return wrapper
        for item in self.raw_schema:
            if item['meta-type'] == 'command':
                self.commands[item['name']] = item
            elif item['meta-type'] == 'event':
                self.events[item['name']] = item
            else:
                self.types[item['name']] = item
        
    def __get_data_type(self, qmp_type: str, dive: bool = True, optional: bool = False) -> 'QmpDataType':
        """
        Private method for generating the QmpDataTypes for a QmpCommand.

        :param qmp_type: The QMP defined data type of the object
        :type qmp_type: str
        :param dive: wether or not to allow recursion into another type with the same meta-type as the current object. Defaults to true.
        :type dive: bool
        :param optional: whether or not the current item is optional
        :type optional: bool
        :returns: a QmpDataType representation of the object.
        :rtype: QmpDataType
        """

        try:
            raw_type = self.types[qmp_type]
            name = raw_type['name']
            meta = raw_type['meta-type']
            python_type = str
            values = None
            members = None
            mark_optional = False

            logger.debug(str(raw_type))

            
            if 'members' in raw_type: # this should occur if the meta-type is object
                python_type = dict
                members = dict()
                for member in raw_type['members']:
                    logger.debug("Object: {} ---> Member: {}".format(name, member))
                    if 'default' in member:
                        mark_optional = True
                    if member['type'] == name: # this object is recursively defined within itself
                        if dive:
                            members[member['name']] = self.__get_data_type(member['type'], dive=False, optional=mark_optional)  # only go one more deep
                        else: # return a bare QmpDataType
                            members[member['name']] = QmpDataType(member['name'], member['type'], python_type, values=values, members=None, optional=optional) # patch with none, this causes a lot of issues for me
                    else:
                        if 'name' in member:
                            members[member['name']] = self.__get_data_type(member['type'], optional=mark_optional)  # recursively get the types
                        else:
                            logger.debug("The problem child ----> {}".format(member))
                            members[raw_type['meta-type']] = self.__get_data_type(member['type'], optional=mark_optional)  # recursively get the types

            # determine the python class of the object
            if meta == 'enum':
                values = raw_type['values']

                # we defaulted to type str, so noting to do for python type
            elif meta == "builtin":
                if name == "number":
                    name = "int"
                elif name == "null":
                    name = "None"
                python_type = getattr(sys.modules["builtins"], name)

            elif meta == "array": # this is a type of list
                meta = raw_type['element-type']
                if meta not in ['str', 'int', 'bool']:
                    members = dict() 
                    members['elements'] = self.__get_data_type(meta)
                    meta = members['elements'].meta_type
                    python_type = list
                    logger.debug("Complex Array detected:\n\tElements: {}\n\tMeta: {}".format(members, meta))
                elif meta == "number":
                    meta = 'int'
                    python_type = int
                else: # builtin python type
                    python_type = python_type = getattr(sys.modules["builtins"], meta)
                meta += " array"
            
            return QmpDataType(name, meta, python_type, values=values, members=members, optional=optional)
        except KeyError:
            # pylint: disable=undefined-variable
            raise QmpTypeNotFound("Type '{}' not found".format(qmp_type))

    def get_command(self, command: str) -> 'QmpCommand':
        """
        Builds a QmpCommand object for a named command. If the command does not exist
        in the QMP Schema, a QmpCommandNotFound exception is raised.

        :param command: name of the command
        :type command: str
        :returns: The command object
        :rtype: QmpCommand
        """
        try:
            raw_cmd = self.commands[command]
            cmd = raw_cmd['name']

            # some commads return nothing, if there is no ret-type key there is no value.
            if 'ret-type' in raw_cmd: 
                logger.debug("===================== Return Object for {} =====================".format(cmd))
                ret_type = self.__get_data_type(raw_cmd['ret-type'])
                logger.debug("===================== Return Object End =====================")
            else:
                ret_type = None

            # build the arguments
            logger.debug("===================== Args Object for {} =====================".format(cmd))
            args = self.__get_data_type(raw_cmd["arg-type"])
            logger.debug("===================== Args Object End =====================")

            return QmpCommand(cmd, ret_type, args=args)

        except KeyError:
            # pylint: disable=undefined-variable
            raise QmpCommandNotFound("'{}' is not a recognized command".format(command))

    def get_commands(self) -> set:
        """
        Get the list of available commands.

        :returns: All QMP commands.
        :rtype: list
        """
        return set(self.commands.keys())

    def get_event(self, event: str):
        """
        Builds a QmpEvent object for a named event. If the event does not exist
        in the QMP Schema, a QmpEventNotFound exception is raised.

        :param event: name of the event
        :type event: str
        :returns: The event object
        :rtype: QmpEvent
        """
        try:
            raw_event = self.events[event]
            event_name = raw_event['name']

            # some commads return nothing, if there is no ret-type key there is no value.
            if 'ret-type' in raw_event:
                logger.debug("===================== Return Object for {} =====================".format(event_name))
                ret_type = self.__get_data_type(raw_event['ret-type'])
                logger.debug("===================== Return Object End =====================")
            else:
                ret_type = None

            # build the arguments
            logger.debug("===================== Args Object for {} =====================".format(event_name))
            args = self.__get_data_type(raw_event["arg-type"])
            logger.debug("===================== Args Object End =====================")
            

            return QmpEvent(event_name, ret_type, args=args)

        except KeyError:
            # pylint: disable=undefined-variable
            raise QmpCommandNotFound("'{}' is not a recognized event".format(event))

    def get_events(self) -> set:
        """
        Get the list of available events.

        :returns: All QMP Events.
        :rtype: set
        """
        return set(self.events.keys())
