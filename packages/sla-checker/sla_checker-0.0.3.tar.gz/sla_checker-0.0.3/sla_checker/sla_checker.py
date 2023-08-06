"""sla_checker main class."""
__author__ = "Andrea Dainese"
__contact__ = "andrea@adainese.it"
__copyright__ = "Copyright 2022, Andrea Dainese"
__license__ = "GPLv3"

import datetime
import logging
import holidays


class SLAChecker:
    """SLAChecker main class."""

    country_holidays = None  # Don't include Sundays
    opening_hours = None
    closing_hours = None
    working_on_sat = True
    working_on_holidays = True
    full_day_service = True

    def __init__(
        self,
        country_code: str = None,
        opening_hours: datetime.time = None,
        closing_hours: datetime.time = None,
        working_on_sat: bool = True,
        working_on_holidays: bool = True,
    ) -> None:
        """Create a SLAChecker object.

        SLAChecker obejct stores the common values to be used to check if an event is within a SLA.

        Input parameters:

        * country_code: the country code (e.g. IT).
          Optional if working_on_holidays == True.
        * opening_hours: define opening hours (e.g. datetime.time(6, 0)).
          Optional if full day service. If set must be lower than closing_hours.
        * closing_hours: define closing hours (e.g. datetime.time(22, 0)).
          Optional if full day service. If set must be greater than opening_hours.
        * working_on_sat: define if Saturday is a working day.
          Optional, default is True.
        * working_on_holidays: define if Sunday and Holidays are working days.
          Optional, default is True. If False country_code is mandatory.

        To define a 24x7 service, set working_on_sat = True and working_on_holidays = True only.
        """
        if country_code:
            try:
                self.country_holidays = holidays.country_holidays(country_code)
            except NotImplementedError as exc:
                raise ValueError("country_code is not supported.") from exc

        if (opening_hours and not closing_hours) or (
            not opening_hours and closing_hours
        ):
            raise ValueError(
                "opening_housrs and closing_hours must be both set or both unset."
            )

        if closing_hours and closing_hours <= opening_hours:
            raise ValueError(
                "if set, closing_hours must be greater than opening_hours."
            )

        if not working_on_holidays and not country_code:
            raise ValueError(
                "if working_on_holidays is False country_code is mandatory."
            )

        self.opening_hours = opening_hours
        self.closing_hours = closing_hours
        self.working_on_sat = working_on_sat
        self.working_on_holidays = working_on_holidays
        if opening_hours:
            self.full_day_service = False

    def check(self, *args, **kwargs) -> bool:
        """
        Transision function to make compatible the legacy syntax.

        Current syntax:

        * event_start: datetime.datetime
        * event_end: datetime.datetime
        * minutes_to_resolve: int

        Legacy syntax:

        * event_start
        * event_end
        * minutes_to_resolve: int
        * country_code: str = None
        * opening_hours: str = None
        * closing_hours: str = None
        * working_on_sat: bool = False
        * working_on_holidays: bool = False
        """
        if (
            kwargs.get("working_on_holidays")
            or kwargs.get("working_on_sat")
            or kwargs.get("closing_hours")
            or kwargs.get("opening_hours")
            or kwargs.get("country_code")
        ):
            # Legacy syntax
            return self.check_v1(*args, **kwargs)

        # Current syntax
        return self.check_v2(*args, **kwargs)

    def check_v2(
        self,
        event_start: datetime.datetime,
        event_end: datetime.datetime,
        minutes_to_resolve: int,
    ) -> bool:
        """Check if an event is within a SLA.

        Input parameters:

        * event_start: when the event starts (e.g. when a trouble ticket is created)
        * event_end: when the event ends (e.g. when the trouble ticket is solved)
        * minutes_to_resolve: maximum time in minutes allowed between `event_start` and `event_end`
        """
        # Checking start and end time
        if event_start > event_end:
            raise ValueError("event_end must follow event_start")

        remaining_seconds = minutes_to_resolve * 60
        current_datetime = event_start

        while remaining_seconds >= 0:
            current_weekday = (
                current_datetime.weekday()
            )  # Current day of the week (0 is Monday)
            if self.full_day_service:
                # Full day service (opening at 00:00, closing at 24:00)
                current_opening_hours = datetime.datetime(
                    current_datetime.year,
                    current_datetime.month,
                    current_datetime.day,
                    0,
                    0,
                )
                current_closing_hours = datetime.datetime(
                    current_datetime.year,
                    current_datetime.month,
                    current_datetime.day + 1,
                    0,
                    0,
                )
            else:
                current_opening_hours = datetime.datetime(
                    current_datetime.year,
                    current_datetime.month,
                    current_datetime.day,
                    self.opening_hours.hour,
                    self.opening_hours.minute,
                )
                current_closing_hours = datetime.datetime(
                    current_datetime.year,
                    current_datetime.month,
                    current_datetime.day,
                    self.closing_hours.hour,
                    self.closing_hours.minute,
                )

            if (
                (self.working_on_holidays and self.working_on_sat)
                or (
                    self.working_on_holidays
                    and current_datetime in self.country_holidays
                )
                or (self.working_on_holidays and current_weekday == 6)
                or (
                    self.working_on_sat
                    and current_datetime not in self.country_holidays
                    and current_weekday == 5
                )
                or (
                    current_datetime not in self.country_holidays
                    and current_weekday < 5
                )
            ):
                # Working day
                if current_datetime < current_opening_hours:
                    print("BEFORE")
                    # Before opening hours (shift to the current opening hours)
                    current_datetime = current_opening_hours
                elif current_datetime > current_closing_hours:
                    print("AFTER")
                    # After closing hours (shift to next day at opening hours)
                    current_datetime = current_opening_hours + datetime.timedelta(
                        days=1
                    )
                else:
                    print("WITHIN")
                    # Within opening hours
                    if event_end.date() == current_datetime.date():
                        print("ENDS TODAY")
                        # Event ends within the current day
                        remaining_seconds = (
                            remaining_seconds
                            - (event_end - current_datetime).total_seconds()
                        )
                        if remaining_seconds >= 0:
                            # Event is within the SLA
                            return True
                    else:
                        print("DONT END TODAY")
                        # Event doesn't end within the current day (update remaining_seconds and
                        # current_datetime)
                        remaining_seconds = (
                            remaining_seconds
                            - (current_closing_hours - current_datetime).total_seconds()
                        )
                        current_datetime = current_opening_hours + datetime.timedelta(
                            days=1
                        )
                        print(remaining_seconds)
                        print(current_datetime)
            else:
                # Not a working day
                current_datetime = current_opening_hours + datetime.timedelta(days=1)

        # SLA expired
        return False

    def check_v1(
        self,
        event_start,
        event_end,
        minutes_to_resolve: int,
        country_code: str = None,
        opening_hours: str = None,
        closing_hours: str = None,
        working_on_sat: bool = True,
        working_on_holidays: bool = True,
    ) -> bool:
        """Check if an event is within a SLA (legacy)."""
        logging.warning("Deprecated syntax, will be removed soon.")
        if country_code:
            try:
                self.country_holidays = holidays.country_holidays(country_code)
            except NotImplementedError as exc:
                raise ValueError("country_code is not supported") from exc
        self.country_code = (  # pylint: disable=attribute-defined-outside-init
            country_code
        )

        if (opening_hours and not closing_hours) or (
            closing_hours and not opening_hours
        ):
            raise ValueError(
                "opening_hours and closing_hours must be set or both unset"
            )

        if opening_hours:
            self.full_day_service = False
            try:
                opening_hour = int(opening_hours.split(":")[0])
                opening_minute = int(opening_hours.split(":")[1])
                self.opening_hours = datetime.time(opening_hour, opening_minute)
            except ValueError as exc:
                raise ValueError(
                    'opening_hours must be in the format of "HH:MM"'
                ) from exc
            try:
                closing_hour = int(closing_hours.split(":")[0])
                closing_minute = int(closing_hours.split(":")[1])
                self.closing_hours = datetime.time(closing_hour, closing_minute)
            except ValueError as exc:
                raise ValueError(
                    'closing_hours must be in the format of "HH:MM"'
                ) from exc

        self.working_on_sat = working_on_sat
        self.working_on_holidays = working_on_holidays

        return self.check(
            event_start=event_start,
            event_end=event_end,
            minutes_to_resolve=minutes_to_resolve,
        )
