#!/usr/bin/env python3
"""Run development solver cases and independently check their finite-grid outcomes."""

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent
SOLVER = PROJECT / '.agents/skills/nap-planner/scripts/optimize.py'


def objective(request, naps, bed):
    wake = []
    previous = request['last_wake']
    for start, end in naps:
        wake.append(start - previous)
        previous = end
    wake.append(bed - previous)
    total = request.get('completed_nap_minutes', 0) + sum(b-a for a, b in naps)
    targets = request['targets']
    scores = {
        'bedtime_deviation': abs(bed-targets['bedtime']),
        'total_nap_deviation': abs(total-targets['total_day_nap_minutes']),
        'wake_deviation': sum(abs(x-y) for x, y in zip(wake, targets['wake_minutes'])),
    }
    return wake, total, scores


def oracle(request):
    """Minute-wise independent enumeration of the documented finite candidate set."""
    ranks = []
    step = request.get('step_minutes', 5)
    fixed = request.get('fixed_naps', [])
    unavailable = request.get('unavailable', [])
    earliest_bed, latest_bed = request['bedtime_range']

    def visit(naps, end, count):
        position = len(naps)
        minimum, maximum = request['wake_ranges'][position]
        if position == count:
            if any(pair not in naps for pair in fixed):
                return
            low, high = max(request['now'], end+minimum, earliest_bed), min(end+maximum, latest_bed)
            for bed in range(low, high+1):
                if (bed-low) % step and bed != high and bed != request['targets']['bedtime']:
                    continue
                scores = objective(request, naps, bed)[2]
                ranks.append(tuple(scores[k] for k in request['priority_order']))
            return
        low, high = max(request['now'], end+minimum), min(end+maximum, latest_bed)
        for start in range(low, high+1):
            if (start-low) % step and start != high and not any(start == a for a, _ in fixed):
                continue
            for duration in set(request['nap_duration_options'][position]):
                stop = start+duration
                if any(start < b and stop > a for a, b in unavailable):
                    continue
                if any(start < b and stop > a and [start, stop] != pair for pair in fixed for a, b in [pair]):
                    continue
                visit(naps+[[start, stop]], stop, count)

    for count in sorted(set(request['remaining_nap_counts'])):
        visit([], request['last_wake'], count)
    return sorted(ranks)


def grade(case, output, exit_code=0):
    """Grade untrusted candidate JSON; return observations, never execute candidate data."""
    findings = []
    if not isinstance(output, dict):
        return {'status':'FAIL','observations':['Output must be an object.']}
    if case['expected_kind'] == 'invalid':
        ok = exit_code != 0 and isinstance(output.get('error'), str) and bool(output['error']) and not output.get('plans')
        return {'status':'PASS' if ok else 'FAIL','observations':['Invalid-request error contract checked.']}
    if exit_code != 0:
        return {'status':'ERROR','observations':['Valid request failed to execute.']}
    request = case['input']
    try:
        if type(output['search_complete']) is not bool:
            raise ValueError('search_complete must be boolean')
        states, count = output['states_examined'], output['feasible_grid_plans']
        if type(states) is not int or not 1 <= states <= request.get('max_states',200000):
            raise ValueError('Examined-state count must be an integer within the search budget')
        if type(count) is not int or not 0 <= count <= states:
            raise ValueError('Feasible count cannot exceed examined states or be negative')
        plans = output['plans']
        if not isinstance(plans, list) or len(plans) > 5:
            raise ValueError('plans must be a list of at most five plans')
        if len(plans) > count:
            raise ValueError('Returned plan count exceeds feasible count')
        seen, reported_ranks = set(), []
        for plan in plans:
            naps, bed = plan['naps'], plan['bedtime']
            if type(bed) is not int or not request['bedtime_range'][0] <= bed <= request['bedtime_range'][1]:
                raise ValueError('Bedtime outside allowed bounds')
            if not isinstance(naps,list) or len(naps) not in request['remaining_nap_counts']:
                raise ValueError('Wrong remaining nap count')
            previous = request['last_wake']
            for i, pair in enumerate(naps):
                if not isinstance(pair,list) or len(pair)!=2 or any(type(v) is not int for v in pair):
                    raise ValueError('Malformed nap interval')
                start, stop = pair
                if start < request['now'] or stop-start not in request['nap_duration_options'][i]:
                    raise ValueError('Nap starts in past or uses an unsupported duration')
                lo, hi = request['wake_ranges'][i]
                if not lo <= start-previous <= hi:
                    raise ValueError('Wake interval outside bounds')
                grid_low = max(request['now'],previous+lo)
                grid_high = min(previous+hi,request['bedtime_range'][1])
                on_grid = (start-grid_low) % request.get('step_minutes',5) == 0
                fixed_start = any(start==a for a,_ in request.get('fixed_naps',[]))
                if not on_grid and start != grid_high and not fixed_start:
                    raise ValueError('Returned nap start is outside the declared finite grid')
                if any(start < b and stop > a for a,b in request.get('unavailable', [])):
                    raise ValueError('Nap overlaps unavailable period')
                previous = stop
            lo, hi = request['wake_ranges'][len(naps)]
            if bed < request['now'] or not lo <= bed-previous <= hi:
                raise ValueError('Before-bed wake interval outside bounds')
            grid_low = max(request['now'],previous+lo,request['bedtime_range'][0])
            grid_high = min(previous+hi,request['bedtime_range'][1])
            if (bed-grid_low) % request.get('step_minutes',5) and bed != grid_high and bed != request['targets']['bedtime']:
                raise ValueError('Returned bedtime is outside the declared finite grid')
            if any(pair not in naps for pair in request.get('fixed_naps', [])):
                raise ValueError('Fixed nap missing')
            wake, total, scores = objective(request,naps,bed)
            if plan['wake_minutes']!=wake or plan['total_day_nap_minutes']!=total or plan['deviations_minutes']!=scores:
                raise ValueError('Reported arithmetic does not match actual plan')
            signature = json.dumps([naps,bed])
            if signature in seen:
                raise ValueError('Duplicate returned plan')
            seen.add(signature)
            reported_ranks.append(tuple(scores[k] for k in request['priority_order']))
        if reported_ranks != sorted(reported_ranks):
            raise ValueError('Candidates are not ranked by declared priorities')
        if output['priority_order'] != request['priority_order']:
            raise ValueError('Priorities changed')
        if output['step_minutes'] != request.get('step_minutes',5):
            raise ValueError('Search grid changed')
        if output['search_complete']:
            ranks = oracle(request)
            if output['feasible_grid_plans'] != len(ranks):
                raise ValueError('Feasible count differs from independent enumeration')
            if reported_ranks != ranks[:5]:
                raise ValueError('Best candidate objectives differ from independent enumeration')
            expected = 'candidates_found' if ranks else 'no_feasible_grid_plan'
            if output['result'] != expected:
                raise ValueError('Result classification contradicts finite search')
            findings.append('Checked feasibility, arithmetic, ranking, and independent finite-grid enumeration.')
        else:
            if output['result'] != ('candidates_found' if plans else 'search_incomplete'):
                raise ValueError('Incomplete search falsely claims infeasibility')
            if case['id'] != 'search-budget':
                return {'status':'UNKNOWN','observations':['Incomplete search; no optimum or infeasibility credit.']}
            if output['states_examined'] != request['max_states']:
                raise ValueError('Truncated search does not report consumed budget')
            findings.append('Checked explicit search-budget exhaustion; no optimality credit.')
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        return {'status':'FAIL','observations':[str(exc)]}
    return {'status':'PASS','observations':findings}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    args = parser.parse_args()
    destination = Path(args.out)
    destination.mkdir(parents=True,exist_ok=False)
    cases = [json.loads(line) for line in (ROOT/'cases/solver.jsonl').read_text().splitlines()]
    results, traces = [], []
    for case in cases:
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        process = subprocess.run([sys.executable,str(SOLVER),'-'],input=json.dumps(case['input']),text=True,capture_output=True,timeout=30)
        raw = process.stderr if process.returncode else process.stdout
        try:
            output = json.loads(raw)
            result = grade(case,output,process.returncode)
        except (ValueError,TypeError) as exc:
            output = None
            result = {'status':'ERROR','observations':[str(exc)]}
        results.append({'id':case['id'],**result})
        traces.append({'id':case['id'],'input':case['input'],'output':output,'stdout':process.stdout,'stderr':process.stderr,'exit_code':process.returncode,'started_at':started,'execution_kind':'actual-solver-cli','input_origin':'synthetic'})
    (destination/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    (destination/'traces.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in traces))
    paths = [Path(__file__),SOLVER,ROOT/'rubric.md',ROOT/'cases/solver.jsonl',ROOT/'cases/agent.jsonl',PROJECT/'.agents/skills/nap-planner/SKILL.md']
    manifest = {'kind':'development','hashes':{str(path.relative_to(PROJECT)):digest(path) for path in paths},'host_boundary':'Shared local OS; no adversarial file isolation','cases':[case['id'] for case in cases]}
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'results':results,'out':str(destination)},indent=2))


if __name__ == '__main__':
    main()
