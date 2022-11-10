## What is Mini Link?

The idea is a program that makes your URLs shorter. Basically, you enter a URL and receive a short version of it.

######_(You can check out the [other version of this project](https://github.com/maripillon/MiniLink/) which I did a year ago using Django and celery)_

In order to start the project, run the following command in the main directory:

`uvicorn main:app --reload`

and to read the APIs document go to: `host:port/minilink/docs/`

To run the tests use this command: `python -m pytest`


###Mini Link has the following APIs:

#### Generate short URL: 
Using md5 hash function, this API gives you a unique yet short URL based on the original one.

#### Get URL information:

Given the parameters `hashed_url`, `offset`, and `limit`, this API gives you information about your URL.

- If only `offset` and `limit` are set, the output will be a list of all generated URL in Mini Link.

- If only `hashed_url` is set then regardless of the other two parameters, the output will be information on the requested  `hashed_url`

#### Delete URL:

Given the hashed_url as the input parameter, this API inactivates the url and its short version.

#### Redirect URL:

As the main API of the Mini Link, it's responsible for redirecting the user from the `hashed_url` to the `original_url`

### Behind the Scenes
Having in mind that our project doesn't involve OOP and the performance is the main goal
I chose FastAPI over Django.


In my opinion, the first step of the system design is designing its database.
Based on Url and Visitor which are two entities of our system, I
considered an RDB (here I utilized from PostgreSQL) and designed an ERD for it:
<img height="550" src="..\miniLink_exbito\files\MiniLink_exbito_db.jpg" width="800"/>

Then I realized the most requested API among all APIs is `Redirecting` and 
knowing that redirecting is a simple key value like hashed_url -> original_url
I used Redis to store (cache) this key-value to speed up the redirecting process.

Along with redirecting the visitor, I also store Visitor data in postgres db.
Based on the [Benchmark](https://github.com/faranakopolis/MiniLink/blob/master/MINI%20LINK_report.pdf)
I did with Jmeter, I realized storing data in database takes too much time and makes the redirecting process getting slow.
So after Learning and testing a few libraries (like multithreading, celery, ...) I decided to use 
Fast API Background Task for writing the visitor data in database and redirect the visitor faster than before.

###Future Work:

    - Write more tests
    - Add Logging for Exceptions (or Sentry)
    - Handle Exceptions better
    - Set Rate Limit for APIs
    - Benchmark the APIs
    - Make url statics more readable and valuable
    - ...


