# Fitness Centre Database

An academic Oracle SQL and SQL*Plus project for fitness centre memberships,
class attendance, room utilisation and equipment usage. The database has 12
related tables; four interactive reports provide formatted details and calculated
summaries. The original `.txt` script filenames are retained.

## Run the scripts

Requirements: Oracle Database, SQL*Plus, and a dedicated empty practice schema
with permission and quota to create tables. Python is optional, for tests only.

1. Open SQL*Plus from this repository folder and connect to your practice schema.
   Do not put credentials in repository files or commands shared with others.
2. Create the tables and load the fictional sample data:

   ```sql
   @CreateTable.txt
   @InsertData.txt
   ```

3. Check the output for errors before issuing `COMMIT;`. If sample loading fails,
   use `ROLLBACK;` before retrying. Oracle table creation is DDL and is not undone
   by that rollback. These scripts are not repeatable migrations: do not rerun
   them over an existing populated schema or use them against production data.
4. Run any report and answer its prompts:

   ```sql
   @TanYiHeng_MembershipStatusReport.txt
   @CheahYongShun_MemberClassAttendanceReport.txt
   @LamYiHen_RoomUtilisationReport.txt
   @LimJunYi_EquipmentUsageReport.txt
   ```

Membership status expects `Active` or `Inactive`; attendance and equipment
reports expect dates in `YYYY-MM-DD` format; room utilisation expects a numeric
month and year. Use periods represented in the sample data. Inputs use SQL*Plus
substitution variables, so run these classroom scripts only with trusted input.

## Coding contributions

| Contributor | Code responsibility |
| --- | --- |
| [Tan Yi Heng](https://github.com/tan0480) | `CreateTable.txt`, `InsertData.txt`, membership status report and its summary |
| [Cheah Yong Shun](https://github.com/ys012007) | Member class attendance report and its summary |
| [Lam Yi Hen](https://github.com/lamyihen77-beep) | Room utilisation report and its summary |
| [Lim Jun Yi](https://github.com/ljunyi0212) | Equipment usage report and its summary |

The import commits attribute the confirmed work to its authors. Tan Yi Heng
performed the repository import and push; import timestamps are not the original
assignment development dates. The supporting summary tests and documentation
were prepared with AI assistance and imported by Tan Yi Heng, separate from the
teammates' original report modules.

## Summary checks and limitations

Run the existing standard-library tests from this folder:

```text
python -B -m unittest discover -s tests -v
```

The eight tests use synthetic data in an in-memory SQLite database and adapt
Oracle functions to check summary calculations, filters, ties, empty results and
duplicate payments. They do not connect to Oracle or modify the sample data.
They do not validate the complete schema/data import, Oracle compatibility or
SQL*Plus display formatting. No Oracle/SQL*Plus execution was performed for this
repository import.

See [SUMMARY_NOTES.md](SUMMARY_NOTES.md) for the calculation definitions.
In particular, membership active/inactive totals count recorded statuses across
memberships, not mutually exclusive current states. Reports include ties; unused
rooms and unbooked equipment are excluded from their utilisation summaries.

`InsertData.txt` contains fictional sample contact details, confirmed by the
project owner. PDFs, database exports, credentials and generated output are not
part of this repository.
