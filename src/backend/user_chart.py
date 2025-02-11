from collections import defaultdict
import datetime
from src.utils.data_base_util import DataBaseUtil


def get_all_registration_dates_from_db():
    """
    Retrieves all registration dates from the 'users' table in the database.

    Returns:
        List of dates (YYYY-MM-DD) representing when users registered.

    """
    db = DataBaseUtil()

    # Fetch all user records from the database
    rows = db.load_many("users")

    # Extract the 'registered_at' date (assuming it's stored at index 8)
    registration_dates = [row[8] for row in rows if row[8] is not None]

    return registration_dates


def get_all_registrations_per_week():

    """
    Groups user registrations by week and calculates a running total.

    Returns:
        A list of tuples where:
        - The first element is the week's starting date (Monday) as a string.
        - The second element is the total number of registered users up to that week.

    """
    registration_dates = get_all_registration_dates_from_db()

    # Dictionary to store user registrations per week (key = Monday of that week)
    weekly_counts = defaultdict(int)

    for reg_date in registration_dates:
        # Determine the Monday of the registration week
        monday = reg_date - datetime.timedelta(days=reg_date.weekday())

        # Count registrations per week
        weekly_counts[monday] += 1

    # Sort the weeks chronologically
    sorted_weeks = sorted(weekly_counts.items())

    total_users = 0  # Running total of registered users
    result = []

    for monday, count in sorted_weeks:
        total_users += count  # Add current week's registrations to the total

        # Append the week's Monday and the total number of users so far
        result.append((monday.strftime("%Y-%m-%d"), total_users))

    return result
