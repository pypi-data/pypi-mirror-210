from enum import StrEnum
from time import mktime
from datetime import datetime

class TimeStampType(StrEnum):
	Default = ""
	_MONTHNAME_DATE_YEAR_HOUR_MINUTE = ":f"
	Short_Time = ":t"
	_HOUR_MINUTE = ":t"
	Long_Time = ":T"
	_HOUR_MINUTE_SECOND = ":T"
	Short_Date = ":d"
	_MONTH_DATE_YEAR = ":d"
	Long_Date = ":D"
	_MONTHNAME_DATE_YEAR = ":D"
	Short_Date_Time = ":f"
	Long_Date_Time = ":F"
	_WEEKNAME_MONTHNAME_DATE_YEAR_HOUR_MINUTE = ":F"
	Relative = ":R"

def discordtimestamp(time: datetime, type: TimeStampType = TimeStampType.Default) -> str:
	return f"<t:{mktime(time.timestamp())}{type.value}>".replace(".0", "")