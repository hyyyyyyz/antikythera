from dataclasses import replace
from datetime import date, timedelta
from math import hypot
from pathlib import Path
import unittest

from artwork import read_plate, studio_plate
from board import calendar_days
from mechanism import (
    CELL,
    PITCH,
    TOP,
    Mission,
    calendar_seed,
    rig,
    screen_flash,
    screen_grip,
)

END = date(2026, 11, 18)
GALLERY = Path(__file__).resolve().parents[1] / "gallery" / "artwork" / "gaia.svg"


class CalendarMission(unittest.TestCase):
    def setUp(self):
        self.year = calendar_days(END, {END - timedelta(days=i): 3 for i in range(365)})
        self.tips = rig()

    def mission(self, days, user="sample", plate=None):
        return Mission(
            days, self.tips, plate or studio_plate(), calendar_seed(user, END, days)
        )

    def test_empty_year_rests(self):
        mission = self.mission([])
        self.assertFalse(mission.shots)
        self.assertEqual((mission.time, mission.hoist, len(mission.frames)), (0, 0, 1))

    def test_every_active_date_clears_before_the_flag(self):
        m = self.mission(self.year)
        self.assertCountEqual([s.tile for s in m.shots], self.year)
        self.assertTrue(
            all(a.fired < a.hit < b.fired for a, b in zip(m.shots, m.shots[1:]))
        )
        self.assertGreater(m.hoist, m.shots[-1].hit)
        self.assertGreater(m.time - m.hoist, 2400)
        self.assertLess(m.time, 65000)
        self.assertTrue(all(a.ms < b.ms for a, b in zip(m.frames, m.frames[1:])))
        self.assertGreater(len({f.pose for f in m.frames}), 5)
        self.assertEqual(m.frames[0].pose, m.frames[-1].pose)

    def test_shuffle_is_repeatable_and_unaffected_by_count_edits(self):
        days = self.year[::3]

        def order(m):
            return [s.tile.day for s in m.shots]

        seq = order(self.mission(days))
        self.assertNotEqual(seq, sorted(seq))
        self.assertEqual(
            seq, order(self.mission([replace(s, count=s.count + 1) for s in days]))
        )
        self.assertNotEqual(seq, order(self.mission(days, "another")))

    def test_pulses_start_at_the_art_and_end_on_the_calendar(self):
        for plate in (studio_plate(), read_plate(GALLERY)):
            mission = self.mission(self.year, plate=plate)
            states = {f.ms: f for f in mission.frames}
            for shot in mission.shots:
                frame = states[shot.fired]
                self.assertEqual(
                    shot.muzzle,
                    screen_flash(
                        screen_grip(self.tips[frame.pose]),
                        plate.pulse_offset,
                        frame.angle,
                    ),
                )
                self.assertEqual(
                    shot.target, (shot.tile.x, TOP + shot.tile.row * PITCH + CELL / 2)
                )
                self.assertGreater(shot.muzzle[0], shot.target[0])
                self.assertGreater(
                    hypot(
                        shot.target[0] - shot.muzzle[0], shot.target[1] - shot.muzzle[1]
                    ),
                    5,
                )
