from datetime import date, timedelta
import unittest
from xml.etree import ElementTree as ET

from board import BANDS, level, render
from calendar_data import daily_commits

SVG = {"s": "http://www.w3.org/2000/svg"}
END = date(2026, 11, 18)


def group(day, commits=1, visibility="PUBLIC", more=False):
    return {
        "repository": {"visibility": visibility},
        "contributions": {
            "pageInfo": {"hasNextPage": more},
            "nodes": [{"occurredAt": f"{day}T08:00:00Z", "commitCount": commits}],
        },
    }


class Contributions(unittest.TestCase):
    def test_public_counts_merge_across_repositories(self):
        groups = [group(END, 2), group(END, 4), group(END, 7, "PRIVATE"), group(END, 3, "INTERNAL")]
        self.assertEqual(daily_commits("demo", END, END, lambda *_: groups), {END: 6})

    def test_split_limited_windows_without_double_counting(self):
        start = END - timedelta(days=1)
        def fetch(user, first, last):
            if first != last:
                return [group(first, 99, more=True)]
            return [group(first, 2)]
        self.assertEqual(daily_commits("demo", start, END, fetch), {start: 2, END: 2})

    def test_error_for_incomplete_single_day(self):
        with self.assertRaisesRegex(ValueError, "complete count"):
            daily_commits("demo", END, END, lambda *_: [group(END)] * 100)


class Drawing(unittest.TestCase):
    def test_layout_for_every_weekday_and_leap_day(self):
        for delta in range(7):
            end = date(2024, 2, 29) + timedelta(days=delta)
            svg = ET.fromstring(render("demo", end, {}))
            sockets = svg.findall(".//s:g/s:title", SVG)
            self.assertEqual(len(sockets), 365)
            self.assertIn(str(end - timedelta(days=364)), sockets[0].text)
            self.assertIn(str(end), sockets[-1].text)
            self.assertFalse(svg.findall(".//s:animate", SVG))

    def test_motion_targets_last_active_day_and_stops(self):
        last = END - timedelta(days=35)
        svg = ET.fromstring(render("name&name", END, {last: 5, END-timedelta(days=390): 100}))
        self.assertIn("5 public commit", svg.find("s:desc", SVG).text)
        animated_socket = None
        for cell in svg.findall(".//s:g", SVG):
            if cell.find("s:title", SVG) is not None and cell.find("s:g[@class='cycle']", SVG) is not None:
                animated_socket = cell
                break
        self.assertIsNotNone(animated_socket)
        self.assertIn(str(last), animated_socket.find("s:title", SVG).text)
        self.assertIn("prefers-reduced-motion", svg.find("s:style", SVG).text)
        for animation in svg.findall(".//s:animate", SVG) + svg.findall(".//s:animateTransform", SVG):
            self.assertEqual(animation.get("fill"), "freeze")
            self.assertNotEqual(animation.get("repeatCount"), "indefinite")

    def test_chip_thresholds(self):
        for i, (threshold, _, _) in enumerate(BANDS):
            self.assertEqual(level(threshold), i)
            if i:
                self.assertEqual(level(threshold - 1), i - 1)
        self.assertEqual(level(1000), 9)

    def test_mobile_calendar_matches_desktop_at_extreme_rail_positions(self):
        for offset in (0, 1, 3, 177, 180, 184, 360, 364):
            day = END - timedelta(days=offset)
            counts = {day: 84}
            boards = [ET.fromstring(render("demo", END, counts, compact=mode)) for mode in (False, True)]
            self.assertEqual([b.find("s:desc", SVG).text for b in boards], [boards[0].find("s:desc", SVG).text]*2)
            for board in boards:
                self.assertEqual(len(board.findall(".//s:g/s:title", SVG)),365)
                labels = [node.text for node in board.findall(".//s:text", SVG)]
                self.assertTrue(all(caption in labels for _, _, caption in BANDS))



if __name__ == "__main__":
    unittest.main()
