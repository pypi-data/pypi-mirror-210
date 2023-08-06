# bovine_tool

bovine_tool provides a CLI interface to manage bovine.

## Configuration

The default database connection is "sqlite://bovine.sqlite3". This can be overwridden with the environment variable "BOVINE_DB_URL".

## Quick start

To register a new user with a FediVerse handle use

```bash
python -m bovine_tool.register fediverse_handle [--domain DOMAIN]
```

the domain must be specified.

## Managing users

```bash
python -m bovine_tool.manage bovine_name
```

displays the user.

To add a did key for [the Moo Client Registration Flow](https://blog.mymath.rocks/2023-03-25/BIN2_Moo_Client_Registration_Flow) with a BovineClient use

```bash
python -m bovine_tool.manage bovine_name --did_key key_name did_key
```

Furthermore, using `--properties` the properties can be over written.

## Todo

- [ ] Add ability to delete stale data, e.g. remote data older than X days
- [ ] Add ability to import/export all data associated with an actor
