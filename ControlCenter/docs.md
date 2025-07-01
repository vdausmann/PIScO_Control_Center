# Documentation and development progress for Control-Center App 

The code of the app is split in the Backend and the Frontend. The Backend contains code
for the functionality of the app, i.e. the basic datatypes, task handling, etc., while the
Frontend only contains code for the visualization.


## Backend
The backend contains three basic datatypes:
1. Setting: A datatype that implements a single setting, i.e. name, type and current
   value.
2. Module: A module is a set of settings and a run command. It represents an external
   module which is called with the run command and provided with the settings. There are
   two types of settings in a module: external and internal. The external settings will be
   parsed to the external module, while the internal settings are only used within the 
   app.
3. Task: A task is a set of modules. The task is used to bundle modules which belong
   together, e.g. modules that are dependent on each other. Task also can be active or
   inactive. Only when a task is active the modules inside it will be started.

The TaskManager handles automatic starting of modules when available.
The Task and Module object each have signals for various states. Other objects can connect
to these signals which will emit data when the state changes.

### Settings
Possible setting types are:
   - StringSetting
   - IntSetting
   - DoubleSetting
   - BoolSetting
   - OptionSetting
   - FolderSetting
   - FileSetting

### Modules
A module can be in one of the following states:
   1. NotExecuted
   2. Running
   3. Finished
   4. Error
Each module has any number of external settings and two internal settings; the command and
the priority. The TaskManager sorts all modules with the state 'NotExecuted' from all
active tasks by their priority, executing the module with the highest priority first.
A module has two signals: the change_state_signal, which emits the state and a string upon
a state change, and the output_received_signal, which emits the output received by either
a stdout or stderror from a running module.


# TODO
- improve setting inheritance by e.g. a "&" in front followed by the name of the setting.
  If a module inherites a setting from another module, it should be automatically set to
  the same value as the other module but should still be overwriteable.
- repair app state writing
- adapt task, module and setting visualizations to the new system
