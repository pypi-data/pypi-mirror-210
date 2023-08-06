# **Anastasia Logging** #

This repository holds a logging implementation wrapper for python scripts with standarized code notifications and additional features.

## **Summary** ##

1. About *logging* python library
2. Enhancements and additional functionalities
    1. Log Output Standarization
    2. Predefined Parameters for AnastasiaLoggers from Environment Variables
    3. Code Tags Standarization
    4. Print Functionality
3. Versioning

## **1. About *logging* Python Library** ##

This repository is based in python base log management library called [logging](https://docs.python.org/3/library/logging.html).

Commonly, when this library is intended to be used, for a basic usage a simple logging import is recommended to be used in order to avoid additional settings in our internal scripts.

```
import logging

logging.warning("I am a very usefull warning")

OUTPUT => WARNING:root:I am a very usefull warning
```

But, for more complex repositories, is recommended to manage different loggers according to their necessities. For a customized logging behaviour, a Logger class must be declared from logging.

```
import logging

logger = logging.Logger("custom_logger")
logger.warning("I am a very usefull warning")

OUTPUT => I am a very usefull warning
```

Have you noticed in the first import logging example that appears the word *root* in the output console? This is because when you use ```import logging``` directly, a default Logger class is instanciated with name *root* along with default configurations.

This repository contains a class called **AnastasiaLogger**, which inherits from Logger class and standarize logging definitions and has some improvments over debugging (```.debug()```), information (```.info()```), warning (```.warning()```), error (```.error()```), critical (```.critical()```) and fatal (```.fatal()```) methods.

```
from anastasia_logging import AnastasiaLogger

logger = AnastasiaLogger()
logger.warning("I am a very usefull warning")

OUTPUT => 2023-05-08 10:39:17 UTC/GMT-0400 | [ANASTASIA-JOB] WARNING: I am a very usefull warning
```

If a script already has a logging usage, it is possible to replace ```import logging``` with ```import anastasia_logging as logging``` and no modifications are required from the script side to work!

```
import anastasia_logging as logging

logging.warning("I am a very usefull warning")

OUTPUT => 2023-05-08 10:39:17 UTC/GMT-0400 | [ANASTASIA-JOB] WARNING: I am a very usefull warning
```

## **2. Enhancements and Additional Functionalities** ##

### **2.1 Log Output Standarization** ###

AnastasiaLogger has a common structure in order to show information, which is the following one:
```
YYYY-MM-DD HR:MN:SS UTC/GMT(+-)HHMN | [TAG] LEVEL: message
```
TAG is define by default as ANASTASIA-JOB (can be changed during class instantiation), and LEVEL is defined according to level method called.

TAG is intended to differentiate responsabilities along scripts in other repositories.

### **2.2 Predefined Parameters for AnastasiaLoggers from Environment Variables** ###

For a faster logging behaviour along an entire repository, some variables that AnastasiaLogger can recieve can be predefined as environment variables, which are:

* ```ANASTASIA_LOG_NAME```: name identification of logger instance (default=```"anastasia-log"```)
* ```ANASTASIA_LOG_TAG```: tag identification for job type for StreamHandlers (console) and FileHandlers (file) (default=```"ANASTASIA-JOB"```)
* ```ANASTASIA_LOG_LEVEL```: define severity hierarchy for log generation (default=```"INFO"```)
* ```ANASTASIA_LOG_SAVELOG```: generate ```.log``` file containing logs generated (default=```"0"``` (deactivated))
* ```ANASTASIA_LOG_PATH```: define a custom name for log file (default=```"anastasia-log.log"```)

If it is not the case, AnastasiaLogger will instanciate with default parameters.

### **2.3 Code Tags Standarization** ###

In order to have a common identification for upper level implementations, AnastasiaLogger holds a standarized code implementations according to different topics.

The coding structure is the following one:

| **Code** 	|         **Topic**      	|
|:---------:|:-------------------------:|
|     0    	|       Unindentified       |
|    1XX   	|       Data related      	|
|    2XX   	|   Mathematical related    |
|    3XX   	|        AI related         |
|    4XX   	|     Resources related 	|
|    5XX   	| Operative System related 	|
|    6XX   	|       API related         |
|    7XX   	|       AWS related         |

Methods ```debug()```, ```info()```, ```warning()```, ```error()```, ```critical()``` and ```fatal()``` can be declared with a code as parameter in order to extended log with a code description.

```
import anastasia_logging as logging

logging.warning("I am a dataset warning", 100)

OUTPUT => 2023-05-08 11:55:27 UTC/GMT-0400 | [ANASTASIA-JOB] WARNING: <W100> I am a dataset warning
```

If a code is already predefined and no message is introduced, a default message will appear according to code declared.

### **2.4 Print Functionality** ###

For a easy visualization in console without interacting with an AnastasiaLogger, you can use ```print``` like a python built-in print call.

```
import anastasia_logging as logging

logging.print("Some prints to show")

OUTPUT => 2023-05-08 11:55:27 UTC/GMT-0400 | [ANASTASIA-JOB] PRINT: Some prints to show
```

## **3. Versioning** ##

### v1.3.4 ###

* Fixes:

    * Fixed edge cases in ```ANASTASIA_LOG_LEVEL``` and ```ANASTASIA_LOG_PATH``` assiganation values

### v1.3.3 ###

* Fixes:

    * Fixed edge case of ```ANASTASIA_LOG_SAVELOG``` environment variable detection if value entered is not a digit

### v1.3.2 ###

* Fixes:

    * Fixed parameter assignation for ```ANASTASIA_LOG_SAVELOG``` environment variable

### v1.3.1 ###

* Fixes:

    * Default unindentified ```debug```, ```critical``` and ```fatal``` standard codes fixed

### v1.3.0 ###

* Features:

    * Functions ```critical```, ```fatal``` and ```debug``` incorporated

### v1.2.0 ###

* Features:

    * Function ```print``` incorporated
    * Functions ```info```, ```warning```, ```error``` and ```print``` can return the formatted message for further usage

### v1.1.1 ###

* Fixes:

    * Function ```basicConfig``` was skipping predefined structures with tags and log streamhandlers

### v1.1.0 ###

* Features:

    * Function ```basicConfig``` equivalent from logging implemented for root AnastasiaLogger

### v1.0.0 ###

* Features:

    * ```AnastasiaLogger``` Class abstraction
    * Standar code description definitions for ```INFO```, ```WARNING``` and ```ERROR```
    * Predefined ```AnastasiaLogger``` parameters loaded from environment variables