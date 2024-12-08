from flask import Blueprint, render_template, jsonify
from app.models import Station, StationStatus, InferenceRequest, PalletType
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db  # Use the current SQLAlchemy session

# Create a blueprint for frontend-specific routes
frontend = Blueprint("frontend", __name__)

def fetch_station_statuses():
    # Query all stations with their statuses
    stations = Station.query.options(joinedload(Station.station_status)).all()

    # Query additional data (e.g., total requests per station)
    request_counts = (
        db.session.query(InferenceRequest.station_id, func.count(InferenceRequest.request_id).label("total_requests"))
        .group_by(InferenceRequest.station_id)
        .all()
    )
    request_counts_dict = {station_id: total_requests for station_id, total_requests in request_counts}

    # Prepare station data with additional metrics
    return [
        {
            "station_name": station.station_name,
            "station_status": station.station_status.stationStatus_name,
            "status_class": (
                "text-success" if station.station_status.stationStatus_name == "Ready"
                else "text-warning" if station.station_status.stationStatus_name == "Processing"
                else "text-danger"
            ),
            "total_requests": request_counts_dict.get(station.station_id, 0),
        }
        for station in stations
    ]

def get_pallet_count():
    """
    Fetch pallet count data for the last 7 and 30 days
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    # Total counts for the last 7 and 30 days
    last_7_days = (
        db.session.query(InferenceRequest.pallet_type, func.count(InferenceRequest.request_id))
        .filter(InferenceRequest.request_creation >= seven_days_ago)
        .group_by(InferenceRequest.pallet_type)
        .all()
    )

    last_30_days = (
        db.session.query(InferenceRequest.pallet_type, func.count(InferenceRequest.request_id))
        .filter(InferenceRequest.request_creation >= thirty_days_ago)
        .group_by(InferenceRequest.pallet_type)
        .all()
    )

    # Convert to JSON-friendly format
    def format_data(data):
        formatted = []
        for pallet_type, count in data:
            pallet_type_name = (
                db.session.query(PalletType.type_name)
                .filter(PalletType.type_id == pallet_type)
                .scalar()
            )
            formatted.append({"pallet_type": pallet_type_name, "count": count})
        return formatted

    return jsonify({
        "last_7_days": format_data(last_7_days),
        "last_30_days": format_data(last_30_days),
    })


# Define frontend routes
@frontend.route("/manager_dashboard")
def manager_dashboard():
    # Fetch required data
    station_data = fetch_station_statuses()
    pallet_count_data = get_pallet_count()


    # Render the Manager Dashboard
    return render_template(
        "managerDashboard.html",
        stations=station_data,
        pallet_count_data=pallet_count_data.json
    )

@frontend.route("/station_dashboard/<int:station_id>")
def station_dashboard(station_id):
    """
    Renders the Station Dashboard for a specific station.
    """
    station = Station.query.get(station_id)
    if not station:
        return "Station not found", 404

    return render_template("stationDashboard.html", station=station)
