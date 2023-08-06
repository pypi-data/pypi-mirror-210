from datetime import datetime, time, timedelta
from gi.repository import GLib
from OpenRadio.core.const import LOG_LEVEL, LOG_HANDLER
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)
LOGGER.propagate = False


class TimeThread:
    def __init__(self, alarms, parent):
        self.parent = parent
        self.timeout_exit = False
        self.alarms = {}
        self.alarms_today = {}
        for alarm_id in alarms:
            alarm = alarms[alarm_id]
            self.add_alarm(alarm_id, alarm)

        self.update_alarms_today(update_time_callback=True)

        check_thread = GLib.timeout_add_seconds(
            1, self._check_alarms
        )  # Check if alarm should ring

    def _exit(self):
        self.timeout_exit = True

    def _check_alarms(self):
        current_date = datetime.now()
        current_time = current_date.time()
        if self.timeout_exit:
            return False

        for alarm_id in self.alarms_today:
            alarm = self.alarms_today[alarm_id]
            if alarm["time_obj"] < current_time:
                LOGGER.debug("Playing alarm : {}".format(alarm_id))
                self.alarms_today.pop(alarm_id)
                self.parent._show_alarm(alarm_id)
                break

        return True

    def update_alarms_today(self, update_time_callback=False):
        self.alarms_today = {}
        current_date = datetime.now()
        current_time = current_date.time()

        # Get the time until midnight and set the next update time
        if update_time_callback:
            midnight = current_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)

            seconds_until_midnight = (midnight - current_date).total_seconds()
            mircos_until_midnight = seconds_until_midnight * 1000
            LOGGER.debug(
                f"Setting next callback in {mircos_until_midnight} micros."
            )
            GLib.timeout_add(mircos_until_midnight, self.update_alarms_today, True)

        for alarm_id in self.alarms:
            alarm = self.alarms[alarm_id]

            if current_date.weekday() not in alarm["alarm_detail"]["weekdays"]:
                LOGGER.debug(f"Alarm {alarm_id} won't ring today.")
                continue

            if current_time > alarm["time_obj"]:
                LOGGER.debug(f"Alarm {alarm_id} would've rung sooner")
                continue

            self.alarms_today[alarm_id] = alarm
            LOGGER.debug(f"Alarm {alarm_id} will ring to today.")
        return False

    def update_alarm(self, alarm_id, new_alarm):
        self.remove_alarm(alarm_id)
        self.add_alarm(alarm_id, new_alarm)

    def remove_alarm(self, alarm_id):
        if alarm_id in self.alarms:
            self.alarms.pop(alarm_id)
        self.update_alarms_today()

    def add_alarm(self, alarm_id, alarm):
        LOGGER.debug(f"Adding {alarm_id} to timeline.")
        hours = alarm["hours"]
        minutes = alarm["minutes"]
        weekdays = alarm["weekdays"]
        alarm_time = time(hour=hours, minute=minutes)
        alarm_dict = {"time_obj": alarm_time, "alarm_detail": alarm}
        self.alarms[alarm_id] = alarm_dict
        self.update_alarms_today()
