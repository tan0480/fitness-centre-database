# Report summaries

The four existing report scripts now print a calculated summary after their
detail output, following presentation slides 15, 17, 19 and 21. Filenames and
the original detail queries are preserved. Run each script as before in SQL*Plus.
No database writes are added.

## Calculation scope

- **Attendance:** the same joins and inclusive ClassDate range as the detail
  report; counts all records and the Present/Absent subsets.
- **Rooms:** the same month/year and room-name groups as the detail report.
  High/low means the maximum/minimum class count, including all ties. Unused
  rooms are excluded, as in the original report. If all counts match, rooms
  are labelled equal usage rather than appearing twice.
- **Equipment:** the same BookingDate range and equipment-name groups as the
  detail report. Most/least means maximum/minimum bookings; regularly used
  groups fall strictly between them. Unbooked equipment is excluded. Equal
  usage and empty periods have explicit messages.
- **Membership:** active/inactive totals count distinct members per recorded
  status across all memberships, regardless of the selected detail status.
  A member with both active and historical inactive memberships counts in both
  totals; these are not mutually exclusive current-status counts. Popular plans
  use the selected status and the detail report's payment-existence requirement,
  count distinct members per plan, and include all ties. Multiple payments do
  not multiply the member counts.

The slide numbers are examples, not constants. The current seed data is not
identical to every slide example, so calculated results can differ.

## Checks

From this folder, run `python -B -m unittest discover -s tests -v`.
The tests execute the summary SELECTs against synthetic data in SQLite with a
small Oracle-function adapter. They check aggregates, filters, ties, empty
results and duplicate payments. They do not prove Oracle compatibility or
SQL*Plus rendering; run the scripts in Oracle/SQL*Plus before publishing.

SQL*Plus formatting reference:
https://docs.oracle.com/database/121/SQPUG/ch_six.htm
