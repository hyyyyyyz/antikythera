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
        groups = [
            group(END, 2),
            group(END, 4),
            group(END, 7, "PRIVATE"),
            group(END, 3, "INTERNAL"),
        ]
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
            self.assertIn("parked", svg.find("s:desc", SVG).text)

    def test_only_real_active_dates_are_animated(self):
        last = END - timedelta(days=35)
        counts = {last: 5, END - timedelta(days=390): 100}
        svg = ET.fromstring(render("name&name", END, counts))
        self.assertIn("name&name", svg.find("s:title", SVG).text)
        self.assertIn("5 public commit", svg.find("s:desc", SVG).text)
        selected = [
            cell.get("data-day")
            for cell in svg.findall("s:g[@data-day]", SVG)
            if cell.find("s:g[@class='moving']", SVG) is not None
        ]
        self.assertEqual(selected, [str(last)])
        cell = svg.find(f"s:g[@data-day='{last}']", SVG)
        self.assertEqual(
            cell.find("s:g[@class='still']/s:rect", SVG).get("class"), "l4"
        )
        visibility = cell.find("s:g[@class='moving']/s:animate", SVG)
        self.assertEqual(visibility.get("values").split(";"), ["1", "0", "1", "1"])
        self.assertIn("prefers-reduced-motion", svg.find("s:style", SVG).text)
        self.assertIsNotNone(
            svg.find("s:g[@class='still']/s:g[@data-part='shuttle']", SVG)
        )
        self.assertFalse(svg.findall(".//s:image", SVG))
        ids = {node.get("id") for node in svg.iter() if node.get("id")}
        animations = svg.findall(".//s:animate", SVG) + svg.findall(
            ".//s:animateTransform", SVG
        )
        self.assertTrue(animations)
        self.assertEqual(len({a.get("dur") for a in animations}), 1)
        for a in animations:
            self.assertEqual(a.get("repeatCount"), "indefinite")
            times = [float(t) for t in a.get("keyTimes").split(";")]
            values = a.get("values").split(";")
            self.assertEqual((times[0], times[-1]), (0, 1))
            self.assertTrue(all(t < u for t, u in zip(times, times[1:])))
            self.assertEqual(len(times), len(values))
            self.assertEqual(values[0], values[-1])
            if a.get("attributeName") == "href":
                self.assertTrue(all(v[0] == "#" and v[1:] in ids for v in values))
        for use in svg.findall(".//s:use", SVG):
            self.assertIn(use.get("href")[1:], ids)

    def test_chip_thresholds(self):
        for i, (threshold, _, _) in enumerate(BANDS):
            self.assertEqual(level(threshold), i)
            if i:
                self.assertEqual(level(threshold - 1), i - 1)
        self.assertEqual(level(1000), 9)

    def test_one_strip_at_extreme_positions(self):
        for offset in (0, 1, 3, 177, 180, 184, 360, 364):
            counts = {END - timedelta(days=offset): 84}
            board = ET.fromstring(render("demo", END, counts))
            cells = [
                g
                for g in board.findall("s:g", SVG)
                if g.find("s:title", SVG) is not None
            ]
            positions = [g.get("transform").split("(")[1][:-1].split() for g in cells]
            self.assertEqual(len(cells), 365)
            self.assertEqual(len({x for x, _ in positions}), 53)
            self.assertEqual(len({y for _, y in positions}), 7)
            self.assertFalse(board.findall(".//s:text", SVG))
            self.assertIn("prefers-color-scheme:dark", board.find("s:style", SVG).text)


if __name__ == "__main__":
    unittest.main()
