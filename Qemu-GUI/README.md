# Qemu GUI

A graphical interface for interacting with Qemu instances via QMP.

## User Guide

This is a rough prototype and primarily offers the ablities to view QMP Commands and Events, dump the current schema to a json file, and execute commands. In order to bring up the UI, you must first start the WFI ICDH Qemu container. The run the UI with debug info, pass the debug flag when calling it: python3 Qemu-GUI/qemu_gui/__init__.py --debug

### Schema Dump

To dump the qmp schema to a file, select 'file' from the menu bar, then 'Dump Schema'. You can then select a file to dump to.

### Command/Event Browser

In the main window, there is a tabbed interface with a 'Commands' and 'Events' tab. Either tab will display a list of commands or events respectively. When selected, the arguments and return structure for the command/event will be displayed in the right hand pane. If the selected
entity is a command, a button at the bottom of the right hand pane will allow you to 'build' the command. This brings up a UI form for construting a JSON string to send to the QMP server. Once all the fields all filled in, you can click the execute button. This will display the raw JSON that was sent to the QMP server and the response. Some item in the command form will have check boxes by them. these are "optional" fields and will not be included in the JSON that is sent unless the check box is checked and that field in enabled. The "optional" fields are defined as such in the QMP schema, but I have found that the command will fail in some cases because the a field was not actually optional.

### Prefernces

There is a preferences menu under Edit from the menu bar, the only functionality this currently provides is the ability to change the port and IP for the ICDH host. If for some reason the default connection info is wrong, causing the UI to crash due to the inablity to connect to a Qemu instance, you can moddify the settings files at ~/.qemu-gui/setting.json. This is a human readable file and should be easy to manually update.

## Todos

- Tags and variants are not considered currently when constructing a QMP Datatype, I also need to take a deeper look into should be considered. alternates work.
- For command building:
  - nested objects are not handled in generic manner and only allows for one level of nesting.
  - arrays are not handled in the command builder yet

### Notes

"variant members, i.e. additional members that depend on the type tag’s value. Present exactly when tag is present. The variants are in no particular order, and may even differ from the order of the values of the enum type of the tag. " - QMP Reference page

## Known Issues

Keeping track of what is wrong with QMP/the ui implementation. QMP has some interesting inconsistencies with datatype defs.

### Command Browser

Commands: Commands that fail due to QMP structure issues, missing args due to bad QMP defs, and my own mistakes.

- [X] migrate-set-parameters: fails due to an index out of bounds issue when getting a NoneType as a string on line 104 of
   qemu_gui __init__.py. Will probably have to use a try catch for this one.
- [X] query-block: fails due to issues with its return type (array of DataType 16, the issue lies within type '238')
- [X] query-blockstats: fails due to issues with its return type (array of DataType 18)
      this was fixed by updating the "dive" functionality of the QmpSchema's get_data_type function. The issue is '18' is recursively defined, so at some point the recursion has to be cut off and raw object type is returned (the object name '18')
- [X] query-named-block-nodes: fails due to issues with return type (array of DataType 28, the issue lies within '238')
- [ ] query-pci: stack overflow, there is a dependency loop defined in nested datatypes in the return object (array of 193).
- [X] x-blockdev-set-iothread: duplicate of migrate-set-parameters issue.

DataTypes: Types that fail to parse due to QMP stucture issues or my own mistakes

- '193':
    causes infinite recursion. This will need to be handled by creating a table of types that have already been explored potentially.

Other intersing types:

### Building Commands

Arrays and objects that are nested more than one level deep are not handled by the command builder UI. You can still build and send the command, but it will return a failed result.

Commands:

- [ ] chardev-change: appears to be improperly defined by the schema, missing "backend.data" param.

### Event Browser

None :D

### Event Builder

Commented out for now, working with the assuption that events are the result of commands and that events cannot be sent. Code exists to transmit events, but its just commented out.
