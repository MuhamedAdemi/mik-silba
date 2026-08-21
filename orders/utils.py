from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone

BUSINESS_DAY_CUTOFF_HOUR = getattr(settings, "BUSINESS_DAY_CUTOFF_HOUR", 7)


def business_date(dt=None):
    """Which 'business day' a moment belongs to.

    The bar's real day runs from BUSINESS_DAY_CUTOFF_HOUR (e.g. 7am) to the
    same time the next calendar day — it stays open past midnight. Without
    this, a sale at 01:00 would silently get counted as a *new* day instead
    of still belonging to the previous evening's shift, splitting one
    business day's takings across two calendar dates.
    """
    dt = timezone.localtime(dt) if dt else timezone.localtime()
    shifted = dt - timedelta(hours=BUSINESS_DAY_CUTOFF_HOUR)
    return shifted.date()


def business_day_bounds(business_date_value):
    """(start, end) aware datetimes spanning one business day: from
    BUSINESS_DAY_CUTOFF_HOUR on business_date_value to the same time the
    next calendar day."""
    naive_start = datetime.combine(business_date_value, time(hour=BUSINESS_DAY_CUTOFF_HOUR))
    start = timezone.make_aware(naive_start)
    end = start + timedelta(days=1)
    return start, end


def today_business_date():
    return business_date()
