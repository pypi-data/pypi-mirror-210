from wiliot_deployment_tools.common.utils import *
import time
import datetime

IS_DATABRICKS = is_databricks()


class ConfigParamsException(Exception):
    def __init__(self, value_name, value):
        """
        :type value_name: string
        :param value_name: value name as appears fo the user
        :type value: string
        :param value: value received
        """
        raise Exception("Please enter valid value to the field '" + str(value_name) +
                        "' (received value is " + str(value) + ")")


class ConfigureDevices:
    if IS_DATABRICKS:
        db_utils().widgets.removeAll()
        db_utils().widgets.text('Edge Management API Key', '')
        db_utils().widgets.dropdown('Environment', 'prod', ['prod', 'test'])
        db_utils().widgets.dropdown('Client', 'Platform', ['Platform', 'Management'])
        db_utils().widgets.text("Owner", '')

        db_utils().widgets.dropdown("Enter or Exit contextual energizing", 'Enter', ['Enter', 'Exit'])
        db_utils().widgets.text("Bridges to configure", '')

        db_utils().widgets.text("Energizing time (in minutes)", '')
        db_utils().widgets.text("Idle time (in minutes)", '')
        db_utils().widgets.text("Start time for energizing (hour, minutes)", '8, 0')

    else:
        debug_print('Running locally, make sure to pass all params for test to run successfully')

    def __init__(self):
        """"
        initialize and save parameters from user
        """
        def check_legal_values():
            if self.enter_or_exit not in ['Enter', 'Exit']:
                raise ConfigParamsException("Enter or Exit contextual energizing ('Enter', 'Exit')",
                                            str(self.enter_or_exit))
            if self.brgs_ids is None:
                raise ConfigParamsException("Bridges to configure", str(self.brgs_ids))

            if self.start_time is None:
                raise ConfigParamsException("Start time for energizing (hour, minutes)", str(self.start_time))
            if len(self.start_time) is not 2:
                raise Exception("Not enough values in 'Start time for energizing (hour, minutes)'")

        if IS_DATABRICKS:
            api_key = db_utils().widgets.get("Edge Management API Key")
            env = db_utils().widgets.get("Environment")
            owner = db_utils().widgets.get('Owner')
            self.enter_or_exit = db_utils().widgets.get('Enter or Exit contextual energizing')
            self.on_duration = db_utils().widgets.get('Energizing time (in minutes)')
            self.idle_duration = db_utils().widgets.get('Idle time (in minutes)')

            self.brgs_ids = db_utils().widgets.get("Bridges to configure").replace(' ', '')
            self.brgs_ids = "".join(self.brgs_ids.split())
            self.brgs_ids = None if self.brgs_ids == '' else self.brgs_ids.split(",")

            self.start_time = db_utils().widgets.get("Start time for energizing (hour, minutes)").replace(' ', '')
            self.start_time = "".join(self.start_time.split())
            self.start_time = None if self.start_time == '' else self.start_time.split(",")

        check_legal_values()
        self.contextual_energizing_client = ContextualEnergizingClient(api_key, owner, env)
        self.sleep_until(int(self.start_time[0]), int(self.start_time[1]))
        # TODO - add the configuration part here, using self.contextual_energizing_client.exit_contextual_energizing()

    def sleep_until(self, hour, minute):
        """
        will wait until the desired time inserted to function (supports up to 24 hours ahead)
        :type hour: int
        :param hour: hour to start working (24-hour scale)
        :type minute: int
        :param minute: minute to start working (60-minute scale)
        """
        run_start_time = datetime.datetime.today()
        future = datetime.datetime(run_start_time.year, run_start_time.month, run_start_time.day, hour, minute)
        if future < run_start_time:
            try:
                future = \
                    datetime.datetime(run_start_time.year, run_start_time.month, run_start_time.day + 1, hour, minute)
            except Exception():
                try:
                    future = datetime.datetime(run_start_time.year, run_start_time.month + 1, 1, hour, minute)
                except Exception():
                    future = datetime.datetime(run_start_time.year + 1, 1, 1, hour, minute)

        debug_print("Waiting to the desired time to start configuration process")
        time.sleep(min((future - run_start_time).total_seconds(), 24 * 60 * 60))


if __name__ == '__main__':
    pass
