import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from app.queries import current_week, history_summary, weekly_breakdown

_CONTEXT = Path(__file__).resolve().parent.parent.parent.parent / "context"
_TODAY = date.today()
_WEEK_START = _TODAY - timedelta(days=_TODAY.weekday())
_WEEK_END = _WEEK_START + timedelta(days=6)


def _load(filename):
    return yaml.safe_load((_CONTEXT / filename).read_text())


def _weeks_to_go(race_date):
    return max(0, (date.fromisoformat(str(race_date)) - _TODAY).days // 7)


def _fmt_history(rows):
    return "\n".join(
        f"  {r['sport']:<10} {r['sessions']:>3} sessions   {r['total_km']:>5} km   {r['total_hours']:>5} h"
        for r in rows
    )


def _fmt_weekly(rows, resting_hr, max_hr):
    header = f"  (load = minutes × HR-reserve fraction, resting {resting_hr} / max {max_hr} bpm)"
    lines = [
        f"  {r['week_start']}  {r['sport']:<10}  {r['sessions']} sess  "
        f"{r['km']:>5} km  {r['minutes']:>4} min  avg HR {r['avg_hr']}  load {r['load']}"
        for r in rows
    ]
    return header + "\n" + ("\n".join(lines) if lines else "  (no data)")


def _fmt_current_week(rows):
    return (
        "\n".join(
            f"  {r['date']}  {r['sport']:<10}"
            + (f" ({r['sub_sport']})" if r["sub_sport"] else "")
            + f"  {r['km']:>5} km  {r['minutes']:>4} min  avg HR {r['avg_hr']}"
            for r in rows
        )
        or "  (no sessions yet this week)"
    )


def _fmt_race(r):
    legs = (
        f"\n    legs assigned: {', '.join(r['legs_assigned'])}"
        if "legs_assigned" in r
        else ""
    )
    swim = r["distance_km"].get("swim") or "—"
    bike = r["distance_km"].get("bike") or "—"
    run = r["distance_km"].get("run") or "—"
    terrain = r["terrain"]
    return (
        f"  {r['name']}  —  {r['date']}  ({_weeks_to_go(r['date'])} weeks away){legs}\n"
        f"    swim {swim} km  /  bike {bike} km  /  run {run} km\n"
        f"    terrain: swim={terrain['swim']}  bike={terrain['bike']}  run={terrain['run']}\n"
        f"    conditions: {r['air_temp_range_c'][0]}–{r['air_temp_range_c'][1]} °C air"
        + (f",  {r['avg_water_temp_c']} °C water" if r.get("avg_water_temp_c") else "")
        + f"  |  goal: {r['goal_type']}"
    )


def build_prompt():
    profile = _load("athlete_profile.yaml")
    running = _load("running.yaml")
    swimming = _load("swimming.yaml")
    cycling = _load("cycling.yaml")
    sleep = _load("sleep.yaml")
    availability = _load("training_availability.yaml")
    races = _load("races.yaml")["races"]

    resting_hr = profile["resting_hr"]
    max_hr = profile["max_hr"]

    next_race = min(races, key=lambda r: date.fromisoformat(str(r["date"])))
    next_race_weeks = _weeks_to_go(next_race["date"])

    run_z = running["hr_zones_bpm"]
    run_p = running["pace_zones_min_per_km"]
    swim_z = swimming["pace_zones_per_100m"]
    cycling_thr = (
        cycling["cycling_threshold_hr"] or "not yet tested — use running zones as proxy"
    )

    history = _fmt_history(history_summary())
    weekly = _fmt_weekly(weekly_breakdown(resting_hr, max_hr), resting_hr, max_hr)
    current = _fmt_current_week(current_week())
    race_lines = "\n\n".join(_fmt_race(r) for r in races)

    return f"""\
You are an expert triathlon coach. Plan the training week below for this athlete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATHLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:        {profile['name']}
Age:         {profile['age']}  |  Weight: {profile['weight_kg']} kg  |  Height: {profile['height_cm']} cm
VO2max:      {profile['vo2max']}
Resting HR:  {resting_hr} bpm  |  Max HR: {max_hr} bpm
HRV baseline: {sleep['baseline_overnight_hrv_ms']} ms
Injuries:    {profile['current_injuries']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RACE CALENDAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{race_lines}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRAINING ZONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RUNNING  (snapshot: {running['fitness_snapshot_period']})
  LTHR: {running['lactate_threshold_hr']} bpm  |  LT pace: {running['lactate_threshold_pace_min_per_km']} min/km
  HR zones:
    Z1 recovery:  ≤ {run_z['z1_recovery']['max']} bpm
    Z2 endurance: {run_z['z2_endurance']['min']}–{run_z['z2_endurance']['max']} bpm
    Z3 tempo:     {run_z['z3_tempo']['min']}–{run_z['z3_tempo']['max']} bpm
    Z4 threshold: {run_z['z4_threshold']['min']}–{run_z['z4_threshold']['max']} bpm
    Z5 max:       {run_z['z5_max']['min']}+ bpm
  Pace zones (min/km):
    Endurance:  {run_p['endurance']['min']}–{run_p['endurance']['max']}
    Threshold:  {run_p['threshold']['min']}–{run_p['threshold']['max']}
    Speed:      {run_p['speed']['min']}–{run_p['speed']['max']}
    Sprint:     < {run_p['sprint']['faster_than']}

SWIMMING
  Pace zones (/100 m):
    Easy aerobic:  {swim_z['easy_aerobic']['min']}–{swim_z['easy_aerobic']['max']}
    CSS:           {swim_z['css']['min']}–{swim_z['css']['max']}
    VO2 intervals: {swim_z['vo2_intervals']['min']}–{swim_z['vo2_intervals']['max']}
    Sprint:        {swim_z['sprint']['min']}–{swim_z['sprint']['max']}

CYCLING
  No power meter — train by HR.
  Threshold HR: {cycling_thr}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRAINING HISTORY — ALL TIME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{history}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAST 4 WEEKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{weekly}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THIS WEEK SO FAR  ({_WEEK_START} – {_TODAY})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{current}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVAILABILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wednesday:             swim only (afternoon, 1 h)
Friday:                swim (afternoon, 1–2 h)
Weekends:              long sessions available (4 h+ morning; up to 3 h evening if needed)
Mon / Tue / Thu / Fri: run or bike available (afternoon, up to 3 h)
Note: {availability['notes']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Next race: {next_race['name']}  on  {next_race['date']}  —  {next_race_weeks} weeks away.

Produce a day-by-day training plan for the week of {_WEEK_START} – {_WEEK_END}.
For each session specify:
  - Sport and session type (e.g. Z2 endurance run, CSS swim set, tempo bike)
  - Duration and target distance
  - Target zone with specific HR or pace numbers from the zones above
  - Brief coaching note (purpose, key execution cues)

Consider:
  - Periodization phase appropriate for {next_race_weeks} weeks out
  - Current load trend and recovery (HRV baseline {sleep['baseline_overnight_hrv_ms']} ms)
  - Athlete does swim + run legs at Barranquilla relay; all three disciplines at 5150 and IM 70.3
  - No injuries or constraints
"""


def main():
    print(build_prompt())


if __name__ == "__main__":
    main()
