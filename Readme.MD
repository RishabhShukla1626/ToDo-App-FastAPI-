# Todos Application
This is a simple Todos application built using FastAPI. It allows users to create, read, update, and delete tasks to be done. The application uses PostgreSQL as its database and SQLAlchemy as the ORM library to communicate with the database.

## Tech Stack Used
**FastAPI:** a modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints.
**PostgreSQL:** a powerful, open-source object-relational database system known for its reliability, robustness, and ability to handle high volumes of data.
**SQLAlchemy:** a SQL toolkit and Object-Relational Mapping (ORM) library that provides a set of high-level API for connecting to relational databases and manipulating the data stored in them.
Running the Application
To run the application on your local machine, you need to follow these steps:

#### 1. Setting up the Environment
First, make sure you have pipenv installed on your machine. You can **install it using pip:**

    pip install pipenv
#### 2. Cloning the Repository
Next, clone the repository to your local machine:

    git clone https://github.com/TheDevCarnage/ToDo-App--FastAPI.git

cd ToDo
#### 3. Installing Dependencies
Install the dependencies using pipenv:

    pipenv install

#### 4. Setting Up the Database
Before running the application, you need to create a PostgreSQL database and set its URL in a .env file. Here's an example .env file:


    DATABASE_URL=postgresql://username:password@localhost/todoapp

Replace username and password with your PostgreSQL username and password, respectively. todoapp is the name of the database.

#### 5. Running the Application
To run the application in your local environment, activate the pipenv shell:

    pipenv shell

Then, change to the ToDo directory and run the FastAPI server using the uvicorn command:

    cd ToDo
    uvicorn main:app --reload

This will start the server on http://localhost:8000.

#### 6. Running the Application Using a Shell Script
Alternatively, you can use the provided entrypoint.sh shell script to start the application:


    #!/bin/bash

    # Activate the virtual environment
    source .venv/bin/activate

    # Change directory to the directory where your main file resides
    cd ToDo

    # Start the FastAPI server
    uvicorn main:app --reload
    Make the script executable:

**Change the permission to run the script**
    chmod +x entrypoint.sh

Then, run the script:

    ./entrypoint.sh

This will start the server on http://localhost:8000.