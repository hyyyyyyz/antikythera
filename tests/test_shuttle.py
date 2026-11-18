from dataclasses import replace
from datetime import date, timedelta
from math import cos, hypot, radians, sin
import unittest

from mechanism import BARREL, DOCK, LEFT, Route, Stop, calendar_seed, rig

END = date(2026, 11, 18)


class ArcadeMission(unittest.TestCase):
    def setUp(self):
        self.model = rig()
        self.geometry = self.model["geometry"]

    def stop(self, week, row):
        day = date(2025, 11, 16) + timedelta(days=7 * week + row)
        return Stop(
            day,
            LEFT + week * self.geometry["pitch"] + self.geometry["size"] / 2,
            row,
            4,
            4,
        )

    def mission(self, active, username="sample"):
        return Route(active, self.model, calendar_seed(username, END, active))

    def test_empty_mission_is_dormant(self):
        r = self.mission([])
        self.assertEqual((r.time, r.signal, r.hoist), (0, 0, 0))
        self.assertFalse(r.shots)
        self.assertEqual(len(r.frames), 1)

    def test_each_real_tile_goes_dark_once_before_the_antenna_and_flag(self):
        active = [self.stop(i // 7, i % 7) for i in range(365)]
        r = self.mission(active)
        self.assertCountEqual([s.tile for s in r.shots], active)
        self.assertTrue(
            all(a.fired < a.hit < b.fired for a, b in zip(r.shots, r.shots[1:]))
        )
        self.assertLess(r.shots[-1].hit, r.deployment)
        self.assertLess(r.deployment, r.signal)
        self.assertLess(r.signal, r.hoist)
        self.assertLess(r.hoist + 2000, r.time)
        self.assertLess(r.time, 65_000)
        self.assertEqual(r.frames[-1].x, DOCK)
        self.assertLess(min(f.x for f in r.frames), 125)
        self.assertTrue(all(a.ms < b.ms for a, b in zip(r.frames, r.frames[1:])))
        self.assertGreater(len({f.pose for f in r.frames}), 5)

    def test_schedule_is_reproducible_and_varies_between_calendars(self):
        active = [self.stop(w, row) for w in range(0, 53, 3) for row in (0, 3, 6)]
        days = lambda r: [s.tile.day for s in r.shots]
        first = days(self.mission(active))
        self.assertEqual(first, days(self.mission(active)))
        self.assertNotEqual(first, days(self.mission(active, "another")))
        self.assertNotEqual(first, sorted(first))
        # Increasing today's count updates the color without reshuffling the level.
        updated = [replace(s, count=s.count + 1) for s in active]
        self.assertEqual(first, days(self.mission(updated)))

    def test_screen_pulses_leave_the_illustrated_muzzle_and_end_on_their_tiles(self):
        cases = [
            [self.stop(51, 6)],
            [self.stop(0, 0), self.stop(52, 6)],
            [self.stop(w, row) for w in range(53) for row in (0, 3, 6)],
        ]
        for active in cases:
            r = self.mission(active)
            states = {f.ms: f for f in r.frames}
            for s in r.shots:
                f = states[s.fired]
                tip = self.model["tip"][f.pose]
                grip = (f.x + tip[0], self.geometry["road_y"] + tip[1])
                theta = radians(f.angle)
                direction = (cos(theta), sin(theta))
                for axis in range(2):
                    self.assertAlmostEqual(
                        s.muzzle[axis],
                        grip[axis] + BARREL * direction[axis],
                        delta=0.001,
                    )
                dx = s.target[0] - s.muzzle[0]
                dy = s.target[1] - s.muzzle[1]
                self.assertGreater(hypot(dx, dy), 15.9)
                self.assertAlmostEqual(
                    dx * direction[1] - dy * direction[0], 0, delta=0.002
                )
                self.assertEqual(
                    s.target,
                    (
                        s.tile.x,
                        self.geometry["top"]
                        + s.tile.row * self.geometry["pitch"]
                        + self.geometry["size"] / 2,
                    ),
                )


if __name__ == "__main__":
    unittest.main()
