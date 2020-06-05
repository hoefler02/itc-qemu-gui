"""
"""
# pylint: disable=import-error
from qmp_ui import QmpCommand, QmpDataType, QmpEvent
from enum import Enum

class QmpType(Enum):
    COMMAND = 1
    EVENT = 2
    DATATYPE = 3

def build_command(command: QmpCommand):
    """
    """
    args = dict()
    for member in command.args.members:
        definition = command.args.members[member]
        if definition.meta_type == "object":
            print(member)

        elif definition.meta_type == "enum":
            valid = False
            while not valid:
                user_input = input("pick a value for {}: {}:> ".format(member, definition.values))
                if user_input in definition.values:
                    args[member] = user_input
                    valid = True
                else:
                    print("that was not an allowable value")
        elif definition.meta_type == "builtin":
            args[member] = definition.python_type(input(("{} ({}: {}):> ".format(member, definition.meta_type, str(definition.python_type)))))

        elif "array" in definition.meta_type:
            data = input(("{} ({}: {}):> ".format(member, definition.meta_type, str(definition.python_type))))
            data = data.split(" ")
            for i in range(len(data)):
                data[i] = definition.python_type(data[i])
            args[member] = data

    return {'execute': command.command, 'arguments': args}


def build_event(event: QmpEvent):
    """
    """
    return build_command(event)
