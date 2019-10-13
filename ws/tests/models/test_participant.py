import datetime
from datetime import date

from freezegun import freeze_time

import ws.utils.dates as dateutils
from ws import models
from ws.tests import TestCase, factories


class ProblemsWithProfile(TestCase):
    # NOTE: These require TestCase since we do actual db lookups based on the record
    def test_our_factory_is_okay(self):
        """ The participant factory that we use is expected to have no problems. """
        participant = factories.ParticipantFactory.create()
        self.assertFalse(participant.problems_with_profile)

    def test_no_cell_phone_on_emergency_contact(self):
        participant = factories.ParticipantFactory.create()
        e_contact = factories.EmergencyContactFactory.create(cell_phone='')
        participant.emergency_info.emergency_contact = e_contact
        participant.save()

        self.assertEqual(
            participant.problems_with_profile,
            ["Please supply a valid number for your emergency contact."],
        )

    def test_full_name_required(self):
        participant = factories.ParticipantFactory.create(name='Cher')
        self.assertEqual(
            participant.problems_with_profile, ["Please supply your full legal name."]
        )

    def test_verified_email_required(self):
        participant = factories.ParticipantFactory.create()

        # Directly assign the participant an invalid email
        # (this should never happen, since we enforce that addresses come from user.emailaddress_set)
        participant.email = 'not-verified@example.com'

        self.assertEqual(
            participant.problems_with_profile,
            [
                'Please <a href="/accounts/email/">verify that you own not-verified@example.com</a>, '
                'or set your email address to one of your verified addresses.'
            ],
        )

    def test_xss_on_email_prevented(self):
        """ Returned strings can be trusted as HTML. """
        participant = factories.ParticipantFactory.create(
            email="</a><script>alert('hax')</script>@hacks.tld"
        )

        participant.user.emailaddress_set.update(verified=False)
        self.assertEqual(
            participant.user.emailaddress_set.get().email,  # (our factory assigns only one email)
            "</a><script>alert('hax')</script>@hacks.tld",
        )

        self.assertEqual(
            participant.problems_with_profile,
            [
                'Please <a href="/accounts/email/">verify that you own '
                # Note the HTML escaping!
                '&lt;/a&gt;&lt;script&gt;alert(&#39;hax&#39;)&lt;/script&gt;@hacks.tld</a>, '
                'or set your email address to one of your verified addresses.'
            ],
        )

    def test_old_student_affiliation_dated(self):
        student = factories.ParticipantFactory.create(affiliation='S')  # MIT or not?

        self.assertEqual(
            student.problems_with_profile, ["Please update your MIT affiliation."]
        )

    def test_not_updated_since_affiliation_overhaul(self):
        """ Any participant with affiliation predating our new categories should re-submit! """
        # This is right before the time when we released new categories!
        before_cutoff = dateutils.localize(datetime.datetime(2018, 10, 27, 3, 15))

        # Override the default "now" timestamp, to make participant's last profile update look old
        participant = factories.ParticipantFactory.create()
        participant.profile_last_updated = before_cutoff
        participant.save()

        self.assertEqual(
            participant.problems_with_profile, ["Please update your MIT affiliation."]
        )


class LeaderTest(TestCase):
    def test_name_with_rating_no_rating(self):
        """ Participants who aren't actively leaders just return their name. """
        trip = factories.TripFactory.create()
        participant = factories.ParticipantFactory.create(name='Tommy Caldwell')
        self.assertEqual('Tommy Caldwell', participant.name_with_rating(trip))

    def test_past_rating(self):
        """ We will display a past rating that was applicable at the time! """
        alex = factories.ParticipantFactory.create(name='Alex Honnold')

        # Make an older rating to show this isn't used
        with freeze_time("2018-11-10 12:25:00 EST"):
            rating = factories.LeaderRatingFactory.create(
                participant=alex,
                activity=models.BaseRating.WINTER_SCHOOL,
                rating='co-leader',
                active=False,  # (presume was active at the time)
            )
            alex.leaderrating_set.add(rating)
        with freeze_time("2019-02-15 12:25:00 EST"):
            rating = factories.LeaderRatingFactory.create(
                participant=alex,
                activity=models.BaseRating.WINTER_SCHOOL,
                rating='Full leader',
                active=False,  # (presume was active at the time)
            )
            alex.leaderrating_set.add(rating)
        trip = factories.TripFactory.create(
            trip_date=date(2019, 2, 23), activity=models.BaseRating.WINTER_SCHOOL
        )

        # At present, Alex is not even a leader
        self.assertFalse(alex.is_leader)
        # However, when that past trip happened, he was a leader.
        self.assertEqual('Alex Honnold (Full leader)', alex.name_with_rating(trip))

    @freeze_time("2018-11-10 12:25:00 EST")
    def test_future_trip(self):
        john = factories.ParticipantFactory.create(name='John Long')

        john.leaderrating_set.add(
            factories.LeaderRatingFactory.create(
                participant=john,
                activity=models.BaseRating.WINTER_SCHOOL,
                rating='Full leader',
            )
        )
        trip = factories.TripFactory.create(
            trip_date=date(2019, 10, 23), activity=models.BaseRating.WINTER_SCHOOL
        )
        self.assertEqual('John Long (Full leader)', john.name_with_rating(trip))
