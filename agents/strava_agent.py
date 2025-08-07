import time
from stravalib.client import Client
from pydantic_ai.agent import Agent, RunContext
from config.llm_config import gemini_model
from config.config import settings
from sqlalchemy import desc
from models import StravaToken
from config.database import get_db

def get_strava_token():
    """Reads token from the database."""
    db = next(get_db())
    token_info = db.query(StravaToken).order_by(desc(StravaToken.id)).first()
    if token_info:
        return {
            "access_token": token_info.access_token,
            "refresh_token": token_info.refresh_token,
            "expires_at": token_info.expires_at,
        }
    return None

def save_strava_token(token_info):
    """Saves token info to the database."""
    db = next(get_db())
    new_token = StravaToken(**token_info)
    db.add(new_token)
    db.commit()
    print("Successfully saved Strava token to the database.")

def get_strava_client():
    """Initializes and returns a Strava client, handling token refresh."""
    client = Client()
    token_info = get_strava_token()

    if not all([settings.STRAVA_CLIENT_ID, settings.STRAVA_CLIENT_SECRET]):
        raise ValueError(
            "Missing STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET in your settings. "
            "Cannot refresh token."
        )

    if time.time() > token_info.get("expires_at", 0):
        print("Strava access token has expired. Refreshing...")
        try:
            refresh_response = client.refresh_access_token(
                client_id=settings.STRAVA_CLIENT_ID,
                client_secret=settings.STRAVA_CLIENT_SECRET,
                refresh_token=token_info["refresh_token"],
            )
            save_strava_token(refresh_response)
            token_info = refresh_response
            print("Strava token refreshed successfully.")
        except Exception as e:
            print(f"Error refreshing Strava token: {e}")
            raise

    client.access_token = token_info["access_token"]
    client.refresh_token = token_info["refresh_token"]
    return client

def get_athlete_stats(run_context: RunContext) -> dict:
    """
    Fetches the activity stats for the authenticated athlete.

    Returns:
        A dictionary containing the athlete's stats.
    """
    client = get_strava_client()
    athlete = client.get_athlete()
    return athlete.stats.to_dict()

def get_latest_activities(run_context: RunContext, limit: int = 5) -> list[dict]:
    """
    Fetches the most recent activities for the authenticated user.

    Args:
        limit: The number of activities to fetch.

    Returns:
        A list of dictionaries, where each dictionary represents an activity.
    """
    client = get_strava_client()
    activities = client.get_activities(limit=limit)
    
    result_activities = []
    for activity in activities:
        result_activities.append({
            "id": activity.id,
            "name": activity.name,
            "distance": float(activity.distance) if activity.distance else None,
            "distance_unit": str(activity.distance.unit) if activity.distance else None,
            "moving_time": str(activity.moving_time) if activity.moving_time else None,
            "elapsed_time": str(activity.elapsed_time) if activity.elapsed_time else None,
            "type": activity.type,
            "start_date": str(activity.start_date),
            "average_speed": float(activity.average_speed) if activity.average_speed else None,
            "average_speed_unit": str(activity.average_speed.unit) if activity.average_speed else None,
            "max_speed": float(activity.max_speed) if activity.max_speed else None,
            "max_speed_unit": str(activity.max_speed.unit) if activity.max_speed else None,
            "total_elevation_gain": float(activity.total_elevation_gain) if activity.total_elevation_gain else None,
            "total_elevation_gain_unit": str(activity.total_elevation_gain.unit) if activity.total_elevation_gain else None,
        })
    return result_activities

def get_activity_details(run_context: RunContext, activity_id: int) -> dict:
    """
    Fetches detailed information for a specific activity by its ID.

    Args:
        activity_id: The ID of the activity to fetch.

    Returns:
        A dictionary containing the detailed activity information.
    """
    client = get_strava_client()
    activity = client.get_activity(activity_id)
    return {
        "id": activity.id,
        "name": activity.name,
        "description": activity.description,
        "distance": float(activity.distance) if activity.distance else None,
        "distance_unit": str(activity.distance.unit) if activity.distance else None,
        "moving_time": str(activity.moving_time) if activity.moving_time else None,
        "elapsed_time": str(activity.elapsed_time) if activity.elapsed_time else None,
        "type": activity.type,
        "start_date": str(activity.start_date),
        "average_speed": float(activity.average_speed) if activity.average_speed else None,
        "average_speed_unit": str(activity.average_speed.unit) if activity.average_speed else None,
        "max_speed": float(activity.max_speed) if activity.max_speed else None,
        "max_speed_unit": str(activity.max_speed.unit) if activity.max_speed else None,
        "total_elevation_gain": float(activity.total_elevation_gain) if activity.total_elevation_gain else None,
        "total_elevation_gain_unit": str(activity.total_elevation_gain.unit) if activity.total_elevation_gain else None,
        "calories": activity.calories,
        "average_heartrate": activity.average_heartrate,
        "max_heartrate": activity.max_heartrate,
    }

def get_athlete_profile(run_context: RunContext) -> dict:
    """
    Fetches the authenticated athlete's profile information.

    Returns:
        A dictionary containing the athlete's profile details.
    """
    client = get_strava_client()
    athlete = client.get_athlete()
    return {
        "id": athlete.id,
        "username": athlete.username,
        "firstname": athlete.firstname,
        "lastname": athlete.lastname,
        "city": athlete.city,
        "state": athlete.state,
        "country": athlete.country,
        "sex": athlete.sex,
        "premium": athlete.premium,
        "created_at": str(athlete.created_at),
        "updated_at": str(athlete.updated_at),
        "profile_medium": athlete.profile_medium,
        "profile": athlete.profile,
    }

from datetime import datetime, timedelta

def get_weekly_progress(run_context: RunContext) -> dict:
    """
    Summarizes the total running distance and time in the past 7 days.

    Returns:
        Dict with total distance, number of runs, and total time.
    """
    client = get_strava_client()
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    activities = client.get_activities(after=one_week_ago)

    total_distance = 0
    total_time = 0
    count = 0

    for activity in activities:
        if activity.type != "Run":
            continue
        count += 1
        total_distance += activity.distance.num
        total_time += activity.moving_time.total_seconds()

    return {
        "run_count": count,
        "total_distance_km": round(total_distance / 1000, 2),
        "total_time_min": round(total_time / 60, 1),
        "average_pace_min_per_km": round((total_time / (total_distance / 1000)) / 60, 2) if total_distance else None
    }

def get_activities_by_type(run_context: RunContext, activity_type: str, limit: int = 10) -> list[dict]:
    """
    Get a list of recent Strava activities of a specific type (e.g., Run, Ride, Swim).

    Parameters:
    - activity_type (str): The type of activity to filter (e.g., "Run").
    - limit (int): Number of recent activities to return (default is 10).

    Returns:
    - A list of activity summaries including ID, name, distance (in km), time, and start date.
    """
    client = get_strava_client()
    activities = client.get_activities(limit=limit)
    return [
        {
            "id": a.id,
            "name": a.name,
            "distance_km": round(a.distance.num / 1000, 2),
            "moving_time_min": round(float(a.moving_time) / 60, 2),
            "start_date": str(a.start_date)
        }
        for a in activities if str(a.type).lower() == activity_type.lower()
    ]


def get_best_efforts(run_context: RunContext, activity_id: int) -> dict:
    """
    Retrieve the best effort segments (e.g., fastest 1k, 5k) for a given activity.

    Parameters:
    - activity_id (int): The Strava activity ID to fetch best efforts from.

    Returns:
    - A dictionary with a list of best effort segment names, distances, and times.
    """
    client = get_strava_client()    
    activity = client.get_activity(activity_id, include_all_efforts=True)
    return {
        "activity_id": activity.id,
        "best_efforts": [
            {
                "name": effort.name,
                "distance_m": effort.distance.num,
                "elapsed_time_sec": float(effort.elapsed_time)
            } for effort in activity.best_efforts
        ]
    }


def get_activity_gps_coords(run_context: RunContext, activity_id: int) -> dict:
    """
    Get GPS coordinates (lat/lng) for a specific activity for mapping or visualization.

    Parameters:
    - activity_id (int): The Strava activity ID.

    Returns:
    - A dictionary containing GPS coordinates as a list of [lat, lng] pairs.
    """
    client = get_strava_client()
    streams = client.get_activity_streams(activity_id, types=["latlng"])
    if 'latlng' in streams:
        return {
            "activity_id": activity_id,
            "gps_coordinates": streams['latlng'].data
        }
    return {"error": "No GPS data found for this activity."}


def get_longest_run(run_context: RunContext) -> dict:
    """
    Finds the athlete’s longest run ever recorded.

    Returns:
        Dict with name, distance, pace, time, date
    """
    client = get_strava_client()
    activities = client.get_activities()
    longest = max(
        (a for a in activities if a.type == "Run"),
        key=lambda a: a.distance.num,
        default=None
    )
    if not longest:
        return {"message": "No run data found"}

    return {
        "name": longest.name,
        "distance_km": round(longest.distance.num / 1000, 2),
        "pace_min_per_km": round(longest.moving_time.total_seconds() / (longest.distance.num / 1000) / 60, 2),
        "moving_time_min": round(longest.moving_time.total_seconds() / 60, 2),
        "date": longest.start_date_local.strftime("%Y-%m-%d")
    }


def get_race_performances(run_context: RunContext, keyword: str = "race", limit: int = 50) -> list[dict]:
    """
    Retrieve recent race-type activities (e.g., official races or time trials).

    Parameters:
    - keyword (str): A keyword to identify races (default is "race").
    - limit (int): Number of recent activities to search (default is 50).

    Returns:
    - A list of race activities with name, distance, time, and start date.
    """
    client = get_strava_client()
    races = [
        {
            "id": a.id,
            "name": a.name,
            "distance_km": round(a.distance.num / 1000, 2),
            "moving_time_min": round(float(a.moving_time) / 60, 2),
            "start_date": str(a.start_date)
        }
        for a in client.get_activities(limit=limit)
        if keyword.lower() in a.name.lower()
    ]
    return races


def compare_activities(run_context: RunContext, activity_id_1: int, activity_id_2: int) -> dict:
    """
    Compare two activities in terms of distance, speed, and elevation gain.

    Parameters:
    - activity_id_1 (int): The ID of the first activity.
    - activity_id_2 (int): The ID of the second activity.

    Returns:
    - A dictionary showing the key metrics and their differences between the two activities.
    """
    client = get_strava_client()
    a1 = client.get_activity(activity_id_1)
    a2 = client.get_activity(activity_id_2)

    return {
        "activity_1": {
            "name": a1.name,
            "distance_km": round(a1.distance.num / 1000, 2),
            "moving_time_min": round(float(a1.moving_time) / 60, 2),
            "elevation_gain_m": a1.total_elevation_gain.num
        },
        "activity_2": {
            "name": a2.name,
            "distance_km": round(a2.distance.num / 1000, 2),
            "moving_time_min": round(float(a2.moving_time) / 60, 2),
            "elevation_gain_m": a2.total_elevation_gain.num
        },
        "differences": {
            "distance_km": round((a1.distance.num - a2.distance.num) / 1000, 2),
            "time_min": round((float(a1.moving_time) - float(a2.moving_time)) / 60, 2),
            "elevation_m": round(a1.total_elevation_gain.num - a2.total_elevation_gain.num, 2)
        }
    }
    
def find_personal_records(run_context: RunContext) -> dict:
    """
    Finds personal records such as longest run, fastest pace, and max elevation gain.

    Returns:
    - A dictionary with distance, pace, and elevation personal bests.
    """
    client = get_strava_client()
    activities = client.get_activities()

    longest = None
    fastest = None
    max_elev = None

    for act in activities:
        if str(act.type).lower() != "run":
            continue
        if not longest or act.distance > longest.distance:
            longest = act
        pace = float(act.moving_time) / (float(act.distance) / 1000)
        if not fastest or pace < fastest["pace"]:
            fastest = {"activity": act, "pace": pace}
        if not max_elev or act.total_elevation_gain > max_elev.total_elevation_gain:
            max_elev = act

    return {
        "longest_run_km": round(longest.distance.num / 1000, 2),
        "fastest_pace_min_per_km": round(fastest["pace"] / 60, 2),
        "highest_elevation_gain_m": round(max_elev.total_elevation_gain.num, 1)
    }

def get_rolled_up_stats(run_context: RunContext) -> dict:
    """
    Retrieves rolled-up running statistics for the authenticated Strava athlete.

    This tool provides high-level summary statistics across different timeframes:
    - Recent totals (last 4 weeks)
    - Year-to-date totals (YTD)
    - All-time totals

    Each section includes:
    - Total number of runs
    - Total distance (in kilometers)
    - Total elevation gain (in meters, where available)

    This is useful for tracking progress over time, generating training insights,
    and comparing short-term vs long-term performance trends.

    Returns:
        A dictionary structured as:
        {
            "recent_run_totals": {
                "count": int,
                "distance_km": float,
                "elevation_gain_m": float
            },
            "ytd_run_totals": {
                "count": int,
                "distance_km": float
            },
            "all_run_totals": {
                "count": int,
                "distance_km": float
            }
        }
    """
    client = get_strava_client()
    athlete = client.get_athlete()
    stats = client.get_athlete_stats(athlete.id)

    return {
        "recent_run_totals": {
            "count": stats.recent_run_totals.count,
            "distance_km": round(stats.recent_run_totals.distance / 1000, 2),
            "elevation_gain_m": stats.recent_run_totals.elevation_gain
        },
        "ytd_run_totals": {
            "count": stats.ytd_run_totals.count,
            "distance_km": round(stats.ytd_run_totals.distance / 1000, 2)
        },
        "all_run_totals": {
            "count": stats.all_run_totals.count,
            "distance_km": round(stats.all_run_totals.distance / 1000, 2)
        }
    }
    
def get_fastest_run_over_distance(run_context: RunContext, min_distance_km: float = 5.0) -> dict:
    """
    Returns the fastest average pace run above a minimum distance.

    Args:
        min_distance_km: Minimum run distance to consider.

    Returns:
        Dict with fastest run info.
    """
    client = get_strava_client()
    activities = client.get_activities(per_page=100)
    qualified = [
        a for a in activities
        if a.type == "Run" and (a.distance.num / 1000) >= min_distance_km
    ]

    if not qualified:
        return {"message": f"No runs longer than {min_distance_km}km found."}

    fastest = min(
        qualified,
        key=lambda a: a.moving_time.total_seconds() / a.distance.num
    )

    pace = fastest.moving_time.total_seconds() / (fastest.distance.num / 1000)
    return {
        "name": fastest.name,
        "distance_km": round(fastest.distance.num / 1000, 2),
        "average_pace_min_per_km": round(pace / 60, 2),
        "date": fastest.start_date_local.strftime("%Y-%m-%d")
    }

strava_coach = Agent(
    model=gemini_model,
    tools=[
        get_athlete_stats,
        get_latest_activities,
        get_activity_details,
        get_athlete_profile,
        get_weekly_progress,
        find_personal_records,
        get_activities_by_type,
        get_best_efforts,
        get_activity_gps_coords,
        compare_activities,
        get_longest_run,
        get_race_performances,
        get_rolled_up_stats,
        get_fastest_run_over_distance
    ],
    system_prompt="""
        You are the StravaCoach, a friendly and motivational AI assistant specializing in running and fitness data.
        You have access to the user's Strava history and can retrieve information about their runs, including distance, time, pace, personal records, and recent activities.
        When a user asks for data, provide it in a clear, encouraging, and helpful manner.
    """
)