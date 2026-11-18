from datetime import date, timedelta
from pathlib import Path

from artwork import read_plate
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
            sockets = svg.findall(".//s:g[@data-day]/s:title", SVG)
            self.assertEqual(len(sockets), 365)
            self.assertIn(str(end - timedelta(days=364)), sockets[0].text)
            self.assertIn(str(end), sockets[-1].text)
            self.assertFalse(svg.findall(".//s:animate", SVG))
            self.assertIn("rests", svg.find("s:desc", SVG).text)

    def test_only_real_active_dates_are_animated(self):
        last = END - timedelta(days=35)
        counts = {last: 5, END - timedelta(days=390): 100}
        svg = ET.fromstring(render("name&name", END, counts))
        self.assertIn("name&name", svg.find("s:title", SVG).text)
        self.assertIn("5 public commit", svg.find("s:desc", SVG).text)
        cell = svg.find(f".//s:g[@data-day='{last}']", SVG)
        self.assertEqual(cell.get("class"), "l4")
        selected = svg.findall(".//s:g[@data-target]", SVG)
        self.assertEqual(len(selected), 1)
        self.assertEqual(
            [u.get("href") for u in selected[0].findall("s:use", SVG)],
            ["#" + cell.get("id")],
        )
        visibility = selected[0].find("s:animate", SVG)
        self.assertEqual(visibility.get("values").split(";"), ["1", "0", "0"])
        for scene in ("moving", "still"):
            arms = svg.findall(f"s:g[@class='{scene}']/s:g[@data-arm='panda']", SVG)
            self.assertEqual(len(arms), 1)
            self.assertIsNone(arms[0].find("s:animateTransform", SVG))
        platform = svg.findall(".//s:g[@data-part='fixed-platform']", SVG)
        self.assertEqual(len(platform), 1)
        self.assertIsNone(platform[0].find(".//s:animateTransform", SVG))
        self.assertIsNone(svg.find(".//s:g[@data-part='transmission']", SVG))
        self.assertEqual(len(svg.findall(".//s:g[@data-part='victory-flag']", SVG)), 1)
        still = svg.find("s:g[@class='still']", SVG)
        self.assertIsNone(still.find(".//s:g[@data-part='victory-flag']", SVG))
        self.assertIsNone(still.find(".//s:path[@data-part='pulse']", SVG))
        self.assertIn("prefers-reduced-motion", svg.find("s:style", SVG).text)
        self.assertIsNotNone(
            svg.find("s:g[@class='still']/s:g[@data-arm='panda']", SVG)
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
            if a.get("attributeName") == "href":
                self.assertTrue(all(v[0] == "#" and v[1:] in ids for v in values))
        for use in svg.findall(".//s:use", SVG):
            self.assertIn(use.get("href")[1:], ids)

    def test_gallery_includes_the_model_credit_and_embedded_art(self):
        example = (
            Path(__file__).resolve().parents[1] / "gallery" / "artwork" / "gaia.svg"
        )
        svg = ET.fromstring(render("sample", END, {END: 1}, read_plate(example)))
        wrist = svg.find(".//s:g[@id='prop-art']", SVG)
        self.assertEqual(
            wrist.findtext("s:title", namespaces=SVG), "Gaia’s Vengeance Vandal"
        )
        self.assertIn("ILilMitch", svg.findtext("s:metadata", namespaces=SVG))
        self.assertIn("Riot Games", svg.findtext("s:metadata", namespaces=SVG))
        self.assertTrue(wrist.findall(".//s:path", SVG))
        self.assertIsNone(svg.find(".//s:image", SVG))
        for grip in svg.findall(".//s:g[@data-part='grip']", SVG):
            layers = [
                e.get("href") or e.get("data-part")
                for e in grip
                if e.tag != "{" + SVG["s"] + "}animateTransform"
            ]
            self.assertEqual(layers, ["#h0", "wrist-art", "#finger0"])

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
                for g in board.findall(".//s:g[@data-day]", SVG)
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
