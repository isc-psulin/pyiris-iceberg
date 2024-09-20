## Data Warehouse
A data warehouse or OLAP database is a centralized repository that supports storing large volumes of data ingested from various sources such as operational systems, application databases, and logs. Figure 1-2 presents an architectural overview of the technical components of a data warehouse.

A data warehouse owns all the technical components in a single system. In other words, all the data is stored in its proprietary file and table formats on its proprietary storage system. This data is then managed exclusively by the data warehouse’s storage engine, is registered in its catalog, and can be accessed only by the user or analytical engines through its compute engine.

Up until about 2015, most data warehouses had the storage and compute components tightly coupled on the same nodes, since most were designed and run on premises. However, this resulted in a lot of problems. Scaling became a big issue because datasets grew in volume at an accelerating pace while the number and intensity of workloads (i.e., compute tasks running on the warehouse) also increased. Specifically, there was no way to independently increase the compute and storage resources depending on your tasks. If your storage needs grew more quickly than your compute needs, it didn’t matter. You still had to pay for additional compute even though you didn’t need it.

This led to the next generation of data warehouses being built with a big focus on the cloud. These data warehouses began gaining traction around 2015 as cloud-native computing burst onto the scene, allowing you to separate the compute and storage components and scale these resources to suit your tasks. They even allowed you to shut down compute when you weren’t using it and not lose your storage.

### Pros
 - Serves as the single source of truth as it allows storing and querying data from various sources
 - Supports querying vast amounts of historical data, enabling analytical workloads to run quickly
 - Provides effective data governance policies to ensure that data is available, usable, and aligned with security policies
 - Organizes the data layout for you, ensuring that it’s optimized for querying
 - Ensures that data written to a table conforms to the technical schema

### Cons
 - Locks the data into a vendor-specific system that only the warehouse’s compute engine can use
 - Expensive in terms of both storage and computation; as the workload increases, the cost becomes hard to manage
 - Mainly supports structured data
 - Does not enable organizations to natively run advanced analytical workloads such as ML

## The Data Lake
While data warehouses provided a mechanism for running analytics on structured data, they still had several issues:
 -  A data warehouse could only store structured data.
 -  Storage in a data warehouse is generally more expensive than on-prem Hadoop clusters or cloud object storage.
 -  Storage and compute in traditional on-prem data warehouses are often commin‐ gled and therefore cannot be scaled separately. More storage costs came with more compute costs whether you needed the compute power or not.

Addressing these issues required an alternative storage solution that was cheaper and could store all your data without the need to conform to a fixed schema. This alternative solution was the data lake.

### A Brief History
Originally, you’d use Hadoop, an open source, distributed computing framework, and its HDFS filesystem component to store and process large amounts of structured and unstructured datasets across clusters of inexpensive computers. But it wasn’t enough to just be able to store all this data. You’d want to run analytics on it too.

The Hadoop ecosystem included MapReduce, an analytics framework from which you’d write analytics jobs in Java and run them on the Hadoop cluster. Writing MapReduce jobs was verbose and complex, and many analysts are more comforta‐ ble writing SQL than Java, so Hive was created to convert SQL statements into MapReduce jobs.

To write SQL, a mechanism to distinguish which files in your storage are part of a particular dataset or table was needed. This resulted in the birth of the Hive table format, which recognized a directory and the files inside it as a table.

Over time, people moved away from using Hadoop clusters to using cloud object storage (e.g., Amazon S3, Minio, Azure Blob Storage), as it was easier to manage and cheaper to use. MapReduce also fell out of use in favor of other distributed query engines such as Apache Spark, Presto, and Dremio. What did stick around was the Hive table format, which became the standard in the space for recognizing files in your storage as singular tables on which you can run analytics. However, cloud storage required more network costs in accessing those files, which the Hive format architecture didn’t anticipate and which led to excessive network calls due to Hive’s dependence on the table’s folder structure.

A feature that distinguishes a data lake from a data warehouse is the ability to leverage different compute engines for different workloads. This is important because there has never been a silver-bullet compute engine that is best for every workload and that can scale compute independently of storage. This is just inherent to the nature of computing, since there are always trade-offs, and what you decide to trade off determines what a given system is good for and what it is not as well suited for.

Note that in data lakes, there isn’t really any service that fulfills the needs of the storage engine function. Generally, the compute engine decides how to write the data, and then the data is usually never revisited and optimized, unless entire tables or partitions are rewritten, which is usually done on an ad hoc basis. Figure 1-3 depicts how the components of a data lake interact with one another.

### Pros
 
 - Lower cost
    - The costs of storing data and executing queries on a data lake are much lower than in a data warehouse. This makes a data lake particularly useful for enabling analytics on data whose priority isn’t high enough to justify the cost of a data warehouse, enabling a wider analytical reach.
 - Stores data in open formats
    - In a data lake, you can store the data in any file format you like, whereas in a data warehouse, you have no say in how the data is stored, which would typically be a proprietary format built for that particular data warehouse. This allows you to have more control over the data and consume the data in a greater variety of tools that can support these open formats.
 - Handles unstructured data
    - Data warehouses can’t handle unstructured data such as sensor data, email attachments, and logfiles, so if you wanted to run analytics on unstructured data, the data lake was the only option.

### Cons
 - Performance
    - Since each component of a data lake is decoupled, many of the optimizations that can exist in tightly coupled systems are absent, such as indexes and ACID (Atomicity, Consistency, Isolation, Durability) guarantees. While they can be re-created, it requires a lot of effort and engineering to cobble the components (storage, file format, table format, engines) in a way that results in performance comparable to that of a data warehouse. This made data lakes undesirable for high-priority data analytics where performance and time mattered.
 - Requires lots of configuration
    - As previously mentioned, creating a tighter coupling of your chosen components with the level of optimizations you’d expect from a data warehouse would require significant engineering. This would result in a need for lots of data engineers to configure all these tools, which can also be costly.
 - Lack of ACID transactions
    - One notable drawback of data lakes is the absence of built-in ACID transaction guarantees that are common in traditional relational databases. In data lakes, data is often ingested in a schema-on-read fashion, meaning that schema validation and consistency checks occur during data processing rather than at the time of

## The Data Lakehouse
While using a data warehouse gave us performance and ease of use, analytics on data lakes gave us lower costs, flexibility by using open formats, the ability to use unstructured data, and more. The desire to thread the needle leads to great strides and innovation, which leads to what we now know as the data lakehouse.

The data lakehouse architecture decouples the storage and compute from data lakes and brings in mechanisms that allow for more data warehouse–like functionality (ACID transactions, better performance, consistency, etc.). Enabling this functional‐ ity are data lake table formats that eliminate all the previous issues with the Hive table format. You store the data in the same places you would store it with a data lake, you use the query engines you would use with a data lake, and your data is stored in the same formats it would be stored in on a data lake. What truly transforms your world from “read-only” data to a “center of my data world” data lakehouse is the table format providing a metadata/abstraction layer between the engine and storage for them to interact more intelligently (see Figure 1-4).

## Hive

### Pros
 -  It enabled more efficient query patterns than full table scans, so techniques such as partitioning (dividing the data based on a partitioning key) and bucketing (an approach to partitioning or clustering/sorting that uses a hash function to evenly distribute values) made it possible to avoid scanning every file for faster queries.
 -  It was file format agnostic, so it allowed the data community over time to develop better file formats, such as Apache Parquet, and use them in their Hive tables. It also did not require transformation prior to making the data available in a Hive table (e.g., Avro, CSV/TSV).
 -  Through atomic swaps of the listed directory in the Hive Metastore, you can make all-or-nothing (atomic) changes to an individual partition in the table.

Over time, this became the de facto standard, working with most data tools and providing a uniform answer to “what data is in this table?”

### Cons 
  1.  File-level changes are inefficient, since there was no mechanism to atomically swap a file in the same way the Hive Metastore could be used to swap a partition directory. You are essentially left making swaps at the partition level to update a single file atomically.
  2. While you could atomically swap a partition, there wasn’t a mechanism for atomically updating multiple partitions as one transaction. This opens up the possibility for end users seeing inconsistent data between transactions updating multiple partitions.
  3. There really aren’t good mechanisms to enable concurrent simultaneous updates, especially with tools beyond Hive itself.
  4. An engine listing files and directories was time-consuming and slowed down queries. Having to read and list files and directories that may not need scanning in the resulting query comes at a cost.
  5. Partition columns were often derived from other columns, such as deriving a month column from a timestamp. Partitioning helped only if you filtered by the partition column, and someone who has a filter on the timestamp column may not intuitively know to also filter on the derived month column, leading to a full table scan since partitioning was not taken advantage of.
  6. Table statistics would be gathered through asynchronous jobs, often resulting in state table statistics, if any statistics were available at all. This made it difficult for query engines to further optimize queries.
  7. Since object storage often throttles requests against the same prefix (think of an object storage prefix as analogous to a file directory), queries on tables with large numbers of files in a single partition (so that all the files would be in one prefix) can have performance issues.
 
### Probably the most importatn thing
**Creators of modern table formats realized the flaw that led to challenges with the Hive table format was that the definition of the table was based on the contents of directories, not on the individual datafiles.*** Modern table formats such as Apache Iceberg, Apache Hudi, and Delta Lake all took this approach of defining tables as a canonical list of files, providing metadata for engines informing which files make up the table, not which directories. This more granular approach to defining “what is a table” unlocked the door to features such as ACID transactions, time travel, and more.