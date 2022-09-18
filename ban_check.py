from typing import Optional
import requests
import re
import datetime


def check_turkish_ban_date(site: str) -> Optional[datetime.date]:
    """
    Looks up when a site (domain + tld) was banned in turkey.
    Returns None if the site isn't banned.
    Works regardless of caller IP.
    Usage: `check_turkish_ban_date('wikileaks.org')`
    """
    reg = re.compile(f"{site}, (?P<day>.*?)/(?P<month>.*?)/(?P<year>.*?) tarihli")

    response = requests.get("http://195.175.254.2", headers={"Host": site})
    result = reg.search(response.text)

    if not result:
        return None

    (day, month, year) = result.groups()
    return datetime.date(int(year), int(month), int(day))
