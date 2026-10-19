"""Exercise the actual summary SELECTs with isolated, synthetic data.

Run: python -m unittest discover -s tests -v
SQLite checks aggregation/filtering only, not Oracle or SQL*Plus rendering.
The adapter handles only TO_DATE, TO_CHAR and EXTRACT used by these reports.
"""
from pathlib import Path
import re
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORTS = {
    "attendance": "CheahYongShun_MemberClassAttendanceReport.txt",
    "room": "LamYiHen_RoomUtilisationReport.txt",
    "equipment": "LimJunYi_EquipmentUsageReport.txt",
    "membership": "TanYiHeng_MembershipStatusReport.txt",
}


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.create_function("TO_DATE", 2, lambda value, fmt: value)
        self.db.create_function("TO_CHAR", 1, lambda value: str(value))
        self.db.executescript("""
            CREATE TABLE Member(MemberID TEXT, Name TEXT);
            CREATE TABLE Membership(MembershipID TEXT, MemberID TEXT, PlanID TEXT, Status TEXT);
            CREATE TABLE MembershipPlan(PlanID TEXT, PlanName TEXT);
            CREATE TABLE Payment(PaymentID TEXT, MembershipID TEXT);
            CREATE TABLE Room(RoomID TEXT, RoomName TEXT);
            CREATE TABLE Coach(CoachID TEXT);
            CREATE TABLE ClassScheduled(ScheduledID TEXT, RoomID TEXT, CoachID TEXT, ClassDate TEXT);
            CREATE TABLE Booking(ScheduledID TEXT, MemberID TEXT, Attendance TEXT);
            CREATE TABLE Equipment(EquipmentID TEXT, EquipmentName TEXT);
            CREATE TABLE EquipmentBooking(EquipmentBookingID TEXT, EquipmentID TEXT, BookingDate TEXT);
            CREATE TABLE dual(dummy TEXT);
            INSERT INTO dual VALUES ('X');
        """)

    def summary(self, report, **variables):
        text = (ROOT / REPORTS[report]).read_text(encoding="utf-8")
        self.assertIn("PROMPT Summary for the report:", text)
        tail = text.split("PROMPT Summary for the report:", 1)[1]
        match = re.search(r"(?ims)^WITH\b.*?;", tail)
        self.assertIsNotNone(match, "Missing summary query")
        sql = match.group(0)
        values = dict(v_start_date="2025-01-01", v_end_date="2025-01-31",
                      v_month="01", v_year="2025", v_status="Active")
        values.update(variables)
        for name, value in values.items():
            sql = sql.replace("&" + name, value)
        sql = re.sub(r"EXTRACT\((MONTH|YEAR) FROM ([\w.]+)\)",
                     lambda m: "CAST(strftime('%" + ("m" if m[1] == "MONTH" else "Y")
                     + "', " + m[2] + ") AS INTEGER)", sql, flags=re.I)
        return [row[0] for row in self.db.execute(sql)]

    def test_attendance_counts_and_period(self):
        self.db.executescript("""
            INSERT INTO Member VALUES ('M1','A'),('M2','B');
            INSERT INTO Room VALUES ('R1','Room A');
            INSERT INTO Coach VALUES ('C1');
            INSERT INTO ClassScheduled VALUES
                ('S1','R1','C1','2025-01-01'),('S2','R1','C1','2025-01-31'),
                ('S3','R1','C1','2025-02-01');
            INSERT INTO Booking VALUES ('S1','M1','Present'),('S1','M2','Absent'),
                ('S2','M1','Present'),('S3','M2','Present');
        """)
        self.assertEqual(self.summary("attendance"), ["Total Attendance Records: 3",
                         "Total Present Records: 2", "Total Absent Records: 1"])

    def test_empty_attendance(self):
        self.assertEqual(self.summary("attendance"), ["Total Attendance Records: 0",
                         "Total Present Records: 0", "Total Absent Records: 0"])

    def test_room_extremes_ties_and_month(self):
        self.db.executescript("""
            INSERT INTO Room VALUES ('R1','A'),('R2','B'),('R3','C'),('R4','Unused');
            INSERT INTO ClassScheduled VALUES
                ('S1','R1','C1','2025-01-01'),('S2','R1','C1','2025-01-02'),
                ('S3','R2','C1','2025-01-01'),('S4','R2','C1','2025-01-02'),
                ('S5','R3','C1','2025-01-01'),('S6','R3','C1','2025-02-01');
        """)
        self.assertEqual(self.summary("room"), ["High-Usage Room: A (classes: 2)",
                         "High-Usage Room: B (classes: 2)", "Low-Usage Room: C (classes: 1)"])

    def test_room_empty_and_equal_usage(self):
        self.assertEqual(self.summary("room"), ["No classes in the selected month/year."])
        self.db.executescript("""
            INSERT INTO Room VALUES ('R1','A'),('R2','B');
            INSERT INTO ClassScheduled VALUES
                ('S1','R1','C1','2025-01-01'),('S2','R2','C1','2025-01-01');
        """)
        self.assertEqual(self.summary("room"), ["Equal-Usage Room: A (classes: 1)",
                                               "Equal-Usage Room: B (classes: 1)"])

    def test_equipment_groups_and_period(self):
        for i, count in enumerate([4, 4, 3, 2, 1, 1], 1):
            self.db.execute("INSERT INTO Equipment VALUES (?,?)", (str(i), "Item " + str(i)))
            for j in range(count):
                self.db.execute("INSERT INTO EquipmentBooking VALUES (?,?,?)",
                                (f"{i}-{j}", str(i), "2025-01-01"))
        self.db.execute("INSERT INTO EquipmentBooking VALUES ('outside','6','2025-02-01')")
        self.assertEqual(self.summary("equipment"), ["Most used equipment: 2 (bookings each: 4)",
                         "Regularly used equipment: 2 (between 1 and 4 bookings each, exclusive)",
                         "Least used equipment: 2 (bookings each: 1)"])

    def test_equipment_empty_and_equal_usage(self):
        self.assertEqual(self.summary("equipment"), ["No equipment bookings in the selected period."])
        self.db.executescript("""
            INSERT INTO Equipment VALUES ('E1','A'),('E2','B');
            INSERT INTO EquipmentBooking VALUES ('B1','E1','2025-01-01'),('B2','E2','2025-01-01');
        """)
        self.assertEqual(self.summary("equipment"), ["All equipment equally used: 2 (bookings each: 1)"])

    def test_membership_counts_do_not_multiply_payments_and_show_plan_ties(self):
        self.db.executescript("""
            INSERT INTO Member VALUES ('M1','A'),('M2','B'),('M3','C');
            INSERT INTO MembershipPlan VALUES ('P1','Annual'),('P2','Monthly');
            INSERT INTO Membership VALUES ('S1','M1','P1','Active'),
                ('S2','M2','P2','Active'),('S3','M3','P1','Inactive');
            INSERT INTO Payment VALUES ('X1','S1'),('X2','S1'),('X3','S2'),('X4','S3');
        """)
        self.assertEqual(self.summary("membership"), ["Total Active Members: 2",
                         "Total Inactive Members: 1", "Most Popular Plan: Annual (members: 1)",
                         "Most Popular Plan: Monthly (members: 1)"])
        self.assertEqual(self.summary("membership", v_status="Inactive"), ["Total Active Members: 2",
                         "Total Inactive Members: 1", "Most Popular Plan: Annual (members: 1)"])

    def test_membership_empty_and_no_matching_status(self):
        self.assertEqual(self.summary("membership"), ["Total Active Members: 0",
                         "Total Inactive Members: 0", "Most Popular Plans: none for selected status."])


if __name__ == "__main__":
    unittest.main()
