import argparse
import os
import re
from datetime import date, datetime, timedelta
from tkinter import filedialog
from typing import Any, Dict, List, Tuple, Type

from pyodbc import Connection, Cursor, connect
from .records import (RECORD_TYPES, STROKES,
                                      IndividualEventRecord,
                                      IndividualInformationRecord, MeetRecord,
                                      RelayEventRecord, RelayNameRecord,
                                      SplitsRecord, TeamIDRecord)
from .time import Time


RESULT_TYPES = {
    "p": "Prelims",
    "s": "Swim-Off",
    "f": "Finals"
}


GENDERS_BG = {
    "m": "Boys",
    "f": "Girls"
}


class Result:
    time: Time
    course: str
    type: str
    splits: Dict[int, Time]
    split_distance: int
    rank: int
    points: float
    is_dq: bool
    dq_code: int
    is_dfs: bool

    def __init__(self, time:Time=None, time_str:str=None,
                 type:str=None, course:str=None, splits=[],
                 split_distance=None, rank:int=None, points:float=None,
                 is_dq:bool=False, dq_code:int=None, is_dfs:bool=False) -> None:
        if time is not None:
            self.time = time
        elif time_str is not None:
            self.time = Time(time_str)
        
        if type is not None:
            self.type = type

        if course is not None:
            self.course = course

        if rank is not None:
            self.rank = int(rank)
        
        if points is not None:
            self.points = float(points)
        
        self.splits = {}

        self.is_dq = is_dq
        self.is_dfs = is_dfs

        if dq_code is not None:
            self.dq_code = dq_code
        

    def __repr__(self) -> str:
        return f"{self.time}"

    def __eq__(self, __o: object) -> bool:
        if type(__o) is not Result:
            raise TypeError("Result object not equatable to objects of other types.")

        if self.time != __o.time:
            return False
        if hasattr(self, "course") and self.course != __o.course:
            return False
        if hasattr(self, "split_distance") and self.split_distance != __o.split_distance:
            return False
        if hasattr(self, "splits") and self.splits != __o.splits:
            return False
        if hasattr(self, "rank") and self.rank != __o.rank:
            return False
        if hasattr(self, "points") and self.points != __o.points:
            return False
        
        return True


class Seed:
    time: Time
    course: str
    heat: int
    lane: int
    rank: int

    def __init__(self, time:Time=None, time_str:str=None, course:str=None, heat:int=None, lane:int=None, rank:bool=None) -> None:
        if time is not None:
            self.time = time
        elif time_str is not None:
            self.time = Time(time_str)

        if course is not None:
            self.course = course

        if heat is not None:
            self.heat = int(heat)

        if lane is not None:
            self.lane = int(lane)

        if rank is not None:
            self.rank = int(rank)

    def __repr__(self) -> str:
        return f"{self.time}"

    def __eq__(self, __o: object) -> bool:
        if type(__o) is not Seed:
            return TypeError("Seed object not equatable to obejcts of other types.")

        if self.time != __o.time:
            return False
        if hasattr(self, "course") and self.course != __o.course:
            return False
        
        return True
        

class AgeGroup:
    lower_age: int
    upper_age: int

    def __init__(self, lower_age:int, upper_age:int) -> None:
        self.lower_age = lower_age
        self.upper_age = upper_age

    def __repr__(self) -> str:
        if self.lower_age > 0 and self.upper_age < 100:
            return f"{self.lower_age}-{self.upper_age}"
        elif self.lower_age <= 0 and self.upper_age < 100:
            return f"{self.upper_age} & Under"
        elif self.lower_age > 0 and self.upper_age >= 100:
            return f"{self.lower_age} & Over"
        else:
            return "Open"


class Event:
    number: int
    letter: str
    distance: int
    stroke: str
    age_group: AgeGroup
    gender: str
    is_relay: bool

    def __init__(self, number:int, letter:str, distance:int|str|float, stroke:str, age_group:AgeGroup, gender:str, is_relay:bool=False) -> None:
        self.number = number
        self.letter = letter
        if type(distance) is str or type(distance) is float:
            self.distance = int(distance)
        elif type(distance) is int:
            self.distance = distance
        self.stroke= stroke
        self.age_group = age_group
        self.gender = gender.lower()
        self.is_relay = is_relay

    def __repr__(self) -> str:
        relay = " Relay" if self.is_relay else ""
        return f"{GENDERS_BG[self.gender]} {self.age_group} {self.distance} {self.stroke}{relay}"


def calculate_usas_id(first_name: str, middle_name: str, last_name: str, birthday: date):
    """Calculates the USA Swimming ID for the given values. i.e. Thomas Andrew Smith, 05/11/00 => 051100THOASMIT."""

    def format(string: str, num_chars: int):
        return re.sub(r"\W", "", string)[0:num_chars].ljust(num_chars,"*").upper()

    bd = birthday.strftime("%m%d%y")
    first = format(first_name, 3)
    middle = format(middle_name, 1)
    last = format(last_name, 4)

    return f"{bd}{first}{middle}{last}"


class Swimmer:
    first_name: str
    pref_name: str
    middle_name: str
    last_name: str
    birthday: str
    age: int
    gender: str
    desync_id: str

    def __init__(self, full_name: str, age: int|str = None, birthday:str = None, pref_name: str = None, gender: str = None, id: str = None) -> None:
        name = parse_name(full_name)
        self.first_name = name["first_name"]
        if "middle_name" in name.keys():
            self.middle_name = name["middle_name"]
        else:
            self.middle_name = ""
        self.last_name = name["last_name"]

        if type(age) is str:
            self.age = int(age)
        elif type(age) is int:
            self.age = age
        
        if birthday is not None:
            self.birthday = birthday

        if gender is not None:
            self.gender = gender.lower()

        if pref_name is not None:
            self.pref_name = pref_name

        if id is not None:
            id = id.upper()
            if self.middle_name == "" and id[9:10] != "*":
                self.middle_name = id[9:10]
            
            if id != self.id:
                self.desync_id = id
                print(f"For swimmer: {full_name} USAS ID does not match given name and birthday. Given: {id}, Calculated: {self.id}")

    @property
    def id(self):
        try:
            return calculate_usas_id(
                first_name=self.first_name,
                middle_name=self.middle_name,
                last_name=self.last_name,
                birthday=self.birthday
            )
        except:
            print(f"Swimmer: {self.last_name}, {self.first_name} {self.middle_name} ")
            return ""

    def __repr__(self) -> str:
        return self.full_pref_name

    @property
    def full_name(self):
        if hasattr(self, "middle_name"):
            return f"{self.last_name}, {self.first_name} {self.middle_name}"
        else:
            return f"{self.last_name}, {self.first_name}"

    @property
    def full_pref_name(self):
        first = self.pref_name if hasattr(self, "pref_name") else self.first_name
        return f"{self.last_name}, {first}"

class IndividualEntry:
    event: Event
    swimmer: Swimmer
    seeds: Dict[str, Seed]
    """Seeds keyed by event round character:
    'p': Prelims
    's': Swim Off
    'f': Finals"""
    results: Dict[str, Result]
    """Results keyed by event round character:
    'p': Prelims
    's': Swim Off
    'f': Finals"""

    def __init__(self) -> None:
        self.seeds = {}
        self.results = {}

    def __repr__(self) -> str:
        return f"{self.swimmer} - {self.event}"

class RelayEntry:
    event: Event
    identifier: str
    swimmers: Dict[str, Dict[int,Swimmer]]
    """Swimmers keyed by relay order"""
    seeds: Dict[str, Seed]
    results: Dict[str, Result]

    def __init__(self) -> None:
        self.swimmers = {}
        self.seeds = {}
        self.results = {}

    def __repr__(self) -> str:
        return f"{self.event} - {self.identifier}"

class Team:
    name: str
    code: str
    lsc: str
    swimmers: Dict[str, Swimmer]
    """Swimmers keyed by USAS Id Number"""

    @property
    def points(self) -> float:
        individual_points = [entry.results["f"].points for entry in self.entries if "f" in entry.results and hasattr(entry.results["f"], "points")]
        ind_total = sum(individual_points)
        relay_points = [relay.results["f"].points for relay in self.relays if "f" in relay.results and hasattr(relay.results["f"], "points")]
        relay_total = sum(relay_points)
        total = ind_total + relay_total
        return total


    def __init__(self, name, code, lsc) -> None:
        self.name = name
        self.code = code
        self.lsc = lsc
        self.swimmers = {}
        self.entries = []
        self.relays = []

    def __repr__(self) -> str:
        return f"{self.name}"

class Session:
    name: str
    number: int
    letter: str
    start: datetime
    events: Dict[int, Event]
    """Events keyed by numerical order within session"""
    course: str

    def __init__(self, name, number, letter, start, course) -> None:
        self.name = name
        self.number = number
        self.letter = letter
        self.start = start
        self.course = course
        self.events = {}

    def __repr__(self) -> str:
        return self.name

class Facility:
    name: str
    address1: str
    address2: str
    city: str
    state: str
    zip: str

    def __init__(self, name, address1=None, address2=None, city=None, state=None, zip=None) -> None:
        self.name = name
        if address1 is not None:
            self.address1 = address1
        if address2 is not None:
            self.address2 = address2
        if city is not None:
            self.city = city
        if state is not None:
            self.state = state
        if zip is not None:
            self.zip = zip

    def __repr__(self) -> str:
        return f"{self.name}"

class Meet:
    name: str
    facility: Facility
    start_date: date
    end_date: date
    sessions: Dict[Tuple[int,str], Session]
    """Session keyed by:
    
    (Session.number, Session.letter)"""
    events: Dict[Tuple[int,str], Event]
    """Events keyed by:
    
    (Event.number, Event.letter)"""
    rounds: Dict[Tuple[int,str,int,str,str], Event]
    """Session/Event relationships. Events keyed by:
    
    (Session.number, Session.letter, Event.number, Event.letter, round_type)
    
    round_type:
    'p': Prelims
    's': Swim Off
    'f': Finals"""
    teams: Dict[str, Team]
    """Teams keyed by:
    
    (Team.code, Team.lsc)"""
    swimmers: Dict[Tuple[str, str], Swimmer]
    """Swimmers keyed by:
    
    (Swimmer.id, Team.code)"""
    entries: Dict[Tuple[int,str,str], IndividualEntry]
    """Individual Entries keyed by:
    
    (Event.number, Event.letter, Swimmer.id)"""
    relays: Dict[Tuple[str,str,str], RelayEntry]
    """Relay Entries keyed by:
    
    (Event.number, Event.letter, Team.code, RelayEntry.identifier)"""

    def __init__(self) -> None:
        self.sessions = {}
        self.events = {}
        self.rounds = {}
        self.teams = {}
        self.swimmers = {}
        self.entries = {}
        self.relays = {}

    def __repr__(self) -> str:
        return self.name


def parse_name(name: str):
    m = re.match(r"^(?P<last_name>.*), (?P<first_name>.*) (?P<middle_name>[A-Z])$", name)
    if m is not None:
        return m.groupdict()

    m = re.match(r"^(?P<last_name>.*), (?P<first_name>.*)$", name)
    if m is not None:
        return m.groupdict()

    raise ValueError("Name not properly formatted")   
    

def read_cl2(input):
    """Read .cl2 file into Meet object"""
    if type(input) is str:
        lines = input.split("\n")
    elif type(input) is list:
        lines = input
    elif type(input) is bytes:
        lines = input.decode("utf-8").split("\n")

    output = []

    for line in lines:
        code = line[0:2]
        
        if code in RECORD_TYPES.keys():
            output.append(RECORD_TYPES[code](line))
    
    output = tuple(output)

    meetRecord = next(record for record in output if type(record) is MeetRecord)

    meet = Meet()
    meet.name = meetRecord.name

    active_team: Team = None
    active_swimmer: Swimmer = None
    active_entry: IndividualEntry|RelayEntry = None
    splits = None

    for active_record in output:
        
        if type(active_record) is TeamIDRecord:
            active_team = Team(name=active_record.team_name, code=active_record.team_code, lsc=active_record.lsc_code)
            meet.teams[active_team.code] = active_team

        elif type(active_record) is IndividualEventRecord:
            if active_swimmer is None or active_record.swimmer_name != active_swimmer.full_name:
                active_swimmer = Swimmer(full_name=active_record.swimmer_name, age=active_record.swimmer_age, birthday=active_record.swimmer_birthday, gender=active_record.swimmer_sex)

                if active_swimmer.id in active_team.swimmers:
                    active_swimmer = active_team.swimmers[active_swimmer.id]
                else:
                    active_team.swimmers[active_swimmer.id] = active_swimmer
            
            active_entry = IndividualEntry()
            active_entry.swimmer = active_swimmer
            active_team.entries.append(active_entry)

            if active_record.event_str in meet.events:
                event = meet.events[active_record.event_str]
            else:
                number = active_record.event_number
                distance = int(active_record.event_distance)
                stroke = STROKES[active_record.event_stroke]
                lower = 0 if active_record.event_lower_age == "UN" else int(active_record.event_lower_age)
                upper = 100 if active_record.event_upper_age == "OV" else int(active_record.event_upper_age)
                age_group = AgeGroup(lower, upper)
                gender = active_record.event_sex.lower()
                event = Event(number, distance, stroke, age_group, gender)
                meet.events[event.number] = event
            active_entry.event = event

            if hasattr(active_record, "seed_time") and active_record.seed_time != "NS" and active_record.seed_time != "DQ":
                if hasattr(active_record, "prelim_heat") and hasattr(active_record, "prelim_lane"):
                    active_entry.seeds["p"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.prelim_heat, lane=active_record.prelim_lane)
                elif hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    active_entry.seeds["f"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.final_heat, lane=active_record.final_lane)  

            if hasattr(active_record, "prelim_time") and active_record.prelim_time != "NS" and active_record.prelim_time != "DQ": 
                active_entry.results["p"] = Result(type="p", rank=active_record.prelim_rank, time_str=active_record.prelim_time, course=active_record.prelim_course)
                if hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    if hasattr(active_record, "swimoff_time"):
                        # Small bug here... who won the swimoff? and how do we determine rank?
                        active_entry.seeds["f"] = Seed(time_str=active_record.swimoff_time, rank=active_record.prelim_rank, course=active_record.swimoff_course, heat=active_record.final_heat, lane=active_record.final_lane)       
                    else:
                        active_entry.seeds["f"] = Seed(time_str=active_record.prelim_time, rank=active_record.prelim_rank, course=active_record.prelim_course, heat=active_record.final_heat, lane=active_record.final_lane)       
      
            if hasattr(active_record, "final_time") and active_record.final_time != "NS" and active_record.final_time != "DQ":
                points = active_record.points if hasattr(active_record, "points") else None
                active_entry.results["f"] = Result(type="f", rank=active_record.final_rank, points=points, time_str=active_record.final_time, course=active_record.final_course )

        elif type(active_record) is IndividualInformationRecord:
            if hasattr(active_record, "pref_name"):
                active_swimmer.pref_name = active_record.pref_name

        elif type(active_record) is RelayEventRecord:
            active_entry = RelayEntry()
            active_entry.identifier = active_record.relay_id
            active_team.relays.append(active_entry)

            if active_record.event_str in meet.events:
                event = meet.events[active_record.event_str]
            else:
                number = active_record.event_number
                distance = int(active_record.event_distance)
                stroke = STROKES[active_record.event_stroke]
                lower = 0 if active_record.event_lower_age == "UN" else int(active_record.event_lower_age)
                upper = 100 if active_record.event_upper_age == "OV" else int(active_record.event_upper_age)
                age_group = AgeGroup(lower, upper)
                gender = active_record.event_sex.lower()
                event = Event(number, distance, stroke, age_group, gender)
                meet.events[event.number] = event
            active_entry.event = event
            
            if hasattr(active_record, "seed_time"):
                if hasattr(active_record, "prelim_heat") and hasattr(active_record, "prelim_lane"):
                    active_entry.seeds["p"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.prelim_heat, lane=active_record.prelim_lane)
                elif hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    active_entry.seeds["f"] = Seed(time_str=active_record.seed_time, course=active_record.seed_course, heat=active_record.final_heat, lane=active_record.final_lane)

            if hasattr(active_record, "prelim_time") and active_record.prelim_time != "NS" and active_record.prelim_time != "DQ":
                active_entry.results["p"] = Result(type="p", rank=active_record.prelim_rank, time_str=active_record.prelim_time, course=active_record.prelim_course)
                # TODO: Add swimoff functionality
                if hasattr(active_record, "final_heat") and hasattr(active_record, "final_lane"):
                    active_entry.seeds["f"] = Seed(time_str=active_record.prelim_time, rank=active_record.prelim_rank, course=active_record.prelim_course, heat=active_record.final_heat, lane=active_record.final_lane)
            
            if hasattr(active_record, "final_time") and active_record.final_time != "NS" and active_record.final_time != "DQ":
                points = active_record.points if hasattr(active_record, "points") else None
                active_entry.results["f"]= Result(type="f", rank=active_record.final_rank, points=points, time_str=active_record.final_time, course=active_record.final_course)

        elif type(active_record) is RelayNameRecord:
            active_swimmer = Swimmer(full_name=active_record.swimmer_name, birthday=active_record.swimmer_birthday, age=active_record.swimmer_birthdate)
            if active_swimmer.id in active_team.swimmers:
                active_swimmer = active_team.swimmers[active_swimmer.id]
            
            active_entry.swimmers.append(active_swimmer)
        
        elif type(active_record) is SplitsRecord:
            try:
                splits = active_entry.results[active_record.swim_code.lower()].splits
            except:
                splits = []

            for i in range(min(int(active_record.num_splits) - len(splits), 10)):
                if hasattr(active_record, f"time_{i + 1}"):
                    time = getattr(active_record, f"time_{i + 1}")
                    if active_record.swim_code.lower() in active_entry.results:
                        active_entry.results[active_record.swim_code.lower()].splits.append(Time(time)) 

    return meet

_CONDITIONS = {
    lambda _, val: type(val) is str: lambda x: str.rstrip(x),
    lambda key, _: key in [
        "Sess_rnd",
        "Event_round",
        "Rnd_ltr",
    ]: lambda x: str.lower(x),
    lambda key, _: key in [
        "Reg_no",
    ]: lambda x: str.upper(x)
}

def sanitize(key, value):
    for condition in _CONDITIONS:
        if condition(key, value):
            value = _CONDITIONS[condition](value)
    return value

def process_result(cursor: Cursor, query: str) -> Dict[str, Any]:
    cursor.execute(query)
    result = cursor.fetchone()
    columns = [column[0] for column in cursor.description]
    out = dict(zip(columns, result))
    return {key: sanitize(key, out[key]) for key in out}

def process_results(cursor: Cursor, query: str) -> Dict[str, Any]:
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    outs = [dict(zip(columns, result)) for result in results]
    return [{key: sanitize(key, out[key]) for key in out} for out in outs]

def create_entry(props: Dict[str, Any], type: Type) -> IndividualEntry | RelayEntry:
    """Creates an entry object from the properties returned in a valid entry query"""
    entry_obj = type()

    def is_valid(time):
        return time is not None and time != 0

    if is_valid(props["Pre_heat"]):
        if is_valid(props["ActualSeed_time"]):
            seed_time = Time(props["ActualSeed_time"])
        else:
            seed_time = Time(0)

        entry_obj.seeds["p"] = Seed(
            time=seed_time,
            course=props["ActSeed_course"],
            heat=props["Pre_heat"],
            lane=props["Pre_lane"]
        )

    if is_valid(props["Fin_heat"]):
        if is_valid(props["Pre_Time"]):
            seed_time = Time(props["Pre_Time"])
        elif is_valid(props["ActualSeed_time"]):
            seed_time = Time(props["ActualSeed_time"])
        else:
            seed_time = Time(0)

        entry_obj.seeds["f"] = Seed(
            time=seed_time,
            course=props["ActSeed_course"],
            heat=props["Fin_heat"],
            lane=props["Fin_lane"]
        )

    if "p" in entry_obj.seeds:
        prelim_time = Time(0)
        prelim_dq = False
        
        if is_valid(props["Pre_Time"]):
            prelim_time = Time(props["Pre_Time"])

        if hasattr(props, "Pre_stat"):
            prelim_dq = props["Pre_stat"] == "Q"

        entry_obj.results["p"] = Result(
            time=prelim_time,
            type="p",
            course=props["Pre_course"],
            rank=props["Pre_place"],
            is_dq=prelim_dq,
        )
    
    if "f" in entry_obj.seeds:
        final_time = Time(0)
        final_dq = False

        if is_valid(props["Fin_Time"]):
            final_time = Time(props["Fin_Time"])

        if hasattr(props, "Fin_stat"):
            final_dq = props["Fin_stat"] == "Q"
        

        entry_obj.results["f"] = Result(
            time=final_time,
            type="f",
            course=props["Fin_course"],
            rank=props["Fin_place"],
            points=props["Ev_score"],
            is_dq=final_dq,
        )

    return entry_obj

MDB_STROKES = {
    "A": "Free", 
    "B": "Back",
    "C": "Breast",
    "D": "Fly",
    "E": "Medley",
}

def read_mdb(path: str) -> Meet:
    """Reads a MeetManager formatted .mdb file into memory as a Meet object"""
    if not os.path.isfile(path) or not os.path.splitext(path)[1] == ".mdb":
        return
    
    connection_string = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=" + path + ";Uid=Admin;Pwd=TeP69s)lAd_mW-(J_72u"
    connection = connect(connection_string)
    cursor = connection.cursor()

    meet = Meet()
    desync_ids = {}

    # Meet
    query = """
            SELECT
                Meet_name1, Meet_location, Meet_addr1,
                Meet_addr2, Meet_city, Meet_state,
                Meet_zip, Meet_start, Meet_end
            from Meet
            """
    result = process_result(cursor, query)
    meet.name = result["Meet_name1"]
    meet.facility = Facility(
        name=result["Meet_location"],
        address1=result["Meet_addr1"],
        city=result["Meet_city"],
        state=result["Meet_state"],
        zip=result["Meet_zip"],
    )
    meet.start_date = result["Meet_start"]
    meet.end_date = result["Meet_end"]

    # Sessions
    query = """
            SELECT
                Sess_no, Sess_ltr, Sess_name,
                Sess_day, Sess_starttime, Sess_course
            FROM Session
            """
    for result in process_results(cursor, query):
        start_time = meet.start_date + timedelta(days=result["Sess_day"]-1, seconds=result["Sess_starttime"])

        session = Session(
            name=result["Sess_name"],
            number=result["Sess_no"],
            letter=result["Sess_ltr"],
            start=start_time,
            course=result["Sess_course"],
        )

        meet.sessions[result["Sess_no"], result["Sess_ltr"]] = session

    # Events
    query = """
            SELECT
                Event_no, Event_ltr, Event_dist,
                Event_stroke, Low_age, High_age,
                Event_gender, Ind_rel
            FROM Event
            """
    for result in process_results(cursor, query):

        event = Event(
            number=result["Event_no"],
            letter=result["Event_ltr"],
            distance=result["Event_dist"],
            stroke=MDB_STROKES[result["Event_stroke"]],
            age_group=AgeGroup(int(result["Low_age"]),int(result["High_age"])),
            gender=result["Event_gender"],
            is_relay=result["Ind_rel"] == "R"
        )

        meet.events[result["Event_no"], result["Event_ltr"]] = event

    # Session Events
    query = """
            SELECT
                Sess_no, Sess_ltr, Sess_order,
                Sess_rnd, Event_no, Event_ltr
            FROM (Sessitem 
            LEFT JOIN Session ON Sessitem.Sess_ptr = Session.Sess_ptr)
            LEFT JOIN Event on Sessitem.Event_ptr = Event.Event_ptr
            """
    for result in process_results(cursor, query):

        event = meet.events[(
            result["Event_no"],
            result["Event_ltr"],
        )]

        meet.rounds[
            result["Sess_no"],
            result["Sess_ltr"],
            result["Event_no"],
            result["Event_ltr"],
            result["Sess_rnd"],
        ] = event
        meet.sessions[
            result["Sess_no"],
            result["Sess_ltr"],
        ].events[result["Sess_order"]] = (
            result["Sess_rnd"],
            event
        )

    # Teams
    query = """
            SELECT
                Team_name, Team_abbr, Team_lsc
            FROM Team
            """
    for result in process_results(cursor, query):
        team = Team(
            name=result["Team_name"],
            code=result["Team_abbr"],
            lsc=result["Team_lsc"],
        )

        meet.teams[result["Team_abbr"], result["Team_lsc"]] = team

    # Swimmers
    query = """
            SELECT 
                Team_abbr, Team_lsc, Reg_no,
                Last_name, First_name, Initial,
                Pref_name, Birth_date, Ath_sex 
            FROM Athlete 
            LEFT JOIN Team ON Athlete.Team_no = Team.Team_no
            """
    for result in process_results(cursor, query):
        full_name = f"{result['Last_name']}, {result['First_name']} {result['Initial']}"
        pref_name = result["Pref_name"] if result["Pref_name"] != "" else None

        swimmer = Swimmer(
            full_name=full_name,
            pref_name=pref_name,
            birthday=result["Birth_date"],
            gender=result["Ath_sex"],
            id=result["Reg_no"],
        )

        if hasattr(swimmer, "desync_id"):
            desync_ids[swimmer.desync_id] = swimmer.id

        if result["Reg_no"] in desync_ids:
            result["Reg_no"] = desync_ids[result["Reg_no"]]

        meet.swimmers[result["Reg_no"]] = swimmer
        meet.teams[result["Team_abbr"], result["Team_lsc"]].swimmers[result["Reg_no"]] = swimmer

    # Individual Entries/Results
    query = """
            SELECT
                ActualSeed_time, ActSeed_course, Pre_heat,
                Pre_lane, Pre_Time, Pre_course,
                Pre_stat, Pre_place, Fin_heat,
                Fin_lane, Fin_Time, Fin_course, Fin_stat,
                Fin_place, fin_dqofficial, Ev_score,
                Reg_no, Team_abbr, Team_lsc,
                Event_no, Event_ltr
            FROM ((Entry
            LEFT JOIN Athlete ON Entry.Ath_no = Athlete.Ath_no)
            LEFT JOIN Team ON Athlete.Team_no = Team.Team_no)
            LEFT JOIN Event ON Entry.Event_ptr = Event.Event_ptr
            """
    for result in process_results(cursor, query):

        if result["Reg_no"] in desync_ids:
            result["Reg_no"] = desync_ids[result["Reg_no"]]

        entry = create_entry(result, IndividualEntry)
        entry.event = meet.events[result["Event_no"], result["Event_ltr"]]
        entry.swimmer = meet.teams[result["Team_abbr"], result["Team_lsc"]].swimmers[result["Reg_no"]]

        meet.entries[result["Event_no"],result["Event_ltr"],result["Reg_no"]] = entry

    # Relay Entries/Results
    query = """
            SELECT
                ActualSeed_time, ActSeed_course, Pre_heat,
                Pre_lane, Pre_Time, Pre_course,
                Pre_stat, Pre_place, Fin_heat, Fin_lane,
                Fin_Time, Fin_course, Fin_place,
                Fin_stat, fin_dqofficial, Ev_score,
                Team_ltr, Team_abbr, Event_no,
                Event_ltr
            FROM (Relay
            LEFT JOIN Team on Relay.Team_no = Team.Team_no)
            LEFT JOIN Event on Relay.Event_ptr = Event.Event_ptr
            """
    for result in process_results(cursor, query):

        entry = create_entry(result, RelayEntry)
        entry.event = meet.events[result["Event_no"], result["Event_ltr"]]
        entry.identifier = result["Team_ltr"]

        meet.relays[
            result["Event_no"],
            result["Event_ltr"],
            result["Team_abbr"],
            result["Team_ltr"],
        ] = entry

    # Relay Swimmers
    query = """
            SELECT
                Event_no, Event_ltr, Team_abbr,
                Team_lsc, RelayNames.Team_ltr, Reg_no,
                Event_round, Pos_no
            FROM (((RelayNames
            LEFT JOIN Relay ON RelayNames.Relay_no=Relay.Relay_no)
            LEFT JOIN Team ON RelayNames.Team_no = Team.Team_no)
            LEFT JOIN Athlete ON RelayNames.Ath_no=Athlete.Ath_no)
            LEFT JOIN Event on RelayNames.Event_ptr=Event.Event_ptr
            """
    for result in process_results(cursor, query):

        if result["Reg_no"] in desync_ids:
            result["Reg_no"] = desync_ids[result["Reg_no"]]

        if result["Event_round"] not in meet.relays[(result["Event_no"],result["Event_ltr"],result["Team_abbr"],result["Team_ltr"])].swimmers:
            meet.relays[
                result["Event_no"],
                result["Event_ltr"],
                result["Team_abbr"],
                result["Team_ltr"],
            ].swimmers[result["Event_round"]] = {}

        meet.relays[
            result["Event_no"],
            result["Event_ltr"],
            result["Team_abbr"],
            result["Team_ltr"],
        ].swimmers[result["Event_round"]][result["Pos_no"]] = meet.teams[result["Team_abbr"], result["Team_lsc"]].swimmers[result["Reg_no"]]

    # Individual Splits
    query = """
            SELECT
                Event_no, Event_ltr, Reg_no,
                Team_abbr, Rnd_ltr, Split_no,
                Split_Time
            FROM ((Split
            LEFT JOIN Athlete ON Split.Ath_no=Athlete.Ath_no)
            LEFT JOIN Team ON Athlete.Team_no=Team.Team_no)
            LEFT JOIN Event ON Split.Event_ptr=Event.Event_ptr
                WHERE Split.Ath_no IS NOT NULL AND Split.Ath_no <> 0
            """
    splits = process_results(cursor, query)
    for result in splits:

        if result["Reg_no"] in desync_ids:
            result["Reg_no"] = desync_ids[result["Reg_no"]]

        if result["Rnd_ltr"] in meet.entries[result["Event_no"],result["Event_ltr"],result["Reg_no"]].results:
            meet.entries[(
                result["Event_no"],
                result["Event_ltr"],
                result["Reg_no"],
            )].results[result["Rnd_ltr"]].splits[result["Split_no"]] = Time(result["Split_Time"])

    # Relay Splits
    query = """
            SELECT
                Event_no, Event_ltr, Team_abbr,
                Relay.Team_ltr, Rnd_ltr, Split_no,
                Split_Time
            FROM ((Split
            LEFT JOIN Relay ON Split.Relay_no=Relay.Relay_no)
            LEFT JOIN Team on Relay.Team_no=Team.Team_no)
            LEFT JOIN Event ON Split.Event_ptr=Event.Event_ptr
                WHERE Split.Relay_no IS NOT NULL AND Split.Relay_no <> 0
            """
    splits = process_results(cursor, query)
    for props in splits:
        meet.relays[(
            props["Event_no"],
            props["Event_ltr"],
            props["Team_abbr"],
            props["Team_ltr"],
        )].results[props["Rnd_ltr"]].splits[props["Split_no"]] = Time(props["Split_Time"])

    return meet


def is_valid_path(path):
    """Validates path to ensure it is valid in the current file system"""

    if not path:
        raise ValueError("No path given")
    if os.path.isfile(path) or os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid path: {path}")

def parse_args():
    """Get command line arguments"""

    parser = argparse.ArgumentParser(description="Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path, help="The path of the file or folder to process")

    args = vars(parser.parse_args())

    # Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("######################################################################")

    return args

def main():

    args = parse_args()

    input_file = args["input_path"]

    if input_file is None:
        input_file = filedialog.askopenfilename()

    if input_file == '':
        exit()

    meet = read_mdb(input_file)

    # f = open(input_file)
    # meet = read(f.readlines())


    # print(meet.teams["FRST"].points)
    # team_scores = [{"team": team, "score": team.points} for team in meet.teams.values()]
    # team_scores.sort(key=lambda x: x["score"], reverse=True)
    print(meet)


if __name__ == "__main__":
    main()
