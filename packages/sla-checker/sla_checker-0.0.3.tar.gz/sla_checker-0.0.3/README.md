# SLA Checker

SLA Checker helps to check if an event is within the defined SLA.

## Installation

```
pip3 install sla-checker
```

## Usage

Input parameters:

* `event_start`: when the event starts (e.g. when a trouble ticket is created)
* `event_end`: when the event ends (e.g. when the trouble ticket is solved)
* `country_code` (optional if `working_on_holidays = True`): the country code (e.g. IT)
* `minutes_to_resolve`: maximum time in minutes allowed between `event_start` and `event_end`
* `opening_hours` (optional if 7x24 service): define opening hours (e.g. `09:00`)
* `closing_hours` (optional if 7x24 service): define closing hours (e.g. `18:00`)
* `working_on_sat` (optional, default is `False`): define if Saturday is a working day
* `working_on_holidays` (optional, default is `False`): define if Sunday and Holidays are working days

Example (7x24 service with 2 hours SLA):

```
sla = sla_checker.SLAChecker()
sla.check(
  event_start = datetime.datetime(2020, 12, 24, 17, 0, 0),
  event_end = datetime.datetime(2020, 12, 28, 10, 0, 1),
  country_code = "IT",
  minutes_to_resolve = 120,
)
```

Example (5x9 service with 2 hours SLA):

```
sla = sla_checker.SLAChecker()
sla.check(
  event_start = datetime.datetime(2020, 12, 24, 17, 0, 0),
  event_end = datetime.datetime(2020, 12, 28, 10, 0, 1),
  country_code = "IT",
  minutes_to_resolve = 120,
  opening_hours = "09:00",
  closing_hours = "18:00",
  working_on_sat = False,
  working_on_holidays = False,
)
```

Example (7x9 service with 2 hours SLA):

```
sla = sla_checker.SLAChecker()
sla.check(
  event_start = datetime.datetime(2020, 12, 24, 17, 0, 0),
  event_end = datetime.datetime(2020, 12, 28, 10, 0, 1),
  country_code = "IT",
  minutes_to_resolve = 120,
  opening_hours = "09:00",
  closing_hours = "18:00",
  working_on_sat = True,
  working_on_holidays = True,
)
```
