# TaskFlow Backend
This is a backend application to manage tasks using a PostgreSQL database with functionality for task creation, updating, deletion, and retrieval. The app supports pagination and persists data to ensure tasks are not lost after server restarts.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
  - [Create Task](#create-task)
  - [Get All Tasks](#get-all-tasks)
  - [Update Task Status](#update-task-status)
  - [Delete Task](#delete-task)
  - [Filter Tasks by Status](#filter-tasks-by-status)
- [Database Setup](#database-setup)
- [Data Persistence](#data-persistence)
- [Logging](#logging)

## Overview

The TaskFlow Backend application allows users to perform basic CRUD operations on tasks, including filtering tasks by status, and supports pagination for the `GET` tasks endpoint. Data is stored in a PostgreSQL database, and task data is persisted between server restarts.

## Installation

To get started with the project, follow these steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/shuklagaurav021/myclnq-tasks.git
   cd taskflow-backend
   ```
````

2. Install the required dependencies:

   ```bash
   npm install
   ```

3. Create a `.env` file in the root of the project to store environment variables.

### Example `.env` file:

```env
SERVICE_NAME='tasks'
PORT=3000
PG_USERNAME=myuser
PG_PASS=yourpassword
PG_DB_NAME=taskflow
PG_HOST=localhost
DATA_FILE=tasks.json
```

4. Set up the PostgreSQL database (instructions provided below).

## Configuration

The app uses environment variables to configure the PostgreSQL database connection and other settings.

- `SERVICE_NAME`: Name of the service.
- `PORT`: Port number for the Express server to run.
- `PG_USERNAME`: Username for the PostgreSQL database.
- `PG_PASS`: Password for the PostgreSQL database.
- `PG_DB_NAME`: Database name.
- `PG_HOST`: Host of the PostgreSQL database.
- `DATA_FILE`: Name of the JSON file used for data persistence (optional).

## API Endpoints

### 1. Create Task

- **Endpoint**: `POST /tasks`
- **Request Body**:
  ```json
  {
    "title": "Task title",
    "description": "Task description"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Task created successfully",
    "task": {
      "id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "status": "pending"
    }
  }
  ```

### 2. Get All Tasks (with Pagination)

- **Endpoint**: `GET /tasks`
- **Query Parameters**:
  - `page` (optional): The page number (default is 1).
  - `limit` (optional): The number of tasks per page (default is 10).
- **Response**:
  ```json
  {
    "data": [
      {
        "id": "uuid",
        "title": "Task title",
        "description": "Task description",
        "status": "pending"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "totalCount": 100,
      "totalPages": 10
    }
  }
  ```

### 3. Update Task Status

- **Endpoint**: `PUT /tasks/:id`
- **Request Body**:
  ```json
  {
    "status": "completed"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Task updated successfully",
    "task": {
      "id": "uuid",
      "title": "Task title",
      "description": "Task description",
      "status": "completed"
    }
  }
  ```

### 4. Delete Task

- **Endpoint**: `DELETE /tasks/:id`
- **Response**:
  ```json
  {
    "message": "Task deleted successfully"
  }
  ```

### 5. Filter Tasks by Status

- **Endpoint**: `GET /tasks/status/:status`
- **Path Parameter**:
  - `status`: The status of the tasks to filter by (`pending` or `completed`).
- **Response**:
  ```json
  {
    "data": [
      {
        "id": "uuid",
        "title": "Task title",
        "description": "Task description",
        "status": "pending"
      }
    ]
  }
  ```

## Database Setup

To run the application, you'll need PostgreSQL set up. Follow these steps:

1. Install PostgreSQL on your system.
2. Create a new database:
   ```sql
   CREATE DATABASE taskflow;
   ```
3. Create the necessary table for storing tasks:

   ```sql
   CREATE TABLE tasks (
     id UUID PRIMARY KEY,
     title VARCHAR(255) NOT NULL,
     description TEXT NOT NULL,
     status VARCHAR(20) DEFAULT 'pending'
   );
   ```

4. Update your `.env` file with your PostgreSQL credentials.

## Data Persistence

By default, the application uses PostgreSQL for data persistence. However, if PostgreSQL is not available, you can opt to store data in a JSON file. The JSON file will be used to persist tasks and allow the data to survive server restarts.

- `tasks.json`: This file will store all tasks if you prefer file-based persistence.

## Logging

This project uses the `winston` logging library for structured logging. Logs will be output to the console during runtime, and errors are captured to help in debugging.

## License

MIT License. See [LICENSE](LICENSE) for more information.

---

Feel free to copy and paste this README into your project directory!
