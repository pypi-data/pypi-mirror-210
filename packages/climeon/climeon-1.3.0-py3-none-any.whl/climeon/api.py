"""Climeon API wrapper, used to access the Climeon API from Python.

Authentication credentials will be fetched from environment variables
``API_USER`` and ``API_PASS`` or programatically at client instantiation or
else through user interaction via Climeon Live Azure B2C.
"""

# Standard modules
from datetime import datetime, timedelta, timezone
from getpass import getpass
from hashlib import sha1
from io import StringIO
import lzma
import json
from logging import getLogger, disable, CRITICAL
from os import getenv, path, listdir, remove, makedirs
from tempfile import gettempdir

# External modules
import dateparser
import msal
import numpy as np
import pandas as pd
import requests

# Climeon modules
try:
    from .identifiers import powerblock, module, hp_system
except ImportError:
    # Expected import error during autosummary documentation import
    from identifiers import powerblock, module, hp_system

# Check for parquet support
try:
    pd.io.parquet.get_engine("auto")
    PARQUET_SUPPORT = True
except ImportError:
    PARQUET_SUPPORT = False

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None

# API details
PROD_URL = "https://api.climeonlive.com/api/v1"
DEV_URL = "https://climeonliveapi-staging.azurewebsites.net/api/v1"

# MSAL settings
CLIENT_ID = "fe8152ab-d22c-4f61-9a24-17bb397bee75"
AUTHORITY = "https://climeonlive.b2clogin.com/climeonlive.onmicrosoft.com/"
POLICY_ROPC = "B2C_1_ropc"
POLICY_SIGN_IN = "B2C_1_SignIn"
AUTHORITY_SIGN_IN = AUTHORITY + POLICY_SIGN_IN
AUTHORITY_ROPC = AUTHORITY + POLICY_ROPC
MSAL_SCOPE = ["https://climeonlive.onmicrosoft.com/backend/read"]
MSAL_TOKEN = ""

# Offline cache settings
BASE_FOLDER = getenv("APPDATA", gettempdir())
OFFLINE_FOLDER = path.join(BASE_FOLDER, "ClimeonLive")
OFFLINE_NAME = "%s_%s_%s_%s_%s"
FOLDER_SIZE_LIMIT = 2*1024*1024*1024

# TSI globals
TSI_TYPES = []
TSI_INSTANCES = []

# Analytics max interval default settings
MAX_RESULTS = 10000
MAX_ERROR = MAX_RESULTS * 10
SQL_INTERVALS = {
    "PT1S": 1,
    "PT10S": 10,
    "PT1M": 60,
    "PT10M": 600,
    "PT1H": 3600,
    "PT12H": 43200,
    "PT24H": 86400
}
MAX_SQL_INTERVALS = {k: v * MAX_RESULTS for k, v in SQL_INTERVALS.items()}
TSI_MAX_RANGE = 31 # days
TSI_INTERVALS = [1, 2, 5, 10, 12, 15, 20]

AUTH_FAIL = "AuthenticationFailed"

class Client():
    """Climeon API client.

        Parameters:
            user (str): User mail to login with. If not supplied it will
                        be fetched from environment variable ``API_USER``, if
                        not set the user will be promted via Azure B2C.
            passwd (str): User password. If not supplied it will be
                          fetched from environment variable ``API_PASS``,
                          if not set the user will be promted via Azure B2C.
            prod (bool): Boolean indicating if the production or development
                         API should be used. Defaults to ``True``.
            plotly (bool): Boolean indicating if plotting library should be
                           set to plotly. Defaults to ``True``.
    """
    # pylint: disable=too-many-public-methods

    def __init__(self, user=None, passwd=None, prod=True, plotly=True):
        self.logger = getLogger(__name__)
        self.user = user or getenv("API_USER")
        self.passwd = passwd or getenv("API_PASS")
        self.url = PROD_URL if prod else DEV_URL
        self.session = requests.Session()
        ropc = self.user and self.passwd
        authority = AUTHORITY_ROPC if ropc else AUTHORITY_SIGN_IN
        self.app = msal.PublicClientApplication(CLIENT_ID,
                                                authority=authority,
                                                validate_authority=False)
        if plotly:
            pd.options.plotting.backend = "plotly"
        if MSAL_TOKEN:
            self.headers = {"authorization": MSAL_TOKEN}
        else:
            self.headers = {"authorization": ""}
            self.login()

    def login(self):
        """Logs in the user to Climeon API."""
        global MSAL_TOKEN # pylint: disable=global-statement
        result = None
        if self.user and self.passwd:
            self.logger.debug("Logging in with user %s", self.user)
            result = self.app.acquire_token_by_username_password(self.user,
                                                                 self.passwd,
                                                                 MSAL_SCOPE)
        else:
            self.logger.debug("Silent login")
            accounts = self.app.get_accounts()
            account = accounts[0] if accounts else None
            result = self.app.acquire_token_silent(MSAL_SCOPE, account=account)
        if not result:
            self.logger.debug("Interactive login")
            try:
                disable(CRITICAL) # Disable logging
                result = self.app.acquire_token_interactive(
                    MSAL_SCOPE,
                    auth_uri_callback=auth_uri_callback
                )
                disable(0) # Enable logging again
            except Exception: # pylint: disable=broad-except
                disable(0) # Enable logging again
                self.fallback_login()
                return
        if "error" in result:
            raise Exception(result["error_description"])
        token = result["access_token"]
        auth = f"Bearer {token}"
        MSAL_TOKEN = auth
        self.headers = {"authorization": auth}

    def fallback_login(self):
        """Fallback in case interactive MSAL login can't be used."""
        self.logger.warning("Falling back on python input")
        self.user = input("Climeon live user email: ")
        self.passwd = getpass("Password: ")
        self.app = msal.PublicClientApplication(CLIENT_ID,
                                                authority=AUTHORITY_ROPC,
                                                validate_authority=False)
        self.login()

    def _http(self, method, endpoint, body, retry):
        headers = self.headers
        if body:
            headers["Content-Type"] = "application/json-patch+json"
            headers["accept"] = "text/plain"
        res = self.session.request(method, endpoint, headers=headers, data=body)
        auth_fail = res.text.startswith(AUTH_FAIL) or res.status_code == 401
        if auth_fail and retry:
            self.login()
            return self._http(method, endpoint, body, False)
        if not res.ok:
            raise Exception(res.text)
        return res

    def get(self, endpoint):
        """General purpose GET method."""
        req_url = self.url + endpoint
        return self._http("GET", req_url, None, True)

    def post(self, endpoint, body):
        """General purpose POST method."""
        req_url = self.url + endpoint
        json_body = json.dumps(body)
        return self._http("POST", req_url, json_body, True)


    # Analytics

    def analytics(self, machine_id, date_from, date_to, variables=None, interval=None):
        """Get aggregated logfile data from the Analytics database.

        Parameters:
            machine_id (str): Module or powerblock id e.g. "0100000016".
            date_from (str, datetime): Datetime to get data from.
            date_to (str, datetime): Datetime to get data to.
            variables (list, optional): Variables to get. Defaults to all
                                        available variables.
            interval (str, optional): Interval size specified in ISO-8601
                                      duration format:
                                      https://en.wikipedia.org/wiki/ISO_8601
                                      Defaults to a reasonable interval.
                                      Can be any of
                                      ``"PT1S", "PT10S", "PT1M", "PT10M", "PT1H", "PT12H", "PT24H"``

        Returns:
            DataFrame: A Pandas DataFrame.
        """
        # pylint: disable=too-many-arguments,too-many-locals
        date_from = parse_datetime(date_from)
        date_to = parse_datetime(date_to)
        if date_to < date_from:
            raise ValueError("Start date must be earlier than end date.")
        interval = interval or default_sql_interval(date_from, date_to)
        if interval not in SQL_INTERVALS:
            raise ValueError("Interval must be one of %s" % list(SQL_INTERVALS.keys()))
        filename = offline_name(machine_id, date_from, date_to, variables, interval)
        dataframe = load_dataframe(filename)
        if not dataframe is None:
            return dataframe
        estimated_result = (date_to - date_from).total_seconds() / SQL_INTERVALS[interval]
        if estimated_result > MAX_ERROR:
            error_text = "Chosen interval %s would request too large of a " \
                         "dataset (%d rows). Increase interval or decrease " \
                         "timerange. Maximum amount of rows to return is %d." \
                         % (interval, int(estimated_result), MAX_ERROR)
            raise ValueError(error_text)
        variables = variables or self.analytics_variables(machine_id)
        body = {
            "searchSpan": {
                "from": date_iso_utc(date_from),
                "to": date_iso_utc(date_to)
            },
            "interval": interval,
            "parameters": [{
                "id": machine_id,
                "variables": variables
            }]
        }
        response = self.post("/Analytics", body)
        raw_data = response.json()
        dataframe = json_to_dataframe(raw_data[machine_id])
        if dataframe.empty:
            self.logger.warning("No data found for %s between %s and %s",
                                machine_id, date_from, date_to)
            return dataframe
        dataframe = format_dataframe(dataframe, date_from.tzinfo, False)
        if len(dataframe.index) > 1:
            rec_int = (dataframe.index[1] - dataframe.index[0]).total_seconds()
        else:
            rec_int = SQL_INTERVALS[interval]
        if SQL_INTERVALS[interval] < rec_int:
            int_str = next((i for i, v in SQL_INTERVALS.items() if v >= rec_int), "PT24H")
            self.logger.warning("Requested interval %s could not be fetched, "
                                "got interval %s instead. Use logfile data to "
                                "get higher resolution.", interval, int_str)
        else:
            int_str = interval
        pandas_interval = int_str[2:].replace("M", "T")
        dataframe = dataframe.resample(pandas_interval).first()
        save_dataframe(dataframe, filename)
        return dataframe

    def analytics_variables(self, machine_id):
        """Get all available variables for a machine."""
        endpoint = f"/Analytics/variables/{machine_id}"
        response = self.get(endpoint)
        return response.json()

    def tsi_query(self, machine_id, date_from, date_to, variables, interval=None):
        """Query the TSI database.

        More info at: https://docs.microsoft.com/en-us/rest/api/time-series-insights/

        Parameters:
            machine_id (str): module or powerblock id e.g. "0100000016".
            date_from (datetime): Datetime to get data from.
            date_to (datetime): Datetime to get data to.
            variables (dict): Variables on TSX syntax.
            interval (str, optional): Interval size specified in ISO-8601
                                      duration format:
                                      https://en.wikipedia.org/wiki/ISO_8601
                                      Defaults to a reasonable interval.

        Returns:
            DataFrame: A Pandas DataFrame.
        """
        #pylint: disable=too-many-arguments
        interval = interval or default_sql_interval(date_from, date_to)
        series_type = "getSeries" if interval == "PT1M" else "aggregateSeries"
        body = {
            series_type: {
                "timeSeriesId": [
                    machine_id
                ],
                "searchSpan": {
                    "from": tsi_utc(date_from),
                    "to": tsi_utc(date_to)
                },
                "inlineVariables": variables,
                "interval": interval,
                "projectedVariables": list(variables.keys())
            }
        }
        response = self.post("/Analytics/tsi/query", body)
        raw_data = response.json()
        if "error" in raw_data:
            raise Exception(raw_data["error"]["message"])
        dataframe = json_to_dataframe(raw_data[machine_id])
        dataframe = format_dataframe(dataframe, date_from.tzinfo)
        return dataframe

    def tsi_types(self):
        """Get all defined TSI types"""
        response = self.get("/Analytics/tsi/types")
        return response.json()["types"]

    def tsi_instances(self):
        """Get all defined TSI instances"""
        response = self.get("/Analytics/tsi/instances")
        return response.json()["instances"]

    def telemetry(self, machine_id, date_from, date_to, variables=None, interval=None):
        """Get telemetry data from the TSI database.

        Parameters:
            machine_id (str): module or powerblock id e.g. "0100000016".
            date_from (str, datetime): Datetime to get data from.
            date_to (str, datetime): Datetime to get data to.
            variables (list, optional): List of variables to fetch. Defaults to
                                        all available.
            interval (str, optional): Interval size specified in ISO-8601
                                      duration format:
                                      https://en.wikipedia.org/wiki/ISO_8601
                                      Defaults to a reasonable interval.
        Returns:
            DataFrame: A Pandas DataFrame.
        """
        #pylint: disable=too-many-arguments
        global TSI_INSTANCES, TSI_TYPES # pylint: disable=global-statement
        date_from = parse_datetime(date_from)
        date_to = parse_datetime(date_to)
        if date_to < date_from:
            raise ValueError("Start date must be earlier than end date.")
        if date_from < datetime.now(timezone.utc) - timedelta(days=TSI_MAX_RANGE+1):
            error_text = "Date %s is too far back for telemetry data. " \
                         "Maximum range back is %s days." % (date_from, TSI_MAX_RANGE)
            raise ValueError(error_text)
        instances = TSI_INSTANCES or self.tsi_instances()
        types = TSI_TYPES or self.tsi_types()
        if not TSI_INSTANCES or not TSI_TYPES:
            TSI_INSTANCES = instances
            TSI_TYPES = types
        instance = next((i for i in instances if i["timeSeriesId"][0] == machine_id), None)
        instance_type = next((t for t in types if t["id"] == instance["typeId"]))
        if variables is None:
            var = instance_type["variables"]
        else:
            var = {k: v for k, v in instance_type["variables"].items() if k in variables}
        interval = interval or default_tsi_interval(date_from, date_to)
        return self.tsi_query(machine_id, date_from, date_to, var, interval)


    # Config

    def config_query(self, query):
        """Get config history for a specific module/powerblock or config name."""
        endpoint = f"/Config/{query}"
        response = self.get(endpoint)
        return response.json()

    def config_changes(self, machine_id=None):
        """Get config changes for specified machine."""
        endpoint = "/Config/changes"
        if machine_id:
            endpoint += f"/{machine_id}"
        response = self.get(endpoint)
        return response.json()


    # Modules

    def modules(self):
        """Get info for all registered modules."""
        response = self.get("/Modules")
        return response.json()

    def module_info(self, module_id):
        """Get info for a specific module."""
        endpoint = f"/Modules/{module_id}"
        response = self.get(endpoint)
        return response.json()

    def modules_telemetry(self):
        """Get all modules latest telemetry."""
        response = self.get("/Modules/telemetry")
        return response.json()

    def module_telemetry(self, module_id):
        """Get latest module telemetry for a specific module."""
        endpoint = f"/Modules/{module_id}/telemetry/"
        response = self.get(endpoint)
        return response.json()

    def module_alerts(self, module_id):
        """Get current alerts for a specific module."""
        endpoint = f"/Modules/{module_id}/alerts/"
        response = self.get(endpoint)
        return response.json()

    def module_alert_history(self, module_id):
        """Get alert history for a specific module."""
        endpoint = f"/Modules/{module_id}/alertHistory/"
        response = self.get(endpoint)
        return response.json()

    def list_blackbox(self, module_id, date):
        """List all blackbox timestamps for a date."""
        date = parse_datetime(date)
        date_str = date.strftime("%y%m%d")
        endpoint = f"/Modules/{module_id}/data/blackbox/{date_str}"
        try:
            response = self.get(endpoint)
        except Exception: # pylint: disable=broad-except
            return []
        t_s = response.json()
        return [date + timedelta(hours=int(t[0:2]), minutes=int(t[2:])) for t in t_s]

    def blackbox(self, module_id, date):
        """Get blackbox file for a timestamp."""
        date = parse_datetime(date)
        date_str = date.strftime("%y%m%d")
        ts_str = date.strftime("%H%M")
        endpoint = f"/Modules/{module_id}/data/blackbox/{date_str}/{ts_str}"
        response = self.get(endpoint)
        data_str = response.text
        header_idx = data_str.index("Timestamp")
        dataframe = pd.read_csv(StringIO(data_str[header_idx:]))
        dataframe = format_dataframe(dataframe, date.tzinfo)
        return dataframe


    # PowerBlocks

    def powerblocks(self):
        """Get info for all registered powerblocks."""
        response = self.get("/PowerBlocks")
        return response.json()

    def powerblock_info(self, powerblock_id):
        """Get info for a specific powerblock."""
        endpoint = f"/PowerBlocks/{powerblock_id}"
        response = self.get(endpoint)
        return response.json()

    def powerblock_alerts(self, powerblock_id):
        """Get current alerts for a specific powerblock."""
        endpoint = f"/PowerBlocks/{powerblock_id}/alerts/"
        response = self.get(endpoint)
        return response.json()

    def powerblock_alert_history(self, powerblock_id):
        """Get alert history for a specific powerblock."""
        endpoint = f"/PowerBlocks/{powerblock_id}/alertHistory/"
        response = self.get(endpoint)
        return response.json()

    def powerblock_parameters(self, powerblock_id, date):
        """Get parameter file for a specific powerblock and date."""
        date_str = date.strftime("%y%m%d")
        endpoint = f"/PowerBlocks/{powerblock_id}/parameters/{date_str}"
        response = self.get(endpoint)
        return response.text


    # Users

    def users(self):
        """Get info for all registered users."""
        response = self.get("/Users")
        return response.json()


    # SecurityGroups

    def security_groups(self):
        """Get info for all registered security groups."""
        response = self.get("/SecurityGroups")
        return response.json()


    # Helpers

    def logfile_raw(self, machine_id, date):
        """Retrieves log file for a specific module and date."""
        date_str = date.strftime("%y%m%d")
        if module(machine_id):
            endpoint = f"/Modules/{machine_id}/data/{date_str}?unpack=False"
        elif powerblock(machine_id):
            endpoint = f"/PowerBlocks/{machine_id}/data/{date_str}?unpack=False"
        elif machine_id == "0900000001":
            endpoint = f"/Other/backbone/data/{date_str}?unpack=False"
        elif hp_system(machine_id):
            endpoint = f"/HPSystems/{machine_id}/data/{date_str}?unpack=False"
        else:
            error = f"Bad id supplied {machine_id}"
            raise ValueError(error)
        response = self.get(endpoint)
        try:
            return lzma.decompress(response.content).decode("utf-8")
        except lzma.LZMAError:
            return response.text

    def download_logfile(self, machine_id, date, directory="."):
        """Download a logfile to disk."""
        date_str = date.strftime("%y%m%d")
        log_file = self.logfile_raw(machine_id, date)
        log_path = f"{directory}/{machine_id}_{date_str}.csv"
        with open(log_path, mode="w+", encoding="utf-8") as file_stream:
            file_stream.write(log_file)
        return log_path

    def logfile(self, machine_id, date_from, date_to=None, variables=None):
        """Get logfile for a machine/date.

        Parameters:
            machine_id (str): module or powerblock id e.g. "0100000016".
            date_from (str, datetime): Datetime to get data from.
            date_to (str, datetime, optional): Datetime to get data to.
            variables (list, optional): List of strings with variable names.
                                        Defaults to all available variables.
                                        Any other variables will be dropped.
                                        Useful if a long timerange is used to
                                        not exhaust memory.

        Returns:
            DataFrame: A Pandas DataFrame.
        """
        date_from = parse_datetime(date_from)
        date_to = parse_datetime(date_to)
        if date_to is None or date_to.date() == date_from.date():
            date_to = date_from + timedelta(days=1)
        if date_to.date() < date_from.date():
            raise ValueError("Start date must be earlier than end date.")
        filename = offline_name(machine_id, date_from.date(), date_to.date(),
                                variables, "")
        dataframe = load_dataframe(filename)
        if not dataframe is None:
            return dataframe
        if variables is not None:
            variables = list(set(variables + ["Timestamp", "Timestamp UTC [-]"]))
        diff = date_to - date_from
        date_list = [date_from + timedelta(days=d) for d in range(diff.days)]
        for date in date_list:
            try:
                data_str = self.logfile_raw(machine_id, date)
            except Exception: # pylint: disable=broad-except
                self.logger.warning("No logfile found for %s on date %s",
                                    machine_id, date.date())
                continue
            header_idx = data_str.index("Timestamp")
            dateframe = pd.read_csv(StringIO(data_str[header_idx:]))
            if variables:
                drop_var = [c for c in dateframe.columns if c not in variables]
                dateframe = dateframe.drop(drop_var, axis=1)
            dateframe = format_dataframe(dateframe, date_from.tzinfo)
            if dataframe is None:
                dataframe = dateframe
            else:
                dataframe = pd.concat([dataframe, dateframe])
        if dataframe is not None:
            save_dataframe(dataframe, filename)
        return dataframe

    def get_machines(self):
        """Get all registered modules/powerblocks."""
        powerblocks = self.powerblocks()
        machines = [m["moduleId"] for p in powerblocks for m in p["modules"]]
        machines.extend([p["powerBlockId"] for p in powerblocks])
        machines.sort()
        return machines

def offline_name(machine_id, date_from, date_to, variables, interval):
    """Get offline name for log data."""
    var = "".join(c for c in variables) if variables else ""
    name_raw = OFFLINE_NAME % (machine_id, date_from, date_to, var, interval)
    filename = sha1(bytes(name_raw, "utf-8")).hexdigest()
    return path.join(OFFLINE_FOLDER, filename)

def save_dataframe(dataframe, filename):
    """Save dataframe to disk. Tries both parquet and pickle."""
    if not path.exists(OFFLINE_FOLDER):
        makedirs(OFFLINE_FOLDER)
    files = listdir(OFFLINE_FOLDER)
    folder_size = sum(path.getsize(f) for f in files if path.isfile(f))
    if folder_size > FOLDER_SIZE_LIMIT:
        oldest_file = min(files, key=path.getctime)
        remove(oldest_file)
    if PARQUET_SUPPORT:
        dataframe.to_parquet(filename + ".parquet")
    else:
        dataframe.to_pickle(filename + ".pickle")

def load_dataframe(filename):
    """Load a dataframe from disk. Tries both parquet and pickle."""
    if path.exists(filename + ".parquet") and PARQUET_SUPPORT:
        return pd.read_parquet(filename + ".parquet")
    if path.exists(filename + ".pickle"):
        return pd.read_pickle(filename + ".pickle")
    return None

def parse_datetime(date_str):
    """Parse a datetime string."""
    date = None
    if date_str is None:
        return date_str
    if isinstance(date_str, str):
        date = dateparser.parse(date_str)
    if date is None:
        date = pd.to_datetime(date_str).to_pydatetime()
    if date.tzinfo is None:
        # Timezone naive, use locale
        date = date.astimezone()
    return date

def tsi_utc(date):
    """Convert a date to a format that TSI can use."""
    return date_iso_utc(date).replace("+00:00", "Z")

def date_iso_utc(date):
    """Convert date to timezone aware, UTC, ISO formatted string."""
    return date.astimezone(timezone.utc).isoformat()

def json_to_dataframe(raw_data):
    """Convert raw json data to a dataframe."""
    columns = [p["name"] for p in raw_data["properties"]]
    columns.insert(0, "Timestamp")
    data = [p["values"] for p in raw_data["properties"]]
    data.insert(0, raw_data["timestamps"])
    data = list(map(list, zip(*data)))
    dataframe = pd.DataFrame(data, columns=columns)
    return dataframe

def format_dataframe(dataframe, original_tz, resample=True):
    """Clean up and properly timestamp dataframe."""
    dataframe = dataframe.loc[:, ~dataframe.columns.str.contains("^Unnamed")]
    ts_1 = parse_datetime(dataframe["Timestamp"][0])
    ts_2 = parse_datetime(dataframe["Timestamp"][1]) if len(dataframe.index) > 1 else None
    if ts_2 is not None and ts_2 - ts_1 < timedelta(seconds=0.5):
        # Blackbox file, need to use Timestamp column to maintain resolution
        utc_1 = parse_datetime(dataframe["Timestamp UTC [-]"][0])
        utc_offset = ts_1 - utc_1
        dataframe["Timestamp"] = pd.to_datetime(dataframe["Timestamp"])
        dataframe["Timestamp"] = dataframe["Timestamp"] + utc_offset
    elif "Timestamp UTC [-]" in dataframe:
        dataframe["Timestamp"] = pd.to_datetime(dataframe["Timestamp UTC [-]"],
                                                utc=True)
    else:
        dataframe["Timestamp"] = pd.to_datetime(dataframe["Timestamp"])
    dataframe = dataframe.set_index("Timestamp")
    if dataframe.index.tz is None:
        dataframe.index = dataframe.index.tz_localize(timezone.utc)
    dataframe.index = dataframe.index.tz_convert(original_tz)
    dataframe.fillna(value=np.nan, inplace=True)
    dataframe.replace(-32768, np.nan, inplace=True)
    if resample:
        # Add missing timestamps as NaN
        dataframe = dataframe.resample("1S").first()
    return dataframe

def default_sql_interval(date_from, date_to):
    """Figure out a reasonable interval for a time range."""
    diff = (date_to - date_from).total_seconds()
    for interval, max_result in MAX_SQL_INTERVALS.items():
        if diff < max_result:
            return interval
    raise ValueError("Could not find a valid interval for this range.")

def default_tsi_interval(date_from, date_to):
    """Figure out a reasonable TSI interval between two datetimes."""
    diff_seconds = (date_to - date_from).total_seconds()
    interval = next(i for i in TSI_INTERVALS if diff_seconds/(60 * i) < MAX_RESULTS)
    return "PT%dM" % interval

def auth_uri_callback(_):
    """Called if interactive login fails."""
    raise Exception("Could not launch browser")
