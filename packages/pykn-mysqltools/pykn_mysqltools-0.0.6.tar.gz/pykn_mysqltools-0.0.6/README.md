# pykn_mysqltools
Handy utility tools for interacting with a MySQL database with Python. This
project was created with a need to interact with MySQL utilizing lots of CSVs,
but the complexity of `pandas` was a bit overkill. Perhaps as my needs grow,
I'll see the light and move over to `pandas`.

## Typical Usage

You'll primarily want to interact with the DBConnection class. Example:

```
from pykn_mysqltools import utilities as pyknmt

my_conn = pyknmt.DBConnection(
    db_hostname="hostname",
    db_username="username",
    db_password="password",
    db_schema="schema",
    db_port="port"
)
```
From here you can interact with your database through `my_conn`, and access 
helpful tools like the `import_csv` method:

```
my_conn.import_csv("./path/to/your.csv", "tablename")
```

If your use case calls for inserting data directly, the `insert` method is your
friend.