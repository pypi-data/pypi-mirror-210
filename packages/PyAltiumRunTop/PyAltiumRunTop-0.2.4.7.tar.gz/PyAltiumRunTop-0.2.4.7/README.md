PyAltiumRun

[![PyPI version](https://badgen.net/pypi/v/PyAltiumRunTop)](https://pypi.org/project/PyAltiumRunTop/)  [![PyPI version](https://badgen.net/pypi/license/PyAltiumRunTop)](https://github.com/krakdustten/PyAltiumRun/blob/master/LICENSE) [![PyPI version](https://badgen.net/pypi/python/PyAltiumRunTop)](https://pypi.org/project/PyAltiumRunTop/)

A Python interface that can run Delphiscript  in [Altium Designer](https://www.altium.com/).

New features can be requested in the [Github Issues](https://github.com/krakdustten/PyAltiumRun/issues).

## Update 
Fix bug log_str
## Add 
Add Parameter Pas File

## Installation requirements

Altium designer must be installed before running this library.

## Quick start
```shell script
pip install PyAltiumRunTop
```
~~~python
from PyAltiumRunTop.AltiumRun import AltiumRun

run = AltiumRun(use_internal_logger=True)                       #Create runner object
run.clear_log_file()                                            #Clear the logs of the previous run
run.set_project_to_open(r"Altium_project/Arduino_uno.PrjPcb")   #Define an Altium project to open
run.add_script(r"Altium_scripts/generate_docs.pas")             #Add a script to the runner
run.set_function("gen_docs", "Arduino_uno")                     #Set the function to run
run.run()                                                       #Run
~~~

## Delphi addons

These are the delphi script addons created.

### Logger

For this module to work the "use_internal_logger" parameter of the runner constructor should be True.

This module creates a log file in the data folder under the scripting project.
It logs everything in the following format:

~~~
[DAY/MONTH/YEAR HOUR:MINUTE:SECOND:MILISECOND]: LOGGED_STRING
~~~

Resulting in a log that looks like this:

~~~
[09/01/22 10:53:30.573]: Starting script
[09/01/22 10:53:30.576]: Opening project: Altium_project/Arduino_uno.PrjPcb
[09/01/22 10:53:30.657]: Arduino_uno
~~~
