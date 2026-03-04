import sys
import uuid
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitdecode
from app.core.db import create_tables, engine
from app.models import (
    Activity,
    DeveloperDataId,
    DeviceInfo,
    Event,
    FileId,
    FitFile,
    Lap,
    Record,
)
from app.models.session import Session as TrainingSession
from more_itertools import consume
from sqlmodel import Session as DBSession
from sqlmodel import select

_RAW_EXPORTS = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw-exports"

_FILE_ID_FIELDS = frozenset(
    {"type", "manufacturer", "product", "time_created", "product_name"}
)
_DEVELOPER_DATA_ID_FIELDS = frozenset(
    {"application_id", "manufacturer_id", "developer_data_index"}
)
_DEVICE_INFO_FIELDS = frozenset({"timestamp", "manufacturer", "product_name"})
_ACTIVITY_FIELDS = frozenset(
    {
        "timestamp",
        "total_timer_time",
        "num_sessions",
        "type",
        "event",
        "event_type",
        "local_timestamp",
    }
)
_EVENT_FIELDS = frozenset({"timestamp", "event", "event_type", "event_group"})
_RECORD_FIELDS = frozenset(
    {
        "timestamp",
        "position_lat",
        "position_long",
        "heart_rate",
        "distance",
        "activity_type",
        "enhanced_speed",
        "enhanced_altitude",
    }
)
_LAP_FIELDS = frozenset(
    {
        "timestamp",
        "message_index",
        "start_time",
        "total_elapsed_time",
        "total_timer_time",
        "total_distance",
        "total_calories",
        "avg_heart_rate",
        "max_heart_rate",
        "avg_cadence",
        "avg_power",
        "max_power",
        "total_ascent",
        "total_descent",
        "sport",
        "normalized_power",
        "sub_sport",
        "total_work",
        "avg_temperature",
        "min_heart_rate",
        "enhanced_avg_speed",
        "enhanced_max_speed",
    }
)
_SESSION_FIELDS = frozenset(
    {
        "timestamp",
        "start_time",
        "sport",
        "sub_sport",
        "total_elapsed_time",
        "total_timer_time",
        "total_distance",
        "total_calories",
        "avg_heart_rate",
        "max_heart_rate",
        "avg_cadence",
        "max_cadence",
        "avg_power",
        "max_power",
        "total_ascent",
        "total_descent",
        "normalized_power",
        "total_work",
        "avg_temperature",
        "min_heart_rate",
        "enhanced_avg_speed",
        "enhanced_max_speed",
    }
)

# Standard FIT activity_type enum + COROS-specific numeric extensions that fitdecode
# cannot resolve to strings because they are not in the standard profile.
_SPORT_MAP = {
    "running": "running",
    "cycling": "cycling",
    "swimming": "swimming",
    "walking": "walking",
    "training": "training",
    "e_biking": "cycling",
    "sedentary": None,  # daily activity tracking — not a workout
    "1": "running",
    "2": "cycling",
    "5": "swimming",
    "10": "training",
    "11": "walking",
    "17": "cycling",  # e_biking
}


def extract_fields(frame, known_fields):
    return {
        field.name: field.value
        for field in frame.fields
        if field.name in known_fields and field.value is not None
    }


def bytes_to_uuid_str(value):
    if value is None:
        return None
    return str(uuid.UUID(bytes=bytes(value)))


def group_messages(path):
    grouped = defaultdict(list)
    with fitdecode.FitReader(path) as reader:
        consume(
            grouped[frame.name].append(frame)
            for frame in reader
            if isinstance(frame, fitdecode.FitDataMessage)
        )
    return grouped


def _has_required(fields, required):
    return required.issubset(fields.keys())


def _detect_sport(record_frames):
    counts = Counter(
        extract_fields(f, {"activity_type"}).get("activity_type") for f in record_frames
    )
    counts.pop(None, None)
    if not counts:
        return "generic"
    return _SPORT_MAP.get(str(counts.most_common(1)[0][0]), "generic")


def build_file_ids(frames, fit_file_id):
    _required = {"type", "manufacturer", "product", "time_created", "product_name"}
    return [
        FileId(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(fields := extract_fields(frame, _FILE_ID_FIELDS), _required)
    ]


def build_developer_data_ids(frames, fit_file_id):
    _required = {"application_id", "manufacturer_id", "developer_data_index"}

    def normalize(fields):
        return {
            **fields,
            **(
                {"application_id": bytes_to_uuid_str(fields["application_id"])}
                if "application_id" in fields
                else {}
            ),
            **(
                {"manufacturer_id": str(fields["manufacturer_id"])}
                if "manufacturer_id" in fields
                else {}
            ),
        }

    return [
        DeveloperDataId(fit_file_id=fit_file_id, **normalize(fields))
        for frame in frames
        if _has_required(
            fields := extract_fields(frame, _DEVELOPER_DATA_ID_FIELDS), _required
        )
    ]


def build_device_infos(frames, fit_file_id):
    _required = {"timestamp", "manufacturer", "product_name"}
    return [
        DeviceInfo(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(
            fields := extract_fields(frame, _DEVICE_INFO_FIELDS), _required
        )
    ]


def build_activities(frames, fit_file_id):
    _required = {
        "timestamp",
        "total_timer_time",
        "num_sessions",
        "type",
        "event",
        "event_type",
        "local_timestamp",
    }
    return [
        Activity(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(fields := extract_fields(frame, _ACTIVITY_FIELDS), _required)
    ]


def build_events(frames, fit_file_id):
    _required = {"timestamp", "event", "event_type", "event_group"}
    return [
        Event(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(fields := extract_fields(frame, _EVENT_FIELDS), _required)
    ]


def build_records(frames, fit_file_id):
    return [
        Record(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(fields := extract_fields(frame, _RECORD_FIELDS), {"timestamp"})
    ]


def build_laps(frames, fit_file_id):
    _required = {
        "timestamp",
        "message_index",
        "start_time",
        "total_elapsed_time",
        "total_timer_time",
        "total_distance",
        "total_calories",
        "sport",
        "sub_sport",
    }
    return [
        Lap(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(fields := extract_fields(frame, _LAP_FIELDS), _required)
    ]


def build_sessions(frames, fit_file_id):
    _required = {
        "timestamp",
        "start_time",
        "sport",
        "sub_sport",
        "total_elapsed_time",
        "total_timer_time",
        "total_distance",
        "total_calories",
    }
    return [
        TrainingSession(fit_file_id=fit_file_id, **fields)
        for frame in frames
        if _has_required(fields := extract_fields(frame, _SESSION_FIELDS), _required)
    ]


def build_synthetic_session(grouped, fit_file_id):
    record_frames = grouped.get("record", [])
    if not record_frames:
        return None

    sport = _detect_sport(record_frames)
    if sport is None:
        return None

    records = [extract_fields(f, _RECORD_FIELDS) for f in record_frames]

    timestamps = [r["timestamp"] for r in records if "timestamp" in r]
    if not timestamps:
        return None

    start_time = min(timestamps)
    timestamp = max(timestamps)
    elapsed = (timestamp - start_time).total_seconds()

    activity_frames = grouped.get("activity", [])
    activity_data = (
        extract_fields(activity_frames[0], _ACTIVITY_FIELDS) if activity_frames else {}
    )

    distances = [r["distance"] for r in records if r.get("distance") is not None]
    hrs = [r["heart_rate"] for r in records if r.get("heart_rate") is not None]
    speeds = [
        r["enhanced_speed"] for r in records if r.get("enhanced_speed") is not None
    ]
    lap_data = [extract_fields(f, _LAP_FIELDS) for f in grouped.get("lap", [])]

    return TrainingSession(
        fit_file_id=fit_file_id,
        timestamp=timestamp,
        start_time=start_time,
        sport=sport,
        sub_sport="generic",
        total_elapsed_time=elapsed,
        total_timer_time=activity_data.get("total_timer_time", elapsed),
        total_distance=max(distances) if distances else 0.0,
        total_calories=sum(lap.get("total_calories", 0) for lap in lap_data),
        avg_heart_rate=round(sum(hrs) / len(hrs)) if hrs else None,
        max_heart_rate=max(hrs) if hrs else None,
        min_heart_rate=min(hrs) if hrs else None,
        enhanced_avg_speed=(sum(speeds) / len(speeds)) if speeds else None,
        enhanced_max_speed=max(speeds) if speeds else None,
    )


def persist_file(path, eng):
    name = path.name
    with DBSession(eng) as db:
        if db.exec(select(FitFile).where(FitFile.filename == name)).first():
            return
        try:
            grouped = group_messages(path)
        except fitdecode.FitHeaderError:
            return

        fit_file = FitFile(filename=name)
        db.add(fit_file)
        db.flush()

        explicit_sessions = build_sessions(grouped.get("session", []), fit_file.id)
        sessions = explicit_sessions or [
            s for s in [build_synthetic_session(grouped, fit_file.id)] if s is not None
        ]

        db.add_all(
            [
                *build_file_ids(grouped.get("file_id", []), fit_file.id),
                *build_developer_data_ids(
                    grouped.get("developer_data_id", []), fit_file.id
                ),
                *build_device_infos(grouped.get("device_info", []), fit_file.id),
                *build_activities(grouped.get("activity", []), fit_file.id),
                *build_events(grouped.get("event", []), fit_file.id),
                *build_records(grouped.get("record", []), fit_file.id),
                *build_laps(grouped.get("lap", []), fit_file.id),
                *sessions,
            ]
        )
        db.commit()


def main():
    create_tables()
    consume(persist_file(path, engine) for path in _RAW_EXPORTS.glob("*.fit"))


if __name__ == "__main__":
    main()
