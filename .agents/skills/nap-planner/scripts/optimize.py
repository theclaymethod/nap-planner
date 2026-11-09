#!/usr/bin/env python3
"""Enumerate a bounded grid of nap opportunities; read JSON, write JSON."""

import argparse
import heapq
import json
import sys


def integer(value, name, low=0, high=2880):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def interval(value, name):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{name} must be [start, end]")
    a, b = [integer(v, name) for v in value]
    if a > b:
        raise ValueError(f"{name} start exceeds end")
    return a, b


def optimize(data):
    last = integer(data["last_wake"], "last_wake")
    now = integer(data["now"], "now")
    if now < last:
        raise ValueError("now must be at or after last_wake")
    bed_low, bed_high = interval(data["bedtime_range"], "bedtime_range")
    step = integer(data.get("step_minutes", 5), "step_minutes", 1, 60)
    limit = integer(data.get("max_states", 200000), "max_states", 1, 2000000)
    counts = data["remaining_nap_counts"]
    if not isinstance(counts, list) or not counts:
        raise ValueError("remaining_nap_counts must be a nonempty list")
    counts = sorted(set(integer(n, "nap count", 0, 4) for n in counts))
    wakes = [interval(v, "wake_ranges") for v in data["wake_ranges"]]
    if len(wakes) != max(counts) + 1 or any(a == 0 for a, _ in wakes):
        raise ValueError("wake_ranges needs max nap count + 1 positive ranges")
    durations = data["nap_duration_options"]
    if len(durations) != max(counts):
        raise ValueError("nap_duration_options needs one list per possible nap")
    durations = [sorted(set(integer(v, "nap duration", 1, 240) for v in row))
                 for row in durations]
    if any(not row for row in durations):
        raise ValueError("nap duration options cannot be empty")
    blocked = [interval(v, "unavailable") for v in data.get("unavailable", [])]
    fixed = [interval(v, "fixed_naps") for v in data.get("fixed_naps", [])]
    if any(a == b for a, b in blocked + fixed):
        raise ValueError("sleep and unavailable intervals must have positive duration")
    if any(a < now for a, _ in fixed):
        raise ValueError("fixed_naps must be future naps; finish an ongoing nap first")
    targets = data["targets"]
    bed_target = integer(targets["bedtime"], "bedtime target")
    nap_target = integer(targets["total_day_nap_minutes"], "nap total target")
    completed = integer(data.get("completed_nap_minutes", 0), "completed_nap_minutes")
    wake_targets = targets["wake_minutes"]
    if len(wake_targets) != len(wakes):
        raise ValueError("wake_minutes targets must match wake_ranges")
    wake_targets = [integer(v, "wake target", 1) for v in wake_targets]
    priorities = data["priority_order"]
    metrics = {"bedtime_deviation", "total_nap_deviation", "wake_deviation"}
    if not isinstance(priorities, list) or len(priorities) != 3 or set(priorities) != metrics:
        raise ValueError("priority_order must order each of the three supported metrics once")

    best, serial, states, feasible, truncated = [], 0, 0, 0, False

    def tick():
        nonlocal states, truncated
        if states >= limit:
            truncated = True
            return False
        states += 1
        return True

    def grid(low, high, extras=()):
        return sorted(set(range(low, high + 1, step)) |
                      {v for v in (high, *extras) if low <= v <= high})

    def search(end, naps, wake_values, count):
        nonlocal serial, feasible
        if not tick():
            return
        i = len(naps)
        lo, hi = wakes[i]
        if i == count:
            if not all(list(item) in naps for item in fixed):
                return
            low, high = max(now, end + lo, bed_low), min(end + hi, bed_high)
            for bed in grid(low, high, (bed_target,)):
                if not tick():
                    return
                values = wake_values + [bed - end]
                scores = {
                    "bedtime_deviation": abs(bed - bed_target),
                    "total_nap_deviation": abs(completed + sum(b - a for a, b in naps) - nap_target),
                    "wake_deviation": sum(abs(v - t) for v, t in zip(values, wake_targets)),
                }
                rank = tuple(scores[key] for key in priorities)
                plan = {"naps": naps, "bedtime": bed, "wake_minutes": values,
                        "total_day_nap_minutes": completed + sum(b - a for a, b in naps),
                        "deviations_minutes": scores}
                feasible += 1
                serial += 1
                item = (tuple(-v for v in rank), -serial, plan)
                if len(best) < 5:
                    heapq.heappush(best, item)
                elif item[:2] > best[0][:2]:
                    heapq.heapreplace(best, item)
            return
        low, high = max(now, end + lo), min(end + hi, bed_high)
        for start in grid(low, high, (a for a, _ in fixed)):
            for duration in durations[i]:
                if not tick():
                    return
                stop = start + duration
                if stop + wakes[i + 1][0] > bed_high:
                    continue
                if any(start < b and stop > a for a, b in blocked):
                    continue
                if any(start < b and stop > a and (start, stop) != (a, b) for a, b in fixed):
                    continue
                search(stop, naps + [[start, stop]], wake_values + [start - end], count)
                if truncated:
                    return

    for count in counts:
        search(last, [], [], count)
        if truncated:
            break
    ranked = sorted(best, key=lambda item: (tuple(-v for v in item[0]), -item[1]))
    return {
        "search_complete": not truncated,
        "states_examined": states,
        "feasible_grid_plans": feasible,
        "step_minutes": step,
        "priority_order": priorities,
        "plans": [item[2] for item in ranked],
        "interpretation": "Nap durations are scenario assumptions; these are sleep opportunities, not sleep predictions.",
        "result": "candidates_found" if best else ("search_incomplete" if truncated else "no_feasible_grid_plan"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="JSON request path, or - for stdin")
    args = parser.parse_args()
    try:
        if args.request == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.request, encoding="utf-8") as stream:
                data = json.load(stream)
        result = optimize(data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
