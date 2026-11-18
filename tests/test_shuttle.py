from collections import Counter
from dataclasses import replace
from datetime import date, timedelta
import unittest

from mechanism import LEFT, Route, Stop, rig, route_stops


class Shuttle(unittest.TestCase):
    def setUp(self):
        self.model = rig()
        self.geometry = self.model["geometry"]

    def stop(self, week, row, count=8):
        day = date(2025, 11, 16) + timedelta(days=week * 7 + row)
        x = LEFT + week * self.geometry["pitch"] + self.geometry["size"] / 2
        return Stop(day, x, row, count, 5)

    def test_selects_distinct_occupied_days_including_the_latest(self):
        active = [self.stop(i, i % 7, count=53 - i) for i in range(53)]
        selected = route_stops(active)
        self.assertEqual(len(set(selected)), 6)
        self.assertEqual(selected[0], active[-1])
        self.assertEqual(selected[-1], active[0])
        self.assertTrue(all(a.day > b.day for a, b in zip(selected, selected[1:])))
        self.assertEqual(route_stops([]), [])

    def test_parked_when_empty(self):
        frames = Route([], self.model).frames
        self.assertEqual(len(frames), 1)
        self.assertIsNone(frames[0].held)
        self.assertEqual(frames[0].cargo, ())

    def test_all_transfers_match_the_projected_pinch_location(self):
        cases = [
            [self.stop(52, 0)],
            [self.stop(0, 6)],
            [self.stop(50 - i * 8, row) for i, row in enumerate((1, 5, 2, 4, 0, 3))],
            [self.stop(20, row) for row in (6, 4, 3)],
        ]
        for stops in cases:
            with self.subTest(stops=len(stops), first=stops[0].day):
                frames = Route(stops, self.model).frames
                self.assertEqual(replace(frames[-1], ms=0), frames[0])
                self.assertTrue(
                    any(a.x != b.x and b.cargo for a, b in zip(frames, frames[1:]))
                )
                events = Counter()
                for before, now in zip(frames, frames[1:]):
                    self.assertGreater(now.ms, before.ms)
                    self.assertNotIn(now.held, now.cargo)
                    self.assertEqual(len(set(now.cargo)), len(now.cargo))
                    self.assertLessEqual(len(now.cargo), len(self.model["slots"]))
                    self.assertTrue(set(now.cargo).issubset(stops))
                    self.assertTrue(0 <= now.wheel < self.model["wheel_frames"])
                    if before.x == now.x:
                        self.assertEqual(before.wheel, now.wheel)
                    else:
                        self.assertEqual((now.pose, now.jaw, now.held), (0, 0, None))
                        self.assertEqual(before.cargo, now.cargo)

                    if before.held == now.held:
                        continue
                    item = now.held or before.held
                    self.assertIn(item, stops)
                    self.assertEqual(now.jaw, 2)
                    arriving = now.held is None
                    cargo = now.cargo if arriving else before.cargo
                    at_tray = item in cargo
                    if at_tray:
                        slot = cargo.index(item)
                        tray_pose = self.model["slots"][slot][-1]
                        expected = self.model["tip"][tray_pose]
                        self.assertEqual(now.pose, tray_pose)
                    else:
                        center_y = (
                            self.geometry["top"]
                            + item.row * self.geometry["pitch"]
                            + self.geometry["size"] / 2
                        )
                        expected = (item.x - now.x, center_y - self.geometry["road_y"])
                        self.assertEqual(now.pose, self.model["cells"][item.row][-1])
                    actual = self.model["tip"][now.pose]
                    for coordinate, target in zip(actual, expected):
                        self.assertAlmostEqual(coordinate, target, delta=0.02)
                    events[item, at_tray, arriving] += 1
                self.assertEqual(
                    events,
                    Counter(
                        (item, tray, arriving)
                        for item in stops
                        for tray in (True, False)
                        for arriving in (True, False)
                    ),
                )


if __name__ == "__main__":
    unittest.main()
