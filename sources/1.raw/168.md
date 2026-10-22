# Logging Guide

We are using the `java.util.logging` package for logging within this project.

## Obtaining Loggers
Each class can obtain its `Logger` using `LogsCenter.getLogger(Class)`, which configures log messages according to the specified logging level.

## Log Output
Log messages are sent to both the console and a designated `.log` file, ensuring that logging data is accessible in real-time and for later review.

## Logging Levels
This project uses multiple log levels to categorize the types of messages logged:

- **INFO**: Used for general messages that indicate the normal flow of the application, like the creation of objects (e.g., "MealList created with an empty list").
- **WARNING**: Employed when handling errors or potentially problematic situations, such as invalid input indices (e.g., logging a warning when an invalid index is passed to delete a meal).
- **SEVERE**: Not yet observed in the provided code, but typically reserved for serious issues that might prevent the application from continuing.
- **DEBUG/FINER**: While not explicitly used in the examples provided, can be added for more granular traceability, especially in methods with complex logic or decision paths.

## Logging Conventions and Examples

- **Action Logging**: Each action in critical methods, such as adding or deleting entries (e.g., meals or exercises), is logged to track user interactions and changes in data.
- **Validation Logging**: Log messages are used when inputs are validated, ensuring that any issues with input values are easily traceable.
- **Return Value Logging**: Methods that perform key actions often log the outcomes, such as the final list of entries after additions or deletions. This practice makes it easier to verify that operations are completing as expected.

## Best Practices for Logging

- When logging at **INFO** level, focus on messages that reflect major steps or state changes within the application, helping to provide a high-level overview.
- Use **WARNING** level logging to capture recoverable issues or cases where an action does not proceed as expected.
- Add **SEVERE** logging if you introduce error-handling for critical failures.

For guidance on log message formatting and additional logging practices, refer to [Java: Logging conventions](https://github.com/se-edu/guides).