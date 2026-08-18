# User Guide

| Field | Value |
|---|---|
| **Document** | User Guide |
| **Location in Repo** | `docs/USER_GUIDE.md` |
| **Author** | Reza Hosseiny |
| **Status** | Approved |
| **Last Updated** | 2026-08-18 |
| **Covers** | How to install, operate, change, and troubleshoot the harness. Includes the procedure for new sample data and for changed decisions. |

> This document uses ASD-STE100 Simplified Technical English. Sentences are
> short. Each instruction is one sentence. The active voice is used.

---

## 1. Before you start

You need these items:

| Item | Detail |
|---|---|
| Python | Version 3.9 or later, with `PyYAML` and `requests` |
| A Splunk instance | Splunk Enterprise 9.x or 10.x. The reference instance is 10.4.1 at `/opt/splunk`. |
| Splunk credentials | An account with administrator capability |
| A production sample export | A CSV file with the columns `index`, `sourcetype`, `source`, `_time`, and `_raw` |

Install the requirements:

```bash
pip install -r requirements.txt
```

Create the credentials file. This file is in `.gitignore`. Do not commit it.

```bash
cp config/.env.example config/.env
$EDITOR config/.env          # set SPLUNK_USERNAME and SPLUNK_PASSWORD
chmod 600 config/.env
```

Confirm that the credentials work:

```bash
make connect
```

The command prints the Splunk version, the server name, and the number of apps
and indexes. If it fails, go to section 7.

## 2. Commands

Run `make help` to see this list at any time.

### 2.1 Offline commands

These commands need no Splunk instance and no credentials.

| Command | Effect |
|---|---|
| `make validate` | Checks the catalog for internal consistency |
| `make profile` | Profiles each sample export and refreshes the remediation map |
| `make fixtures` | Generates the synthetic coverage-fixture events |
| `make build` | Renders `build/apps/` from the catalog |
| `make redaction` | Confirms that no production identifier is in a generated file |
| `make offline` | Runs all five commands above, in order |

### 2.2 Instance commands

These commands need `config/.env`.

| Command | Effect |
|---|---|
| `make connect` | Confirms the credentials and reports the Splunk version |
| `make deploy` | Pushes the generated apps and restarts Splunk |
| `make seed` | Loads the sample data into the governed indexes |
| `make reseed` | Clean reload: purges, deploys, then seeds |
| `make teardown` | Removes the generated apps, the catalog indexes, and the test users |
| `make all` | Runs `offline`, then `deploy`, then `seed` |
| `make rebuild` | Runs `teardown`, then `all` |
| `make clean` | Removes generated output. Does not change the catalog or Splunk. |

`make deploy` restarts Splunk. The restart takes approximately 45 seconds.
Splunk cannot add an index without a restart.

## 3. First installation

Do the steps in this order:

```bash
make offline      # validate, generate fixtures, profile, build, check redaction
make connect      # confirm the credentials
make deploy       # create the indexes; Splunk restarts
make seed         # load the sample data
```

Then confirm the result. Open `reports/seed_verification.md`. Every row must
show a delta of `+0`.

The reference result is 35 indexes and 31,608 events.

## 4. Daily use

### 4.1 You have a new sample export

1. Copy the CSV file into `sample_data/`.
2. Run `make profile`.
3. Read the output.

The output shows one of two results for each value in the export:

- **No mapping gaps.** Every value has a rule. Go to step 4.
- **Mapping gaps.** The export holds a feed that no rule classifies. The output
  names each one. Go to section 4.3 first.

4. Run `make reseed`.

`make reseed` purges the old data, deploys again, and then seeds. Use this
command, and not `make seed`. Section 4.5 gives the reason.

A new sourcetype inside a known feed needs no work. A rule such as `aruba:*`
classifies it automatically. Only a new feed needs a decision.

### 4.2 You want to change a decision

An example is to move Aruba wireless logs out of the shared network index and
into an index of their own.

1. Edit `catalog/mapping.yaml`. Change the `index` value of the rules.
2. Run `make validate`.

The check fails, because the new index is not in the register:

```
1 ERRORS:
  index ops_non_inf_wls_m: routed to by mapping but not registered in indexes.yaml
```

3. Add the new index to `catalog/indexes.yaml`. Give it a description, the
   decoded name fields, and both owners.
4. Add the content code to `catalog/taxonomy.yaml` if the code is new.
5. Run `make validate` again. It must report `validation: clean`.
6. Run `make reseed`.

The check enforces the naming rules. A code must have three letters. `wifi` is
rejected. `wls` is accepted.

### 4.3 You must classify a new feed

For each new feed, decide these six items:

| Item | Where it goes | Example |
|---|---|---|
| Data class | The first part of the index name | `ops` |
| Compliance driver | The second part | `non` |
| Domain | The third part | `inf` |
| Content code, three letters | The fourth part | `ndl` |
| Retention tier | The suffix | `_m` |
| Business owner and technical owner | `catalog/indexes.yaml` | `it_networking` |

Then:

1. Add a `legacy_indexes` entry in `catalog/mapping.yaml`. Give it one rule for
   each sourcetype pattern.
2. Add the index to `catalog/indexes.yaml`, unless it already exists.
3. Register any new code in `catalog/taxonomy.yaml`.
4. Run `make validate`, then `make reseed`.

A rule can use a glob for the sourcetype. It can also use a template for the
governed value. The templates are listed at the top of `catalog/mapping.yaml`.

### 4.4 You must change an owner

Edit `catalog/indexes.yaml`. Use a unit code from `catalog/business_units.yaml`.
Then run `make validate`. No reload is needed, because ownership is a record and
not a Splunk setting.

### 4.5 Why `make reseed` and not `make seed`

Seeding is not incremental. It sends every event that it resolves. To send again
on top of existing data adds a second copy of every event. Every count then
doubles, and every test that depends on a count becomes wrong.

`make seed` therefore refuses to run when the inputs changed. It reports the
change and names `make reseed` instead.

`make reseed` purges first. It removes the catalog indexes and their data. It
also purges the data from an index that Splunk provides, because such an index
cannot be removed.

## 5. What the reports tell you

| Report | Content |
|---|---|
| `reports/mapping_worksheet.md` | What one export contains, and which standard each value does not obey |
| `docs/source_remediation_map.md` | Each legacy value and the governed value that replaces it |
| `reports/seed_verification.md` | Expected and actual event counts for each index |
| `reports/resolved_inventory.json` | Governed sourcetypes and sources for each index |

`reports/` holds generated output. It is in `.gitignore`.
`docs/source_remediation_map.md` is a deliverable. It is committed.

## 6. Data protection

### 6.1 What is not committed

| Path | Reason |
|---|---|
| `sample_data/*.csv` | Production exports hold real host names and identifiers |
| `raw_files/catalog/` | Holds the Azure tenant identifier and an internal host name |
| `config/.env` | Holds credentials |
| `config/forbidden_literals.txt` | Holds identifiers that must not be committed |
| `build/`, `reports/` | Generated output |

### 6.2 How to confirm that redaction works

```bash
make redaction
```

The command checks every generated document, and every event in each export. A
clean result reports:

```
clean — no production identifier found in any checked file.
```

To confirm the result on the instance, search for a known real value. The count
must be zero:

```
index=* "yourdomain.example" | stats count
```

Also search for `example.invalid`. The count must be more than zero. This
distinguishes a successful redaction from an empty index.

### 6.3 How to add a new identifier to protect

Put a non-sensitive marker, such as a DNS domain, in the
`forbidden_literals` list in `catalog/redaction.yaml`.

Put a specific identifier, such as a tenant identifier, in
`config/forbidden_literals.txt`. That file is in `.gitignore`, so the value is
not committed. `config/forbidden_literals.example.txt` shows the format.

**A hit from the literal search is a fault in the redaction rules.** Correct the
rules. Do not add the value to the list to make the report clean.

## 7. Troubleshooting

### 7.1 `make connect` fails with 401

The credentials are wrong. Check `SPLUNK_USERNAME` and `SPLUNK_PASSWORD` in
`config/.env`. Confirm that the account has administrator capability.

### 7.2 `make connect` fails with connection refused

Splunk is not listening. Two causes are usual:

- Splunk is stopped. Run `systemctl status splunk`.
- Splunk is in the middle of a restart. Wait, then try again. A restart takes
  approximately 45 seconds.

### 7.3 The indexes exist but hold no events

Splunk logs `INDEXER_MISSING_INDEX` for each event that it drops. The index
exists in the configuration, but the indexer does not have it.

Run `make deploy` again. That command restarts Splunk. Splunk cannot add an
index without a restart.

### 7.4 An event count does not match

Open `reports/seed_verification.md` and find the row. A negative delta and a
positive delta have different causes.

**More events than expected.** The events are broken into more than one event
each. A multi-line event with `SHOULD_LINEMERGE = false` gives one event for
each line. The seeder flattens each event to prevent this. If the fault returns,
check for an event that holds a carriage return.

**Fewer events than expected.** The events are joined together. Splunk cannot
find a timestamp on a line, so it adds the line to the event before it. The
seeder adds the timestamp from the export to prevent this. To confirm, look at
the start of the raw event. It must begin with a date or an epoch value.

Run this search to see the counts that Splunk holds:

```
| tstats count where index=* by index
```

Use `tstats`. Do not use `totalEventCount` from the REST endpoint. That value
is behind the ingestion and is not reliable for a comparison.

### 7.5 `make deploy` reports that the app directory is not writable

The app directory belongs to the `splunk` user. You have two options:

- Use the management API. Set `deployment.method: rest` in
  `config/settings.yaml`. This is the default.
- Grant access to the directory. Add your account to the `splunk` group, or set
  an access control list on the directory.

### 7.6 An index will not delete during teardown

Two causes are usual, and both are correct behaviour:

- **The index belongs to Splunk.** `summary` is an example. Teardown purges the
  data instead. The index itself stays.
- **The caller is in the wrong application.** Splunk reports
  `sourceApp doesn't equal callerApp`. Teardown deletes an index in the
  namespace of the application that owns it.

## 8. Rules to follow

1. Never edit a file in `build/`. Change the catalog and generate again.
2. Never use the Splunk web interface to change RBAC. The strategy prohibits it.
   Such a change goes to `etc/system/local`, which is outside version control.
3. Never commit a production export, a credential, or the forbidden-literal
   file.
4. Never write `catalog/expectations.yaml` with a tool. A person writes that
   file. Section 4.2 of `docs/DESIGN.md` gives the reason.
5. Always run `make validate` after a catalog change.
6. Always use `make reseed` after the inputs change, and not `make seed`.

## 9. Related documents

| Document | Purpose |
|---|---|
| `docs/DESIGN.md` | The architecture and the reason for each design rule |
| `ai-egc/ROADMAP.md` | The five phases and the current position |
| `ai-egc/START_HERE.md` | The governance framework and the reading order |
| `strategy/Splunk_Strategy_2.0.md` | The normative specification |
