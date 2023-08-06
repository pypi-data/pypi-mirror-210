from datetime import datetime

class QuotaManager():

    def __init__(self, api_name=None):
        """Quota Manager initializer

        Args:
            api_name (str, optional): Name of api i.e. BulkAPI, Bullhorn etc etc.
        """
        self.api_name = api_name
        self.second = ['1 second', '1second', 'second']
        self.minute = ['1 minute', '1minute', 'minute']
        self.hour = ['1 hour', '1hour', 'hour']
        self.day = ['1 day', '1day', 'day']
        self.month = ['1 month', '1month', 'month']
        self.year = ['1 year', '1year', 'year']
    
    def log(self, msg):
        """Method to print/log message

        Args:
            msg (str): message to print/log
        """
        print(msg)

    def get_current_month_year_seconds(self, cal_type='month'):
        """Method to get the current month/year seconds

        Returns:
            int: total seconds in a month/year
        """
        total_days = 0
        # current_date = datetime.strptime('2023-11-07 00:00:00', '%Y-%m-%d %H:%M:%S')
        current_date = datetime.utcnow()
        
        if cal_type.lower() == 'month':
            # Get the first day of the current month
            first_day = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate the number of days in the current month
            if current_date.month == 12:
                next_month = first_day.replace(year=current_date.year + 1, month=1)
            else:
                next_month = first_day.replace(month=current_date.month + 1)
            total_days = (next_month - first_day).days
        
        if cal_type.lower() == 'year':
            first_day = current_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            next_year = first_day.replace(year=current_date.year + 1, month=1)
            total_days = (next_year - first_day).days
                    
        return total_days * 24 * 60 * 60 #total seconds 

    def get_seconds(self, qtime):
        """Method to get seconds from quota time

        Args:
            qtime (str): quota time i.e. 1 second, 1 minute, 1 hour, 1 day
        Returns:
            int: total seconds
        """
        if qtime.lower() in self.second:
            return 1
        elif qtime.lower() in self.minute:
            return 60
        elif qtime.lower() in self.hour:
            return 3600
        elif qtime.lower() in self.day:
            return 86400
        elif qtime.lower() in self.month:
            return self.get_current_month_year_seconds(cal_type='month')
        elif qtime.lower() in self.year:
            return self.get_current_month_year_seconds(cal_type='year')
        
    
    def get_start_time(self, now_dt, qtime):
        """Method to get the start time of quota

        Args:
            now_dt (datetime): datetime object with UTC datetime now
            qtime (str): quota time i.e. 1 second, 1 minute, 1 hour, 1 day, 1 month, 1 year etc

        Returns:
            datetime: datetime of start time UTC based
        """
        
        if qtime.lower() in self.minute:
            before_time = now_dt.replace(second=59)
        elif qtime.lower() in self.hour:
            before_time = now_dt.replace(minute=59, second=59)
        elif qtime.lower() in self.day:
            before_time = now_dt.replace(hour=23, minute=59, second=59)
        elif qtime.lower() in self.month:
            # before_time = now_dt.replace(day=1, hour=0, minute=0, second=0)
            first_day = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate the number of days in the current month
            if now_dt.month == 12:
                before_time = first_day.replace(year=now_dt.year + 1, month=1)
            else:
                before_time = first_day.replace(month=now_dt.month + 1)
        elif qtime.lower() in self.year:
            before_time = now_dt.replace(year=now_dt.year + 1, month=1, day=1, hour=0, minute=0, second=0)
        else:
            return now_dt
        return before_time


    def calculate_requests_quota(self, total_quota, used_quota, qtime='1 hour'):
        """Method to calculate the time interval for next request

        Args:
            total_quota (int): total number of API requests
            used_quota (int): total number of consumed API requests
            qtime (str, optional): quota time i.e. 1 second, 1 minute, 1 hour, 1 day
        Returns:
            str: requests in specific time i.e. 1 request in 29 seconds
        """
        self.log(f'request received to calculate quota per second for {self.api_name}')
        now_dt = datetime.utcnow()
        after_time = self.get_start_time(now_dt, qtime)
        # seconds = self.get_seconds(qtime)
        # (total_quota - used_quota)
        remaining_time = after_time - now_dt
        msg = f'now-time : {now_dt},\nend-time: {after_time},\nquota-remaining-time: {remaining_time}'
        self.log(msg)
        total_seconds = int(str(remaining_time.total_seconds()).split('.')[0])
        self.log(f'total-remaining-time-in-seconds : {total_seconds}')
        
        pending_requests = total_quota - used_quota
        self.log(f'balance requests : {pending_requests}')
        if pending_requests <= 0:
            msg = f'All quota used, please wait for {total_seconds} seconds'
            quota_time = f'{total_seconds} seconds'
            quota_per_second = 0
        if total_seconds <= 0:
            msg = f'Quota is going to renew in 0 seconds'
            quota_time = '0 second'
            quota_per_second = 0
        else:
            if pending_requests <= total_seconds:
                quota_per_second = total_seconds / pending_requests
                quota_per_second = round(quota_per_second, 2)
                msg = f'1 request in {quota_per_second} seconds'
                quota_time = f'{quota_per_second} second'
                quota_per_second = 1
            else:
                quota_per_second = pending_requests / total_seconds
                quota_per_second = round(quota_per_second, 2)
                msg = f'{quota_per_second} request in 1 seconds'
                quota_time = '1 second'
        return {
                'msg': msg,
                'requests': quota_per_second,
                'time': quota_time
                }


# objq = QuotaManager('bulkapi')
# print(objq.calculate_requests_quota(2000, 500, '1 hour'))
