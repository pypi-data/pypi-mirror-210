import datetime
import time

DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_WEEK_FORMAT = '%Y#%W'
DEFAULT_MONTH_FORMAT = '%Y-%m'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATETIME_FILE_FORMAT = '%Y_%m_%d_%H_%M_%S'

"""
%a	星期的英文单词的缩写：如星期一， 则返回 Mon
%A	星期的英文单词的全拼：如星期一，返回 Monday
%b	月份的英文单词的缩写：如一月， 则返回 Jan
%B	月份的引文单词的缩写：如一月， 则返回 January
%c	返回datetime的字符串表示，如03/08/15 23:01:26
%d	返回的是当前时间是当前月的第几天
%f	微秒的表示： 范围: [0,999999]
%H	以24小时制表示当前小时
%I	以12小时制表示当前小时
%j	返回 当天是当年的第几天 范围[001,366]
%m	返回月份 范围[0,12]
%M	返回分钟数 范围 [0,59]
%P	返回是上午还是下午–AM or PM
%S	返回秒数 范围 [0,61]。。。手册说明的
%U	返回当周是当年的第几周 以周日为第一天
%W	返回当周是当年的第几周 以周一为第一天
%w	当天在当周的天数，范围为[0, 6]，6表示星期天
%x	日期的字符串表示 ：03/08/15
%X	时间的字符串表示 ：23:22:08
%y	两个数字表示的年份 15
%Y	四个数字表示的年份 2015
%z	与utc时间的间隔 （如果是本地时间，返回空字符串）
%Z	时区名称（如果是本地时间，返回空字符串）
"""


class DateTimeTool:
    @staticmethod
    def get_current_timestamp_ms():
        return int(time.time() * 1000)

    @staticmethod
    def get_current_timestamp():
        return int(time.time())

    @staticmethod
    def format_current_time(format_str=DEFAULT_DATETIME_FORMAT):
        return datetime.datetime.now().strftime(format_str)

    @staticmethod
    def get_yesterday():
        return DateTimeTool.get_past_date()

    @staticmethod
    def format_yesterday(format_str=DEFAULT_DATE_FORMAT):
        yesterday = DateTimeTool.get_yesterday()
        return yesterday.strftime(format_str)

    @staticmethod
    def get_day_start_time(date=datetime.datetime.now()):
        return datetime.datetime.combine(date, datetime.time.min)

    @staticmethod
    def get_day_end_time(date=datetime.datetime.now()):
        return datetime.datetime.combine(date, datetime.time.max)

    @staticmethod
    def timestamp_to_datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def datetime_to_timestamp(date_time):
        return int(date_time.timestamp())

    @staticmethod
    def date_to_datetime(d):
        return datetime.datetime.combine(d, datetime.time.min)

    @staticmethod
    def datetime_to_date(dt):
        return dt.date()

    @staticmethod
    def format_date(date, format_str=DEFAULT_DATE_FORMAT):
        return date.strftime(format_str)

    @staticmethod
    def str_to_date(date_str, format_str=DEFAULT_DATE_FORMAT):
        return datetime.datetime.strptime(date_str, format_str)

    @staticmethod
    def get_past_date(today=datetime.datetime.now(), days=1):
        """
        获取过去时间 days => number
        如果days为负数，则获取未来时间
        默认获取昨天时间
        :param days:
        :return:
        """
        return today - datetime.timedelta(days=days)

    @staticmethod
    def get_dates_range(start_date, end_date, format=DEFAULT_DATE_FORMAT):
        """
         根据开始日期、结束日期返回这段时间里所有天的集合
        :param start_date: 开始日期时间戳
        :param end_date: 结束日期时间戳
        :param format:  格式化类型
        :return:
        """
        list = []
        list.append(start_date.strftime(format))
        while start_date < end_date:
            start_date += datetime.timedelta(days=1)
            list.append(DateTimeTool.format_date(start_date, format))
        return list


# start = datetime.datetime(2023,5,1)
# end = datetime.datetime(2023,5,25)
# print(DateTimeTool.get_dates_range(start,end))


class WeekTool:
    @staticmethod
    def get_weekday(date=datetime.datetime.now()):
        return date.weekday()

    @staticmethod
    def get_weekday_name(date=datetime.datetime.now()):
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return weekday_names[date.weekday()]

    @staticmethod
    def get_week_number(date=datetime.datetime.now()):
        return date.isocalendar()[1]

    @staticmethod
    def get_week_number_to_format(date=datetime.datetime.now(), format=DEFAULT_WEEK_FORMAT):
        return DateTimeTool.format_date(date, format)

    @staticmethod
    def get_week_numbers(start_date, end_date):
        current_date = start_date
        week_numbers = set()
        while current_date <= end_date:
            week_numbers.add(WeekTool.get_week_number(current_date))
            current_date += datetime.timedelta(days=1)
        return sorted(list(week_numbers))

    @staticmethod
    def get_week_numbers_to_format(start_date, end_date, format=DEFAULT_WEEK_FORMAT):
        week_list = []
        while start_date < end_date:
            week_list.append(DateTimeTool.format_date(start_date, format))
            start_date += datetime.timedelta(days=7)
        return list(set(week_list))

    @staticmethod
    def get_week_start_time(date=datetime.datetime.now()):
        start_of_week = date - datetime.timedelta(days=date.weekday())
        return datetime.datetime.combine(start_of_week, datetime.time.min)

    @staticmethod
    def get_week_end_time(date=datetime.datetime.now()):
        end_of_week = date + datetime.timedelta(days=6 - date.weekday())
        return datetime.datetime.combine(end_of_week, datetime.time.max)

    @staticmethod
    def get_week_range(start_date, end_date):
        current_date = start_date
        week_ranges = []
        while current_date <= end_date:
            week_start = WeekTool.get_week_start_time(current_date)
            week_end = WeekTool.get_week_end_time(current_date)
            week_ranges.append((week_start, week_end))
            current_date += datetime.timedelta(days=7)
        return week_ranges

    @staticmethod
    def get_week_range_dict_iter(start_date, end_date, format=DEFAULT_WEEK_FORMAT):
        current_date = start_date
        week_ranges = []
        while current_date <= end_date:
            week_start = WeekTool.get_week_start_time(current_date)
            week_end = WeekTool.get_week_end_time(current_date)
            if week_start < start_date:
                week_start = start_date
            if end_date < week_end:
                week_end = end_date
            cur_week_str = WeekTool.get_week_number_to_format(week_start, format=format)
            item = {
                cur_week_str: (week_start, week_end)
            }
            week_ranges.append(item)
            current_date += datetime.timedelta(days=7)
        return week_ranges


# # 示例用法
# current_date = datetime.date.today()
# print("当前日志所在的星期几:", WeekTool.get_weekday(current_date))
# print("当前日志所在的星期几[名字]:", WeekTool.get_weekday_name(current_date))
# print("当前日志所在的第几周:", WeekTool.get_week_number(current_date))
#
# start_date = datetime.datetime(2023, 1, 10)
# end_date = datetime.datetime(2023, 12, 31)
# week_numbers = WeekTool.get_week_numbers(start_date, end_date)
# print(week_numbers)
#
#
# print("指定时间所在周开始时间",WeekTool.get_week_start_time(current_date))
# print("指定时间所在周结束时间",WeekTool.get_week_end_time(current_date))
# result = WeekTool.get_week_range(start_date,end_date)
# print(result)
# result = WeekTool.get_week_range_dict_iter(start_date,end_date)
# print(result)


class MonthTool:

    @staticmethod
    def get_month(date=datetime.datetime.now()):
        return date.month

    @staticmethod
    def get_month_name(date=datetime.datetime.now()):
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                       "October", "November", "December"]
        return month_names[date.month - 1]

    @staticmethod
    def get_all_months(start_date, end_date, format=DEFAULT_MONTH_FORMAT):
        current_date = start_date
        months = set()
        while current_date <= end_date:
            months.add(current_date.strftime(format))
            current_date = current_date.replace(day=1) + datetime.timedelta(days=32)
            current_date = current_date.replace(day=1)
        return sorted(list(months))

    @staticmethod
    def get_month_start_time(date=datetime.datetime.now()):
        start_of_month = date.replace(day=1)
        return datetime.datetime.combine(start_of_month, datetime.time.min)

    @staticmethod
    def get_month_end_time(date=datetime.datetime.now()):
        next_month = date.replace(day=28) + datetime.timedelta(days=4)
        end_of_month = next_month - datetime.timedelta(days=next_month.day)
        return datetime.datetime.combine(end_of_month, datetime.time.max)

    @staticmethod
    def get_past_month(date=datetime.datetime.now(),num=1):
        """
        获取指定日期过去月份数的日期
        如果number为负数，则是未来日期
        默认是过去一个月日期
        :param date:
        :return:
        """
        past_month = date.month - num
        try:
            past_year_date = date.replace(month=past_month)
        except Exception as e:
            day = date.day - 1
            past_year_date = date.replace(month=past_month,day=day)
        return past_year_date

    @staticmethod
    def get_month_range(start_date, end_date):
        current_date = start_date
        month_ranges = []

        while current_date <= end_date:
            month_start = MonthTool.get_month_start_time(current_date)
            month_end = MonthTool.get_month_end_time(current_date)
            month_ranges.append((month_start, month_end))
            current_date = current_date.replace(day=1) + datetime.timedelta(days=32)
            current_date = current_date.replace(day=1)
        return month_ranges

    @staticmethod
    def get_month_range_dict_iter(start_date, end_date, format=DEFAULT_MONTH_FORMAT):
        current_date = start_date
        month_ranges = []

        while current_date <= end_date:
            month_start = MonthTool.get_month_start_time(current_date)
            month_end = MonthTool.get_month_end_time(current_date)
            if month_start < start_date:
                month_start = start_date
            if end_date < month_end:
                month_end = end_date
            cur_month_str = DateTimeTool.format_date(month_start, format)
            item = {
                cur_month_str: (month_start, month_end)
            }
            month_ranges.append(item)
            current_date = current_date.replace(day=1) + datetime.timedelta(days=32)
            current_date = current_date.replace(day=1)
        return month_ranges


# 示例用法
# current_date = datetime.date.today()
# print("当前日志所在的月份名字[英文]:", MonthTool.get_month_name(current_date))
#
# start_date = datetime.datetime(2023, 1, 1)
# end_date = datetime.datetime(2023, 12, 31)
# months = MonthTool.get_all_months(start_date, end_date)
# print("指定时间段内所有月份:", months)
#
# specified_date = datetime.date(2023, 5, 24)
# month_start_time = MonthTool.get_month_start_time(specified_date)
# month_end_time = MonthTool.get_month_end_time( datetime.date(2021, 2, 4))
# print("时间所在月份最小时间:", month_start_time)
# print("时间所在月份最大时间:", month_end_time)
#
# next_month = MonthTool.get_next_month(specified_date)
# print("指定时间下一个月时间:", next_month)
#
# date_range = (datetime.datetime(2023, 5, 10), datetime.datetime(2023, 7, 31))
# month_ranges = MonthTool.get_month_range(*date_range)
# print("给定时间（日期）区间中所有月份起止时间:", month_ranges)
#
# month_ranges = MonthTool.get_month_range_dict_iter(*date_range)
# print("给定时间（日期）区间中所有月份起止时间:", month_ranges)


class YearTool:
    import datetime

    @staticmethod
    def get_year(date=datetime.datetime.now()):
        """
        获取指定日期年份
        :param date: 指定日期，格式为'YYYY-MM-DD'
        :return: 年份数据
        """
        return date.year

    @staticmethod
    def is_leap_year(date=datetime.datetime.now()):
        """
        判断指定日期是否是闰年
        :param date: 指定日期，格式为'YYYY-MM-DD'
        :return: 是闰年返回True，否则返回False
        """
        year = YearTool.get_year(date=datetime.datetime.now())
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return True
        else:
            return False

    @staticmethod
    def get_past_year(date=datetime.datetime.now(),num=1):
        """
        获取指定日期过去年数日期
        如果years是负数则是未来的日期
        :param date: 指定日期，格式为'YYYY-MM-DD'
        :return: 前一年时间，格式为'YYYY-MM-DD'
        """
        past_year = date.year - num
        try:
            past_year_date = date.replace(year=past_year)
        except Exception as e:
            day = date.day - 1
            past_year_date = date.replace(year=past_year,day=day)
        return past_year_date

    @staticmethod
    def get_year_start_time(date=datetime.datetime.now()):
        start_of_month = date.replace(day=1)
        return datetime.datetime.combine(start_of_month, datetime.time.min)

    @staticmethod
    def get_year_end_time(date=datetime.datetime.now()):
        next_month = date.replace(day=28) + datetime.timedelta(days=4)
        end_of_month = next_month - datetime.timedelta(days=next_month.day)
        return datetime.datetime.combine(end_of_month, datetime.time.max)

    @staticmethod
    def get_year_range(start_date, end_date):
        """
        给定时间（日期）区间，返回区间中所有年份起止时间
        :param start_date: 区间起始日期，格式为'YYYY-MM-DD'
        :param end_date: 区间截止日期，格式为'YYYY-MM-DD'
        :return: 所有年份起止时间列表，格式为[(年份1起始时间，年份1截止时间), (年份2起始时间，年份2截止时间), ...]
        """
        start_year = datetime.datetime.strptime(start_date, '%Y-%m-%d').year
        end_year = datetime.datetime.strptime(end_date, '%Y-%m-%d').year
        year_range = []
        for year in range(start_year, end_year + 1):
            year_start_date = datetime.datetime.strptime(str(year) + '-01-01', '%Y-%m-%d').strftime('%Y-%m-%d')
            year_end_date = datetime.datetime.strptime(str(year) + '-12-31', '%Y-%m-%d').strftime('%Y-%m-%d')
            year_range.append((year_start_date, year_end_date))
        return year_range

d = datetime.datetime(2024,2,29)
print( YearTool.get_past_year(d) )