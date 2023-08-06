# Fluctuate

[![coverage report](https://gitlab.com/munipal-oss/fluctuate/badges/master/coverage.svg)](https://gitlab.com/munipal-oss/fluctuate/-/commits/master)
[![Latest Release](https://gitlab.com/munipal-oss/fluctuate/-/badges/release.svg)](https://gitlab.com/munipal-oss/fluctuate/-/releases)

Fluctuate is a simple migration utility for [Fauna DB] written in [Python]. It doesn't
aim to be as full featured as something like [fauna-schema-migrate], but aims to provide
a foundation to set up your Fauna dabatases as code.

# Table of contents

[[_TOC_]]

# Installation

Install with the usual [Python] package manager. Here's an example with [pip]:

```bash
pip install fluctuate
```

Ensure it installed correctly by running:

```bash
fluctuate --version
```

If you would like to use the [AWS SecretsManager] integration for retrieval of the fauna
secret key, you will need to install the `aws_secrets_manager` extra. Here's an example
with [pip]:

```bash
pip install fluctuate[aws_secrets_manager]
```

# Creating migrations

Fluctuate will automatically search for migrations when invoked. It looks for a Python
module named "fluctuate_migrations" that has a module level attribute called
"migrations" somewhere on or under the current working directory.

To define your projects migrations, create a file named `fluctuate_migrations.py` in a
subfolder of your project along with an `__init__.py` within that subfolder. Within
`fluctuate_migrations.py` you need to create a tuple or list of `Migration`s named
"migrations" that defines your migrations. An example from our test suite is below:

```python
# fluctuate_migrations.py
from fauna import fql
from faunadb import query

from fluctuate.migrations import Migration

migrations = (
    Migration(
        name="test_migration_1",
        namespace="cli_test",
        migration=query.create_collection(
            {"name": "test_collection_1", "history_days": 0}
        ),
        reverse_migration=query.delete(query.collection("test_collection_1")),
    ),
    Migration(
        name="test_migration_2",
        namespace="cli_test",
        migration=query.create_collection(
            {"name": "test_collection_2", "history_days": 0}
        ),
        reverse_migration=query.delete(query.collection("test_collection_2")),
    ),
    Migration(
        name="test_migration_3",
        namespace="cli_test",
        migration=query.create_database({"name": "test_database_1"}),
        reverse_migration=query.delete(query.database("test_database_1")),
    ),
    Migration(
        name="test_migration_4",
        namespace="cli_test",
        migration=fql(
            """
            Collection.create({name: "test_collection_3", history_days: 0})
            """
        ),
        reverse_migration=fql('Collection.byName("test_collection_3").delete()'),
        child_database="test_database_1",
    ),
    Migration(
        name="test_migration_5",
        namespace="cli_test",
        migration=fql('Database.create({name: "test_database_2"})'),
        reverse_migration=fql('Database.byName("test_database_2").delete()'),
        child_database="test_database_1",
    ),
    Migration(
        name="test_migration_6",
        namespace="cli_test",
        migration=query.create_collection(
            {"name": "test_collection_4", "history_days": 0}
        ),
        reverse_migration=query.delete(query.collection("test_collection_4")),
        child_database="test_database_1/test_database_2",
    ),
    Migration(
        name="test_migration_7",
        namespace="cli_test",
        migration=query.create_index(
            {
                "name": "test_collection_4_index",
                "source": query.select(
                    "ref", query.get(query.collection("test_collection_4"))
                ),
                "terms": [{"field": ["data", "name"]}],
                "unique": True,
            }
        ),
        reverse_migration=query.delete(query.index("test_collection_4_index")),
        child_database="test_database_1/test_database_2",
    ),
    Migration(
        name="test_migration_8",
        namespace="cli_test",
        migration=fql(
            """
            Collection.create(
                {
                    name: "test_collection_5",
                    history_days: 0,
                    indexes: {by_name: {terms: [{field: "name"}]}},
                    constraints: [{unique: ["name"]}]
                }
            )
            """
        ),
        reverse_migration=fql('Collection.byName("test_collection_5").delete()'),
        child_database="test_database_1/test_database_2",
    ),
)

```

Let's walk through this example. First a bit about migrations. Each `Migration` has 5
fields, the first 4 of which are required:

1. name: This is the migration name, and needs to be unique within the migration's
   namespace
2. namespace: This is the namespace under which the migration resides. You should
   uniquely namespace your application's migrations so as not to clash with any other
   application's migrations that may also be applied to your database.
3. migration: This is the FQLv4 or FQLv10 query used to create your schema documents, be
   it collections, indexes, UDFs, or otherwise.
4. reverse_migration: This is the FQLv4 or FQLv10 query that will be used to undo
   whatever the FQL in the migration did, so it should be the opposite operation.
5. (OPTIONAL) child_database: This defines the child database to which this migration
   should be applied. Fluctuate will attempt to log into this database and apply the
   migrations there. Nested child databases should be specified in the same format used
   for [scoped keys]. If no child database is defined, the migrations apply to the
   database the current key in use provides access to.

In the example above, there are a total of 8 migrations to be preformed. The first 3
migrations apply to the top level database, which is the database the key used to run
the migration has access to. Then the next 2 migrations are applied to "test_database_1"
which is created by migration number 3. Finally, the last 3 migrations are applied to
"test_database_2" which is nested under "test_database_1" and was created in the 5th
migration.

In this example we applied each schema document in a separate migration, but as the
`migration` field can be any arbitrary FQL, all schema documents could be created in one
migration. This tool does not impose an opinion on how to lay out your migrations. Both
FQLv4 and FQLv10 migrations are supported and can be used interchangeably.

Each migration is applied in a single transaction to write both the migration and the
record that keeps track of the applied migrations. If the migration is written in FQLv4,
a FQLv4 client will be used to apply it. If the migration is written in FQLv10, a FQLv10
client will be used to apply it. You need to be aware of the
[caveats of schema documents] when referring to them within the same migration. There is
also the constraint of not being able to use any schema documents created within the
same transaction. This constraint is present in both FQLv4 and FQLv10.

# Applying migrations

The `fluctuate migrate` command is used to apply all unapplied migrations. As migrations
are applied to your databases, their application is recorded in a separate collection.
This is referred to when applying migrations to ensure the same migration is not applied
twice. Migrations are applied in the order they are defined in the migrations tuple or
list.

Each migration, and the recording of the application of that migration, are applied in a
single transaction. If a migration fails, the transaction rolls back and no changes from
that migration will be applied. Any migrations that were already successfully applied
will remain applied. A unique constraint ensures that the same migration in the same
namespace can only be applied once.

This tool will attempt to create a collection named "fluctuate_migrations" and an index
named "fluctuate_migrations_unique_name_and_namespace" on all databases this is used on.
If a collection and/or index with these names already exist, running this tool will
fail.

# Unapplying migrations

The `fluctuate unmigrate` command is used to unapply migrations. This is a destructive
operation so it should be run with care. A target migration to unapply up to can be
provided, otherwise all applied migrations will be unapplied. Migrations are unapplied
in the reverse order from how they are defined in the migrations tuple or list.

Using the example above, if the following is run:

```bash
fluctuate unmigrate --key some_key --target test_cli.test_migration_5
```

Then the reverse_migrations for test_cli.test_migration_8, test_cli.test_migration_7,
and test_cli.test_migration_6 are run, removing test_collection_5, the
test_collection_4_index, and test_collection_4 from test_database_2. Then the reverse
migration for test_cli.test_migration_5 is run deleting test_database_2 from
test_database_1.

Unapplying a migration, and the recording of unapplying that migration, is done in a
single transaction. If a reverse migration fails, the transaction rolls back and no
changes from that migration will be reversed. Any migrations that were already
successfully unapplied will remain unapplied.

# Specifying Fauna DB credentials

Both commands above require access to a FaunaDB database in order to operate. A key can
be specified directly when invoking the command using `--key` or the key can be fetched
from [AWS SecretsManager] by specifying `--secret-arn` with the [ARN] of the secret to
read. Usage of `--secret-arn` requires installation of the `aws_secrets_manager` extra
and configuration of AWS credentials. See the command help message for more details.

Both of these arguments can be specified with the environment variables FLUCTUATE_KEY
and FLUCTUATE_SECRET_ARN, respectively.

Fluctuate supports the usage of [scoped keys] as credentials, but the scoped key must
have sufficient access to perform the migration operations or migrating will fail.

When applying migrations to a child database, Fluctuate creates a scoped key from the
key provided to the command. By default this scoped key uses the [admin role]. However,
if the key provided to the command is itself a scoped key, the role of that scoped key
will be used instead.

[Fauna DB]: https://docs.fauna.com/fauna/current/
[Python]: https://www.python.org/
[fauna-schema-migrate]: https://github.com/fauna-labs/fauna-schema-migrate
[pip]: https://pip.pypa.io/en/stable/
[scoped keys]: https://docs.fauna.com/fauna/current/security/keys?lang=python#scoped-keys
[Do]: https://docs.fauna.com/fauna/current/api/fql/functions/do?lang=python
[caveats of schema documents]: https://forums.fauna.com/t/do-and-creation-of-schema-documents/3418/
[AWS SecretsManager]: https://docs.aws.amazon.com/secretsmanager/
[ARN]: https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
[admin role]: https://docs.fauna.com/fauna/current/security/keys?lang=python#admin-role
