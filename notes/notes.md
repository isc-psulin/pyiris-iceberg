Move the features section to the Readme. This is here as a temp local only file.

## Features


## TODO
 - [ ] Add entry point to using JSON based config
 - [ ] Add option to use pyodbc
   - [x] odbc now being use
   - [ ] make odbc an option in the config
 - [ ] Move the logging initialization out of IRISIceberg
   - [ ] There probably needs to be one utils level logger that can be used by all modules in a single process and then a logger can be created for each job that runs on a sperate process
 - [x] Run initial performance tests from local to local and azure replicating 500MB
 - [ ] Tracking
   - [ ] Create the job when job starts and add this job id to all logs
   - [ ] Convert the current Job table to a Job steps table - 
   - [x] Add serialization of all data transfers for retries and reporting\
   - [ ] Add rate of data read and write to tracking in records/sec and mb/sec
   - [ ] Hash and save the hash and raw config to the job table
 - Modify tests to run from new dirs
   - [x] Changed dir structure
   - [ ] change to use fixtures for all tests
 - [x] Log all errors, warnings, info level logs to a table. 
 - [ ] Create a stored proc to pull the debug and trace logs.
 - [ ] Documentation
   - [ ] Add Doc strings to all modules and classes
   - [ ] Add Doc strings to all functions and methods
   - [ ] Add Sphin
 - [ ] Add more exception handling with a focus on clarity of the issue and solution.
 - [ ] Move purge table into iceberg and log as a job 
 - [ ] Fix the job, job steps and logs search

## Backlog
  - [ ] Add multiprocessing method for writes

## Important things to know about Iceberg
    - Iceberg is a specification, not an implementation
      - There are many implementations, but they all support the specification to a different degree, and in different ways.
    - The Iceberg format does not have a concept of unique key. This means that data duplication must be prevented by the engine during writes or handled by management process using things like Merge.

## Assumptions
  1. Code we are writing is most likely going to run in an IRIS intance



## Decisions
  1. Python as language
     1. Embedded Python is more fully integrated into IRIS than the JAVA runtime
     2. MGB has experience with Python
  2. Pyiceberg of PySpark
     1. Pyiceberg is a lighterweight library than PySpark
     2. Spark is a complicated distributed compute engine and requires knowledge to troubleshoot
     3. Spark hosts a JVM and the core code is mostly in Scala 
     4. Spark does have the most complete implementation of the Iceberg specification
  3. Configuration driven jobs
     1. All of the jobs run from a config file.
     2. 


