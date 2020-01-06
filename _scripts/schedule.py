# A lil' script which generates a schedule given a series of dates
# Written by Will Barnes September 2018

# Dependencies: PyYaml - `pip install PyYaml`

from datetime import date, timedelta, datetime
from collections import defaultdict

TERMS = ["Michaelmas", "Lent", "Easter"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ADD = "add"
REMOVE = "remove"
ONE_WEEK = timedelta(7)

# Default constants
MIN_EPS = 5
MAX_EPS = 7

# General stuff

class Show:
    def __init__(self, title, episode_count, slot_number):
        """Constructor

        Arguments:
        title          -- the title of the show
        episode_count  -- the number of episodes in the show
        episode_weight -- the length of the episode in minutes
        slot_number    -- the number of the slot this show is in
        """
        self.title = title
        self.episode_count = episode_count
        self.slot_number = slot_number
    
    def __str__(self):
        return "{} ({} episodes)".format(self.title, self.episode_count)

    def get_proportion(self, episodes_shown):
        return episodes_shown/self.episode_count

    def get_prop_from_shows(self, shows):
        return self.get_proportion(shows[self])
        
    def format(self, episodes):
        """Returns a string representing the given episodes of the show"""
        sorted_eps = sorted(episodes)
        first = sorted_eps[0]
        last = sorted_eps[-1]

        if first == last:
            return ["{} {}".format(self.title, first)]
        else:
            return ["{} {}-{}".format(self.title, first, last)]
        

class Slot:
    """Helper class, duck-typed to work the same as a Show - aggregate pattern"""
    def __init__(self, shows, slot_number = None):
        """Constructor

        Arguments:
        shows -- a list of Show objects
        """

        self.set_shows(shows)
        
        if slot_number == None:
            self.slot_number = shows[0].slot_number
        else:
            self.slot_number = slot_number
    
    def __str__(self):
        return "[" + ", ".join([str(show) for show in self.shows]) + "]"
        
    def set_shows(self, shows):
        self.shows = shows
        self.reset_count()
    
    def reset_count(self):
        self.episode_count = sum(show.episode_count for show in self.shows)
        

    def get_proportion(self, episodes_shown):
        # Handle special case with empty slot
        if self.episode_count > 0:
            return episodes_shown/self.episode_count
        else:
            return 1
    
    def get_prop_from_shows(self, shows):
        return self.get_proportion(shows[self])
    
    def get_show(self, episode_number):
        for show in self.shows:
            prev_num = episode_number
            episode_number -= show.episode_count
            if episode_number <= 0:
                return (show, prev_num)
        return (None, episode_number)
        
    def format(self, episodes):
        sorted_eps = sorted(episodes)
        
        shows = defaultdict(list)
        for ep in sorted_eps:
            show, new_ep = self.get_show(ep)
            shows[show].append(new_ep)
        
        return [show.format(eps)[0] for show,eps in shows.items()]
        

class MeetingType:
    """A helper class encapsulating a meeting type"""
    def __init__(self, day, venue, event, start_time, end_time, shows):
        """Constructor

        Arguments:
        day           -- the day of the week the meeting is on, as an integer
                         from 0 (Monday) to 6 (Sunday)
        venue         -- the venue of the meeting
        event         -- the user-readable name of this meeting (eg. Main Meeting)
        start_time    -- the start time of the meeting
        end_time      -- the end time of the meeting
        shows         -- a list of Show objects
        """
        
        self.day = day
        self.venue = venue
        self.event = event
        self.start_time = start_time
        self.end_time = end_time
        self.shows = shows
        
    def _get_week_count(self, start_date, end_date):
        days_til_first = (7 + self.day - start_date.weekday()) % 7
        first_meeting = start_date + timedelta(days_til_first)

        days_before_last = (7 - self.day + end_date.weekday()) % 7
        last_meeting = end_date - timedelta(days_before_last)

        return 1 + (last_meeting - first_meeting).days // 7

    def _get_next(self, shows, eps_left, meeting_proportion):
        if eps_left == 0:
            return None
            
        min_prop = 1
        min_eps = float("inf")

        behind_eps = None
        behind_prop = None
        for (show, ep) in shows.items():
            prop = show.get_proportion(ep)

            if (ep < min_eps) and (prop < meeting_proportion):
                min_eps = ep
                behind_eps = show
                
            if prop < min_prop:
                min_prop = prop
                behind_prop = show

        if behind_eps:
            return behind_eps
        else:
            return behind_prop

    def _distribute(self, start_date, end_date, min_eps, max_eps, total_week_count=None, starting_week=0, meetings=None, shows=None):
        """Returns a list of Meeting objects, making a best effort to distribute the shows between the given dates,
        along with state for distributing over longer periods

        Arguments:
        start_date           -- the first possible day for a meeting to occur
        end_date             --  the last possible day for a meeting to occur
        min_eps              -- the minimum number of episodes in a meeting
        max_eps              -- the maximum number of episodes in a meeting
        total_weeks (Opt)    -- the total number of weeks to distribute over 
        starting_week  (Opt) -- the week to start at in assignment
        meetings (Opt)       -- the existing allocated meetings
        shows (Opt)          -- the existing state of the shows dict
        """

        days_til_first = (7 + self.day - start_date.weekday()) % 7
        first_meeting = start_date + timedelta(days_til_first)
        week_count = self._get_week_count(start_date, end_date)
        
        if total_week_count is None:
            total_week_count = week_count

        if shows is None:
            shows = {}

            for show in self.shows:
                shows[show] = 0

        if meetings is None:
            meetings = []

        # Assignment algorithm - go for the one with the least proportion at each step
        # we have a catchup mechanism that if a show ever gets behind meetings we add more eps

        for week_number in range(starting_week, starting_week + week_count):
            meeting_date = first_meeting + (ONE_WEEK * week_number)
            episodes = defaultdict(list)
            current = 0
            
            meeting_prop = (week_number + 1) / total_week_count
            while True:
                next_show = self._get_next(shows, max_eps - current, meeting_prop)
                
                if next_show == None:
                    break
                elif ((next_show.get_prop_from_shows(shows) < meeting_prop)
                      or (current < min_eps)):
                    next_episode = shows[next_show] + 1
                    shows[next_show] = next_episode
                    
                    episodes[next_show].append(next_episode)
                    current += 1
                else:
                    break
            episode_list = list(episodes.items())

            if episode_list:
                meetings.append(Meeting(self, meeting_date, episode_list))

        return (meetings, shows, starting_week + week_count)

    def distribute_dates(self, dates, min_eps, max_eps):
        """
        Returns a list of Meeting objects, making a best effort to distribute the shows between the given dates,
        along with state for distributing over longer periods

        Arguments:
        dates   -- a set of tuples (start_date, end_date) where
            start_date is the first possible day for a meeting to occur
            end_date is the last possible day for a meeting to occur
        min_eps -- the minimum number of episodes in a meeting
        max_eps -- the maximum number of episodes in a meeting
        """
        
        total_week_count = 0
        for (start_date, end_date) in dates:
            total_week_count += self._get_week_count(start_date, end_date)
            
        meetings = None
        shows = None
        starting_week = 0
        for start_date, end_date in dates:
            meetings, shows, starting_week = self._distribute(start_date, end_date, min_eps, max_eps,
                                                              meetings=meetings, shows=shows,
                                                              starting_week=starting_week,
                                                              total_week_count=total_week_count)

        return meetings
        
    def distribute_terms(self, terms, min_eps, max_eps):
        return self.distribute_dates([(t.start_date, t.end_date) for t in terms], min_eps, max_eps)
        

    def distribute(self, start_date, end_date, min_eps, max_eps):
        """Returns a list of Meeting objects, making a best effort to distribute the shows between the given dates

        Arguments:
        start_date -- the first possible day for a meeting to occur
        end_date   --  the last possible day for a meeting to occur
        min_eps    -- the minimum length of a meeting in minutes
        max_eps    -- the maximum length of a meeting in minutes
        """
        return self._distribute(start_date, end_date, min_eps, max_eps)[0]
        
    def distribute(self, term, min_eps, max_eps):
        return distribute(term.start_date, term.end_date, min_eps, max_eps)
        
    def to_yaml(self):
        return [f"- name: {self.event}",
                f"  time: {self.start_time}&#8203;-&#8203;{self.end_time}",
                f"  venue: {self.venue}"]

class Meeting:
    """A helper class which encapsulates a single meeting"""
    def __init__(self, meeting_type, date, episodes):
        """Constructor

        Arguments:
        meeting_type -- a MeetingType object which contains other details about
                        this meeting
        date         -- a date object denoting the exact date of this meeting
        episodes     -- a list of (show, int list) tuples which denote the
                        episodes being shown at this meeting
        """

        self.type = meeting_type
        self.date = date
        self.episodes = sorted(episodes, key=lambda x:x[0].slot_number)

    def to_yaml(self):
        lines = []
        lines.append("- date: " + self.date.isoformat())
        lines.append("  event: {}".format(self.type.event))
        lines.append("  shows:")
        for show,episodes in self.episodes:
            for line in show.format(episodes):
                lines.append("   - " + line) 
        return lines
        
class Term:
    """A helper class encapsulating a term"""
    def __init__(self, name, start_date, end_date):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date


def generate_term(term, start_date, end_date, meeting_types, min_eps = MIN_EPS, max_eps = MAX_EPS):
    """Generate the YAML for a term's schedule

    Arguments:
    term          -- the term name (eg. Michaelmas)
    start_date    -- the start date of the term (also used to determine display year)
    end_date      -- the end date of the term
    meeting_types -- a list of MeetingType objects
    """

    lines = []
    lines.append("- term: {} {}".format(term, start_date.year))
    lines.append("  events:")
    
    for meeting_type in meeting_types:
        lines += indent_all(meeting_type.to_yaml(), 2)
    
    lines.append("  meetings:")
    
    meetings = []
    for meeting_type in meeting_types:
        meetings += meeting_type.distribute(start_date, end_date, min_eps, max_eps)

    meetings.sort(key=extract_date)

    for meeting in meetings:
        lines += indent_all(meeting.to_yaml(), 2)

    return lines
    
def generate_terms(terms, meeting_types, min_eps = MIN_EPS, max_eps = MAX_EPS):
    """Generate the YAML for a Lent/Easter schedule

    Arguments:
    terms         -- the term names (eg. [Lent, Easter])
    dates         -- a set of tuples (start_date, end_date) where
            start_date is the first possible day for a meeting to occur
            end_date is the last possible day for a meeting to occur
    meeting_types -- a list of MeetingType objects
    """
    
    # Copy lists to avoid damaging the originals
    terms = list(terms)
    
    meetings = []
    for meeting_type in meeting_types:
        meetings += meeting_type.distribute_terms(terms, min_eps, max_eps)

    meetings.sort(key=extract_date)

    lines = []
    next_term = terms.pop(0)
    for meeting in meetings:
        if next_term and meeting.date >= next_term.start_date:
            lines.append("- term: {} {}".format(next_term.name, next_term.start_date.year))
            lines.append("  events:")
            
            for meeting_type in meeting_types:
                lines += indent_all(meeting_type.to_yaml(), 4)
            
            lines.append("  meetings:")
            if terms:
                next_term = terms.pop(0)
            else:
                next_term = None
        lines += indent_all(meeting.to_yaml(), 4)

    return lines

def extract_date(x):
    return x.date

def indent(line, spaces):
    return " " * spaces + line

def indent_all(lines, spaces):
    return [indent(line, spaces) for line in lines]
    
# Placeholder meetings etc

def placeholder_type():
    return MeetingType(1, "Bowett Room, Queens'", "Placeholder Meeting", "7", "10pm", [Slot([], 1), Slot([], 2), Slot([], 3)])

def placeholder_term():
    return Term("Michaelmas", date(2018, 10, 2), date(2018, 11, 30))

def placeholder_show(number):
    return Show("Madoka Magica", 12, number)


# YAML stuff

# TODO(WJBarnes456): Implement YAML input

# CLI utility functions


def get_new_day():
    new_day = None
    while new_day == None:
        option = input("New day: ")
        
        for i, day in enumerate(DAYS):
            if option in day:
                new_day = i
        
        if new_day == None:
            print("Not sure! Please try again")
    
    return new_day
    
def get_new_string(thing):
    option = input("New {}: ".format(thing))
    return option
    
def get_new_int(thing, pos_only = False):
    while True:
        try:
            option = int(input("New {}: ".format(thing)))
            if (not pos_only) or option > 0:
                return option
            else:
                print("{} must be positive. Please try again.", thing)
        except ValueError:
            print("That is not a number. Please try again.")
            
def get_new_date(thing):
    while True:
        try:
            option = input("New {} (YYYY-MM-DD): ".format(thing))
            return datetime.strptime(option, "%Y-%m-%d").date()
        except ValueError:
            print("That is not a valid date. Please try again.")

# CLI stuff
def print_menu():
    print("===== MAIN MENU =====")
    print("1. Change meetings")
    print("2. Change terms + dates")
    print("3. Generate schedule")
    print("0. Exit")

def run_cli():
    meeting_types = []
    terms = []
    
    while True:
        print_menu()
        
        option = input()
        if option == "0":
            return
        elif option == "1":
            change_meetings(meeting_types)
        elif option == "2":
            change_terms(terms)
        elif option == "3":
            export_schedule(meeting_types, terms)
        else:
            print("Unknown option, please try again")
            
def export_schedule(meeting_types, terms):
    if len(terms) == 0:
        print("Terms are empty! Change term dates first")
        return
       
    lines = generate_terms(terms, meeting_types, 5, 7)
    file = input("Output filename: ")
    with open(file, "w") as f:
        for line in lines:
            f.write(line + "\n")
            
    print("File exported, check {}".format(file))

def print_types_menu(meeting_types):
    print("===== CHANGE MEETINGS =====")
    for i, meeting_type in enumerate(meeting_types, 1):
        print("{}. Change {} on {}s".format(i, meeting_type.event, DAYS[meeting_type.day]))
    print("{}. Add new meeting".format(len(meeting_types) + 1))
    
    print("0. Save and back")
    
def change_meetings(meeting_types):
    while True:
        try:
            print_types_menu(meeting_types)
            option = int(input())
            
            if option == 0:
                return
            elif option <= len(meeting_types):
                if change_meeting(meeting_types[option-1]):
                    del meeting_types[option-1]
            elif option == len(meeting_types) + 1:
                meeting = placeholder_type()
                if not change_meeting(meeting):
                    meeting_types.append(meeting)
            else:
                print("Unknown option, please try again")
        except ValueError:
            print("Unknown input, please try again")

def print_meeting_menu(current_meeting):
    print("===== CHANGE MEETING =====")
    print("1. Set meeting day (currently {})".format(DAYS[current_meeting.day]))
    print("2. Set meeting venue (currently '{}')".format(current_meeting.venue))
    print("3. Set meeting event type (currently '{}')".format(current_meeting.event))
    print("4. Set meeting start time (currently '{}')".format(current_meeting.start_time))
    print("5. Set meeting end time (currently '{}')".format(current_meeting.end_time))
    print("6. Change meeting shows")
    print("7. Remove meeting")
    print("0. Save and back")
    
def change_meeting(current_meeting):
    while True:
        try:
            print_meeting_menu(current_meeting)
            option = int(input())
            
            if option == 0:
                return
            elif option == 1:
                current_meeting.day = get_new_day()
            elif option == 2:
                current_meeting.venue = get_new_string("venue")
            elif option == 3:
                current_meeting.event = get_new_string("event")
            elif option == 4:
                current_meeting.start_time = get_new_string("start time")
            elif option == 5:
                current_meeting.end_time = get_new_string("end time")
            elif option == 6:
                change_shows(current_meeting.shows)
            elif option == 7:
                return True
            else:
                print("Unknown option, please try again")
                
        except ValueError:
            print("Unknown input, please try again")

def print_shows(shows):
    print("===== CHANGE SHOWS =====")
    for i, slot in enumerate(shows, 1):
        print("{0}. Change slot {0} (currently {1})".format(i, str(slot)))
        
    print("{}. Add new slot".format(len(shows) + 1))
    
    print("0. Save and back")
    
def change_shows(shows):
    while True:
        try:
            print_shows(shows)
            option = int(input())
            
            if option == 0:
                return
            elif option <= len(shows):
                if change_slot(shows[option-1]):
                    del shows[option-1]
            elif option == len(meeting_types) + 1:
                slot = Slot([], len(meeting_types) + 1)
                if not change_slot(slot):
                    shows.append(slot)
            else:
                print("Unknown option, please try again")
                
        except ValueError:
            print("Unknown input, please try again")

def print_slot(slot):
    print("===== CHANGE SLOT =====")
    for i, show in enumerate(slot.shows, 1):
        print("{0}. Change {1}".format(i, str(show)))
        
    print("{}. Add new show".format(len(slot.shows) + 1))
    
    print("0. Save and back")            

def change_slot(slot):
    shows = slot.shows
    while True:
        try:
            print_slot(slot)
            option = int(input())
            
            if option == 0:
                # Recompute episode count to ensure it distributes right
                slot.reset_count()
                return
            elif option <= len(shows):
                if change_show(shows[option-1]):
                    del shows[option-1]
            elif option == len(shows) + 1:
                show = placeholder_show(slot.slot_number)
                if not change_show(show):
                    shows.append(show)
            else:
                print("Unknown option, please try again")
                
        except ValueError:
            print("Unknown input, please try again")
            
def print_show(show):
    print("===== CHANGE SHOW =====")
    print("1. Set show title (currently {})".format(show.title))
    print("2. Set episode count (currently {})".format(show.episode_count))
    print("3. Remove show")
    print("0. Save and back")

def change_show(show):
    while True:
        try:
            print_show(show)
            option = int(input())
            
            if option == 0:
                return
            elif option == 1:
                show.title = get_new_string("title")
            elif option == 2:
                show.episode_count = get_new_int("episode count", pos_only = True)
            elif option == 3:
                return True
            else:
                print("Unknown option, please try again")
                
        except ValueError:
            print("Unknown input, please try again")
    
def print_terms(terms):
    print("===== CHANGE TERMS =====")
    for i, term in enumerate(terms, 1):
        print("{}. Change {} term (currently starts {}, ends {})".format(i, term.name, term.start_date, term.end_date))
    
    print("{}. Add new term".format(len(terms) + 1))
    
    print("0. Exit")
    
def change_terms(terms):
     while True:
        try:
            print_terms(terms)
            option = int(input())
            
            if option == 0:
                return
            elif option <= len(terms):
                if change_term(terms[option-1]):
                    del terms[option-1]
            elif option == len(terms) + 1:
                term = placeholder_term()
                if not change_term(term):
                    terms.append(term)
            else:
                print("Unknown option, please try again")
                
        except ValueError:
            print("Unknown input, please try again")

def print_term(term):
    print("===== CHANGE TERM =====")
    print("1. Set term name (currently {})".format(term.name))
    print("2. Set term start date (currently {})".format(term.start_date))
    print("3. Set term end date (currently {})".format(term.end_date))
    print("4. Remove term")
    print("0. Save and back")
    
def change_term(term):
    while True:
        try:
            print_term(term)
            option = int(input())
            
            if option == 0:
                return
            elif option == 1:
                term.name = get_new_string("term name")
            elif option == 2:
                term.start_date = get_new_date("start date")
            elif option == 3:
                term.end_date = get_new_date("end date")
            elif option == 4:
                return True
            else:
                print("Unknown option, please try again")
                
        except ValueError:
            print("Unknown input, please try again")
    
    
if __name__ == '__main__':
    run_cli()
