# Using static methods instead of normal methods seems to break feed functionality
# pylint: disable=no-self-use
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from ws.models import Trip
from ws.utils.dates import local_date

DEFAULT_TIMEZONE = timezone.get_default_timezone()  # (US/Eastern)


class UpcomingTripsFeed(Feed):
    title = "MITOC Trips"
    link = reverse_lazy("upcoming_trips")
    description = "Upcoming trips by the MIT Outing Club"

    def items(self):
        upcoming_trips = Trip.objects.filter(trip_date__gte=local_date())
        return upcoming_trips.order_by('-trip_date')

    def item_title(self, trip):
        return trip.name

    def item_description(self, trip):
        return trip.description

    def item_link(self, trip):
        return reverse('view_trip', args=[trip.pk])

    def item_pubdate(self, trip):
        return trip.time_created.astimezone(DEFAULT_TIMEZONE)

    def item_author_name(self, trip):
        return trip.creator.name

    def item_updateddate(self, trip):
        return trip.last_edited.astimezone(DEFAULT_TIMEZONE)
