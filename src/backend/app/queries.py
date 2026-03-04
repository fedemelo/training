from sqlmodel import text

from app.core.db import engine

_TRIATHLON_SPORTS = "('running', 'cycling', 'swimming')"


def _query(sql):
    with engine.connect() as conn:
        return [dict(row._mapping) for row in conn.execute(text(sql))]


def history_summary():
    return _query(f"""
        SELECT sport,
               COUNT(*)                                              AS sessions,
               ROUND(SUM(total_distance) / 1000.0)::int             AS total_km,
               ROUND((SUM(total_timer_time) / 3600.0)::numeric, 1)  AS total_hours
        FROM session
        WHERE sport IN {_TRIATHLON_SPORTS}
        GROUP BY sport
        ORDER BY total_hours DESC
    """)


def weekly_breakdown(resting_hr, max_hr):
    rows = _query(f"""
        SELECT DATE_TRUNC('week', start_time)::date                  AS week_start,
               sport,
               COUNT(*)                                              AS sessions,
               ROUND((SUM(total_distance) / 1000.0)::numeric, 1)    AS km,
               ROUND(SUM(total_timer_time) / 60.0)::int             AS minutes,
               ROUND(AVG(avg_heart_rate))::int                      AS avg_hr
        FROM session
        WHERE start_time >= NOW() - INTERVAL '28 days'
          AND avg_heart_rate IS NOT NULL
          AND sport IN {_TRIATHLON_SPORTS}
        GROUP BY week_start, sport
        ORDER BY week_start, sport
    """)
    hr_range = max_hr - resting_hr
    return [
        {**r, "load": round(r["minutes"] * (r["avg_hr"] - resting_hr) / hr_range)}
        for r in rows
    ]


def current_week():
    return _query(f"""
        SELECT sport,
               sub_sport,
               start_time::date                                      AS date,
               ROUND((total_distance / 1000.0)::numeric, 1)         AS km,
               ROUND(total_timer_time / 60.0)::int                  AS minutes,
               avg_heart_rate                                        AS avg_hr
        FROM session
        WHERE start_time >= DATE_TRUNC('week', NOW())
          AND sport IN {_TRIATHLON_SPORTS}
        ORDER BY start_time
    """)
