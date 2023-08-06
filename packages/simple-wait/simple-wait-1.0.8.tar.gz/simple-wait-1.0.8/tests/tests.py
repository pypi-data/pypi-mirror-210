#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ipetrash"


import io
import unittest

from datetime import timedelta, datetime

from src.simple_wait import str_timedelta, get_timeout_date, wait


class TestCase(unittest.TestCase):
    timedelta_cases: list[dict[str, int]] = [
        ("00:00:10", dict(seconds=10)),
        ("00:00:10", dict(seconds=10, milliseconds=150)),
        (
            "10:40:30",
            dict(hours=10, minutes=40, seconds=30, milliseconds=100, microseconds=100),
        ),
        ("1 day, 6:00:00", dict(hours=30)),
        ("1 day, 6:00:00", dict(days=1, hours=6)),
        ("14 days, 0:00:00", dict(weeks=2)),
        (
            "8 days, 2:10:20",
            dict(
                weeks=1,
                days=1,
                hours=2,
                minutes=10,
                seconds=20,
                milliseconds=100,
                microseconds=100,
            ),
        ),
    ]

    def test_str_timedelta(self):
        for expected, actual in self.timedelta_cases:
            with self.subTest(expected, **actual):
                self.assertEqual(
                    expected,
                    str_timedelta(timedelta(**actual)),
                )

    def test_get_timeout_date(self):
        with self.subTest("None"):
            now = datetime.today()

            self.assertTrue(get_timeout_date())
            self.assertTrue(get_timeout_date(now))
            self.assertEqual(now, get_timeout_date(now))

        with self.subTest("Simple"):
            now = datetime.today()
            self.assertEqual(
                now + timedelta(hours=2, minutes=10, seconds=20),
                get_timeout_date(now, hours=2, minutes=10, seconds=20),
            )

        for _, actual in self.timedelta_cases:
            with self.subTest(actual):
                now = datetime.today()
                self.assertEqual(
                    now + timedelta(**actual), get_timeout_date(now, **actual)
                )

    def test_wait(self):
        log = io.TextIOWrapper(
            buffer=io.BytesIO(),
            encoding="utf-8",
        )
        wait(seconds=3, log=log)

        log.seek(0)
        lines = [
            line.strip() for line in log.readlines() if "Time left to wait" in line
        ]
        self.assertTrue(lines)
        self.assertTrue(len(lines) > 1)


if __name__ == "__main__":
    unittest.main()
