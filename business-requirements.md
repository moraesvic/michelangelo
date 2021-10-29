# Business requirements / Design document

This is a document describing what I intend to achieve with this project — what will be considered a successful implementation and what benchmarks I have in mind.

### The API is going to consist of two main endpoints: PRODUCTS and PICTURES

1. PRODUCTS datamodel contains information such as product name, description, price, quantity in stock, as well as metadata such as when the product was included in the database

2. PICTURES datamodel point to **thumbnails** of pictures illustrating the products. Each register must contain picture original filename, MD5 hash, path at which it is stored in the filesystem and metadata.

3. Picture binary data is going to be stored in the filesystem, and not as a blob in the database. On the internet, one can find opinions for and against each scenario: [link 1](https://wiki.postgresql.org/wiki/BinaryFilesInDB) \[[archived](https://archive.md/WewFO)\], [link 2](https://stackoverflow.com/questions/3748/storing-images-in-db-yea-or-nay) \[[archived](https://archive.md/oVqVi)\]. In the end, I weighed the pros and cons and decided to store pictures in the filesystem, in order not to incur in much overhead for a very frequent request.

4. Every product can have an associated picture. Many products can have the same associated picture. The implementation should check whether the picture was already uploaded to the server with an MD5 hash check.

5. There should be no picture without an associated product.

6. These constraints are to be enforced by a Relational Database Management System (RDBMS).

### The back-end must be written in Python 3.8, with the web-framework Flask 2.0. Delivery of static content will be managed by Nginx.

### Each API endpoint must be structured according to the REST architecture, and *at least* support HTTP methods GET, POST, PATCH and DELETE, associated to RDBMS operations READ, INSERT, UPDATE and DELETE.

### Each uploaded file must be validated.

1. Files larger than 5 MB must not be accepted.

2. Files containing non-image data (i.e., text, executable format, audio, etc.) must not be accepted.

3. User input, including file extension, is not to be trusted.

### Once validated, pictures must be stored in the filesystem in an efficient way, regarding disk usage. For that goal, picture resizing, re-encoding and compression can be used.

1. Image resolution has to have minimal dimension of 200 pixels (either width or height)

2. The client will make requests to 8-10 pictures at a time, and this can be a bottleneck for user experience, especially when download occurs over a mobile network.

3. Client tests must be run using throttling. Values for the slowest throttling mode, **corresponding roughly to a slow 3G connection**: download rate 450 kbit/s, upload rate 150 kbit/s, latency 250ms.

4. In the slowest throttling mode, DOMContentLoaded should happen in **less than 5 seconds**. Transfer of all resources for the page must happen in **less than 10 seconds**.

5. To achieve that, a good benchmark is: the average picture size should not be larger than 70 KB (before gzip compression).

### The API endpoints can be benchmarked with "ab" (Apache Benchmark)

1. It does not make a lot of sense, because the performance depends on what machine is running the server, database size, among others. But it is at least an indicator we can use to compare different approaches and frameworks

2. It is reasonable to expect that the API can complete at least 50 JSON GET requests per second, when 50 users try to connect simultaneously, [using KeepAlive header and accepting compression](https://stackoverflow.com/questions/12732182/ab-load-testing) ("ab -k -H "Accept-Encoding: gzip, deflate" -n 500 -c 50 path/to/api")

### There will be no authentication. In a real case scenario, this would be a must, but it is not expected to be implemented within the limited given timeframe.

- The client side will be implemented with React

1. At least 3 pages are required: products overview, products insert, and product specific page.

### There will be an endpoint for populating data using a CSV file through a Command Line Interface (CLI). This is intended for admin use and will not be available to regular users.