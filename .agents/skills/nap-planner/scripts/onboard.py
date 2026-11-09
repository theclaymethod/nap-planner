#!/usr/bin/env python3
"""Create a local child profile without replacing an existing profile."""

import argparse
from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from zoneinfo import ZoneInfo


def onboard(args):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.child):
        raise ValueError('child must be a lowercase identifier such as maya or child-1')
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    if args.age_months is not None:
        if args.as_of is None:
            raise ValueError('age-months requires its parent-supplied as-of date')
        if not math.isfinite(args.age_months) or args.age_months < 0:
            raise ValueError('age-months must be a nonnegative finite number')
    if args.birth_date and date.fromisoformat(args.birth_date) > as_of:
        raise ValueError('birth-date cannot be after the reference date')
    if args.timezone:
        ZoneInfo(args.timezone)
    if args.wake_minutes:
        low, high = args.wake_minutes
        if not 0 < low <= high <= 1440:
            raise ValueError('wake-minutes must be a positive ascending range in minutes')
        if args.as_of is None:
            raise ValueError('wake-minutes requires the report as-of date')
    folder = Path(args.data_root).expanduser().resolve() / args.child
    destination = folder / 'profile.json'
    if destination.exists():
        existing = json.loads(destination.read_text())
        if existing.get('child_id') != args.child:
            raise ValueError('existing profile has a different child_id; select the correct folder')
        return {'created': False, 'profile_path': str(destination), 'profile': existing}
    now = datetime.now(timezone.utc).isoformat()
    age = {'months':args.age_months,'as_of':as_of.isoformat(),'source':'parent'} if args.age_months is not None else None
    tolerance = []
    if args.wake_minutes:
        tolerance.append({'minutes':args.wake_minutes,'meaning':args.wake_meaning,'applies_to':args.applies_to,'reported_on':as_of.isoformat(),'statement':args.wake_statement or f'Parent reported {args.wake_minutes[0]}–{args.wake_minutes[1]} minutes awake.'})
    profile = {'schema_version':1,'child_id':args.child,'name':args.name,'birth_date':args.birth_date,'age_observation':age,'timezone':args.timezone,'reported':{'wake_tolerance':tolerance,'usual_nap_durations_minutes':[],'usual_nap_count':None,'bedtime':None,'care_instructions':[]},'preferences':{'priority_order':None,'flexibility':None},'estimates':[],'development_scenarios':[],'open_questions':[],'updated_at':now}
    if not args.birth_date and age is None:
        profile['open_questions'].append('Age with reference date, or optional birth date')
    if not args.timezone:
        profile['open_questions'].append('Local time zone')
    if tolerance and (args.wake_meaning=='unresolved' or args.applies_to=='unknown'):
        profile['open_questions'].append('Meaning and applicable positions of the reported wake tolerance')
    folder.mkdir(parents=True,exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w',dir=folder,delete=False,encoding='utf-8') as stream:
            temporary = Path(stream.name)
            json.dump(profile,stream,indent=2,ensure_ascii=False)
            stream.write('\n')
        # Link creates the destination atomically and cannot overwrite another creator.
        os.link(temporary,destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    entry = {'at':now,'reason':'Parent onboarding','fields':['profile'],'previous':None,'new':profile}
    with (folder/'changes.jsonl').open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(entry,ensure_ascii=False)+'\n')
    saved = json.loads(destination.read_text())
    return {'created':True,'profile_path':str(destination),'profile':saved}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',default='children')
    parser.add_argument('--child',required=True)
    parser.add_argument('--name')
    age = parser.add_mutually_exclusive_group()
    age.add_argument('--age-months',type=float)
    age.add_argument('--birth-date')
    parser.add_argument('--as-of')
    parser.add_argument('--timezone')
    parser.add_argument('--wake-minutes',nargs=2,type=int)
    parser.add_argument('--wake-meaning',choices=['unresolved','usual_range','upper_limit','preferred_range'],default='unresolved')
    parser.add_argument('--applies-to',default='unknown')
    parser.add_argument('--wake-statement')
    try:
        result = onboard(parser.parse_args())
    except (OSError,ValueError,KeyError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__':
    sys.exit(main())
