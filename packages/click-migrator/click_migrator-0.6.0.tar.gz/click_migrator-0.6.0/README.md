# click_migrator

#### Solution for executing ClickHouse database migration scripts.

Supported:
- sql migration with single statement
- sql migrations with multiple statements separated by semicolons
- clickhouse database only

## 1. Installation

`pip install click_migrator`

## 2. Usage

```
from click_migrator.migrator import Migrator

migrator = Migrator(migrations_dir, db_host, db_name, db_user, db_password, db_port, create_db_if_not_exists)
migrator.migrate()
```

Parameter                        | Description                                                  | Type | Default value
---------------------------------|--------------------------------------------------------------|-----|--------------
migrations_dir                   | Path to the directory with migrations                        | Path| -            
db_host                          | Database hostname                                            | str | "localhost" 
db_name                          | Database name                                                | str | "default" 
db_user                          | Database user                                                | str | "default" 
db_password                      | Database user password                                       | str | ""        
db_port                          | Database port                                                | int | 8999      
create_db_if_not_exists          | Flag to create a database `db_name`, if it does not exist    | bool| True   

### 2.1 Migration file name requirements

The name of the migration files must follow the following pattern:

```
001.any_characters.sql
002.any_characters.sql
003.any_characters.sql
...
```
### 2.2 Content of sql migrations

Sql-migrations can contain one or more statements. 
Instructions in multiple statements migrations must be separated by a semicolon.

```
WARNING: It is not recommended to use a semicolon, for example,
in the comments to the table, this can lead to errors.
```

#### 2.2.1 One statement example:
```
create table if not exists example
(
    `id` Int16
)
engine = ReplacingMergeTree()
partition by id
ORDER BY (id)
settings index_granularity = 8192;
```

#### 2.2.2 Multiple statement example:
```
create table if not exists example
(
    `id` Int16
)
engine = ReplacingMergeTree()
partition by id
ORDER BY (id)
settings index_granularity = 8192;

insert into example
values
	(1),
	(2),
	(3);
```

## 3. Migration history table

To account for applied migrations, the migrator creates a `migration_history` table.

Field         | Type      | Description                                    |
--------------|-----------|------------------------------------------------|
version       | UInt16    | Sequence number of migration                   
file_name     | String    | Name of the migration file                     
checksum      | String    | md5 checksum                                   
installed_on  | DateTime  | Migration execution date                       
success       | Bool/Int8 | Confirmation that the migration was successful 

If the migration fails, the `success` field is set to `False`. 
In this case, you need to fix the broken migration,
remove the record about the unsuccessful migration from the `migration_history` table,
and then repeat the migrations.
