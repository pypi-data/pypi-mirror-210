from math import inf
from os.path import isfile
from multiprocessing import cpu_count

CGROUPS_FS_PREFIX = "/sys/fs/cgroup"

CGROUPS_V1_CPU_QUOTA = f"{CGROUPS_FS_PREFIX}/cpu/cpu.cfs_quota_us"
CGROUPS_V1_CPU_PERIOD = f"{CGROUPS_FS_PREFIX}/cpu/cpu.cfs_period_us"
CGROUPS_V1_CPUACCT_USAGE = f"{CGROUPS_FS_PREFIX}/cpu/cpuacct.usage"
CGROUPS_V2_CPU_MAX = f"{CGROUPS_FS_PREFIX}/cpu.max"
CGROUPS_V2_CPU_STAT = f"{CGROUPS_FS_PREFIX}/cpu.stat"


def get_cgroups_cpu_quota() -> float:
    if isfile(CGROUPS_V2_CPU_MAX):
        return get_cpu_quota_v2()
    elif isfile(CGROUPS_V1_CPU_QUOTA):
        return get_cpu_quota_v1()
    else:
        return cpu_count()


# Documentation: https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
def get_cpu_quota_v2() -> float:
    with open(CGROUPS_V2_CPU_MAX, "rt") as cpu_max:
        cpu_max_line = cpu_max.read()
        return parse_cpu_quota_v2(cpu_max_line)


def get_cpu_used() -> float:
    if isfile(CGROUPS_V2_CPU_STAT):
        return get_cpu_used_v2()
    elif isfile(CGROUPS_V1_CPUACCT_USAGE):
        return get_cpu_used_v1()
    else:
        assert False, "Found no recognised cgroup to extract CPU for"


def get_cpu_used_v1():
    with open(CGROUPS_V1_CPUACCT_USAGE, "rt") as container_cpu_stat:
        return int(container_cpu_stat.read().strip()) / 1_000_000_000


def get_cpu_used_v2():
    with open(CGROUPS_V2_CPU_STAT, "rt") as container_cpu_stat:
        for line in container_cpu_stat.readlines():
            if line.startswith("usage_usec "):
                return int(line.strip().split()[1]) / 1_000_000


def parse_cpu_quota_v2(cpu_max_line: str) -> float:
    words = cpu_max_line.split()
    if len(words) != 2:
        raise Exception(
            f"Unexpected content in cgroups v2 cpu.max file: {cpu_max_line}"
        )

    (quota_str, period_str) = words
    if quota_str == "max":
        return inf

    quota = int(quota_str)
    period = int(period_str)
    if quota <= 0:
        raise Exception(
            f"Quota in cgroups v2 cpu.max file was <= 0. Content: {cpu_max_line}"
        )
    if period <= 0:
        raise Exception(
            f"Period in cgroups v2 cpu.max file was <= 0. Content: {cpu_max_line}"
        )

    return quota / period


# Documentation: https://www.kernel.org/doc/Documentation/scheduler/sched-bwc.txt
def get_cpu_quota_v1() -> float:
    with open(CGROUPS_V1_CPU_QUOTA, "rt") as quota, open(
        CGROUPS_V1_CPU_PERIOD, "rt"
    ) as period:
        quota_line = quota.read()
        period_line = period.read()
        return parse_cpu_quota_v1(quota_line, period_line)


def parse_cpu_quota_v1(quota_line: str, period_line: str) -> float:
    quota = int(quota_line)
    if quota > 0:
        period = int(period_line)
        return quota / period
    elif quota == 0:
        raise Exception("Quota for cgroups v1 was 0")
    else:
        # A quota of -1 means "no restriction"
        return inf
