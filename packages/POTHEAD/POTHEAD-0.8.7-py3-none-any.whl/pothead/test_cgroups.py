from math import inf
from time import monotonic
from unittest import TestCase
from random import random

from .cgroups import parse_cpu_quota_v1, parse_cpu_quota_v2, get_cpu_used


class CgroupsTest(TestCase):
    def test_v1_valid(self):
        assert parse_cpu_quota_v1("500000", "500000") == 1.0
        assert parse_cpu_quota_v1("200000", "500000") == 0.4
        assert parse_cpu_quota_v1("-1", "500000") == inf

    def test_v1_invalid(self):
        self.verify_exception_with_msg(
            lambda: parse_cpu_quota_v1("0", "500000"), "Quota for cgroups v1 was 0"
        )

    def test_v2_valid(self):
        assert parse_cpu_quota_v2("500000 500000") == 1.0
        assert parse_cpu_quota_v2("200000 500000") == 0.4
        assert parse_cpu_quota_v2("max 500000") == inf

    def test_v2_invalid(self):
        self.verify_exception_with_msg(
            lambda: parse_cpu_quota_v2("0 500000"),
            "Quota in cgroups v2 cpu.max file was <= 0. Content: 0 500000",
        )
        self.verify_exception_with_msg(
            lambda: parse_cpu_quota_v2("-1 500000"),
            "Quota in cgroups v2 cpu.max file was <= 0. Content: -1 500000",
        )
        self.verify_exception_with_msg(
            lambda: parse_cpu_quota_v2("200000 0"),
            "Period in cgroups v2 cpu.max file was <= 0. Content: 200000 0",
        )
        self.verify_exception_with_msg(
            lambda: parse_cpu_quota_v2("200000 -1"),
            "Period in cgroups v2 cpu.max file was <= 0. Content: 200000 -1",
        )

    def test_get_cpu_used(self):
        t1 = monotonic()
        cu1 = get_cpu_used()
        x = 0
        for _ in range(10):
            for _ in range(100000):
                x += random()

            t2 = monotonic()
            cu2 = get_cpu_used()

            time_elapsed = t2 - t1
            cpu_used = cu2 - cu1
            # We're very lenient here, since tests could be running on an overbooked
            # and not have access to the full CPU
            assert cpu_used > time_elapsed * 0.5, "Expected test to consume > 50% CPU"
            (t1, cu1) = (t2, cu2)

    def verify_exception_with_msg(self, func, msg):
        with self.assertRaises(Exception) as ctx:
            func()
        assert str(ctx.exception) == msg
