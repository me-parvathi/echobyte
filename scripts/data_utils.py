#!/usr/bin/env python3
"""
Shared date-/random-utility helpers for the new data-generation pipeline.
These functions are intentionally standalone so they can be reused by every
seeder module without pulling in heavy third-party deps beyond the stdlib & Faker.
"""
from __future__ import annotations

import datetime as dt
import random
from typing import Tuple, List

_RAND = random.Random()

# ----------------------------------------------------------------------------
# RANDOM DATE HELPERS
# ----------------------------------------------------------------------------

def seed_rng(seed: int | None = None) -> None:
    """Seed the internal module-level RNG so downstream calls are repeatable."""
    _RAND.seed(seed)


def rand_past_datetime(start: dt.datetime | None = None,
                        end: dt.datetime | None = None) -> dt.datetime:
    """Return a random UTC timestamp between *start* and *end* (exclusive).

    If *start* is omitted, defaults to 5 years ago.  If *end* is omitted,
    defaults to now (UTC).
    """
    if end is None:
        end = dt.datetime.utcnow()
    if start is None:
        start = end - dt.timedelta(days=5 * 365)

    start_ts = start.timestamp()
    end_ts = end.timestamp()
    if end_ts <= start_ts:
        raise ValueError("end must be after start")

    return dt.datetime.fromtimestamp(_RAND.uniform(start_ts, end_ts), tz=dt.timezone.utc)


def ensure_created_before_updated(created_at: dt.datetime,
                                  min_delta_sec: int = 0,
                                  max_delta_sec: int = 60 * 60 * 24 * 120) -> Tuple[dt.datetime, dt.datetime]:
    """Given a *created_at* value, return a tuple `(created_at, updated_at)` where
    *updated_at* is guaranteed to be >= *created_at* by at least *min_delta_sec*
    and at most *max_delta_sec* seconds.
    """
    if min_delta_sec < 0:
        raise ValueError("min_delta_sec cannot be negative")
    if max_delta_sec < min_delta_sec:
        raise ValueError("max_delta_sec must be >= min_delta_sec")

    delta = _RAND.randint(min_delta_sec, max_delta_sec)
    updated_at = created_at + dt.timedelta(seconds=delta)
    return created_at, updated_at


# ----------------------------------------------------------------------------
# PERIOD / OVERLAP UTILITIES
# ----------------------------------------------------------------------------

def periods_overlap(a_start: dt.date, a_end: dt.date, b_start: dt.date, b_end: dt.date) -> bool:
    """Return True if [a_start, a_end] overlaps with [b_start, b_end] (inclusive)."""
    return not (a_end < b_start or b_end < a_start)


def find_non_overlapping_period(existing: List[Tuple[dt.date, dt.date]],
                                period_days: int,
                                search_from: dt.date,
                                search_to: dt.date) -> Tuple[dt.date, dt.date]:
    """Find a date span of *period_days* days within [search_from, search_to]
    that does not overlap any of *existing* periods (list of tuples).

    Raises RuntimeError if no such slot is found after 500 attempts.
    """
    attempts = 0
    while attempts < 500:
        attempts += 1
        start = search_from + dt.timedelta(days=_RAND.randint(0, (search_to - search_from).days - period_days))
        end = start + dt.timedelta(days=period_days)
        if all(not periods_overlap(start, end, ex_start, ex_end) for ex_start, ex_end in existing):
            return start, end
    raise RuntimeError("Unable to find non-overlapping period after 500 attempts")
