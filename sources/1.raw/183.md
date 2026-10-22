---
  layout: default.md
  title: "TalentMatch Logging Guide"
---

# TalentMatch Logging Guide

* TalentMatch uses the `java.util.logging` package for logging.
* The `LogsCenter` class is used to manage the logging levels and logging destinations.
* The `Logger` for a class can be obtained using `LogsCenter.getLogger(Class)` which will log messages according to the specified logging level.
* Log messages are output through the console and to a `.log` file.
* The output logging level can be controlled using the `logLevel` setting in the configuration file (See the [Configuration guide](Configuration.md) section).
* **When choosing a level for a log message**, follow the conventions given in [_[se-edu/guides] Java: Logging conventions_](https://se-education.org/guides/conventions/java/logging.html).

## TalentMatch-Specific Logging

### Key Components to Log

TalentMatch logs important events in these key components:

* **ModelManager**: Log changes to application data (persons, jobs, applications)
* **LogicManager**: Log command execution and parsing
* **StorageManager**: Log data saving and loading operations
* **UiManager**: Log UI initialization and updates

### Logging Levels for TalentMatch Components

* **SEVERE**: System failures, data corruption, or critical errors that prevent core functionality
* **WARNING**: Potential issues with data integrity or user errors
* **INFO**: Major user operations (add/edit/delete persons, jobs, or applications)
* **FINE**: Detailed information about command execution and data processing
* **FINER/FINEST**: Highly detailed debugging information for troubleshooting

### Example Logging Statements

```java
// Example for LogicManager when parsing a command
private static final Logger logger = LogsCenter.getLogger(LogicManager.class);
// ...
logger.info("Command word: " + commandWord + "; Arguments: " + arguments);

// Example for ModelManager when adding a person
private static final Logger logger = LogsCenter.getLogger(ModelManager.class);
// ...
logger.info("Adding person: " + person.getName());

// Example for StorageManager when saving data
private static final Logger logger = LogsCenter.getLogger(StorageManager.class);
// ...
logger.fine("Attempting to write to data file: " + filePath);
```

### Debugging TalentMatch

When troubleshooting issues with TalentMatch:

1. Set the logging level to `FINE` or `FINER` in `config.json` to see detailed execution flow
2. Check the `.log` file for error stacktraces and warnings
3. Pay special attention to logs from the component where issues are suspected
4. Look for errors in job-application relationship management and view state transitions

Logs are especially useful for diagnosing issues related to:
* Command parsing errors
* Data persistence problems
* Application status transitions
* Relationship management between persons, jobs, and applications
