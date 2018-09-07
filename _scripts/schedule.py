# A lil' script which generates a schedule given a series of dates
# Written by Will Barnes September 2018

# Dependencies: PyYaml - `pip install PyYaml`

from datetime import date, timedelta
from collections import defaultdict

TERMS = ["Michaelmas", "Lent", "Easter"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ADD = "add"
REMOVE = "remove"
ONE_WEEK = timedelta(7)

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
    def __init__(self, shows):
        """Constructor

        Arguments:
        shows -- a list of Show objects
        """

        self.shows = shows

        self.episode_count = sum(show.episode_count for show in shows)
        self.slot_number = shows[0].slot_number

    def get_proportion(self, episodes_shown):
        return episodes_shown/self.episode_count
    
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
            print(ep)
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

    def _distribute(self, start_date, end_date, min_eps, max_eps, meetings=False, shows=False):
        """Returns a list of Meeting objects, making a best effort to distribute the shows between the given dates,
        along with state for distributing over longer periods

        Arguments:
        start_date     -- the first possible day for a meeting to occur
        end_date       --  the last possible day for a meeting to occur
        min_eps        -- the minimum number of episodes in a meeting
        max_eps        -- the maximum number of episodes in a meeting
        meetings (Opt) -- the existing allocated meetings
        shows (Opt)    -- the existing state of the shows dict
        """

        days_til_first = (7 + self.day - start_date.weekday()) % 7
        first_meeting = start_date + timedelta(days_til_first)

        days_before_last = (7 - self.day + end_date.weekday()) % 7
        last_meeting = end_date - timedelta(days_before_last)

        week_count = 1 + (last_meeting - first_meeting).days // 7

        # Assignment algorithm - go for the one with the least proportion at each step
        # we have a catchup mechanism that if a show ever gets behind meetings we add more eps

        if not shows:
            shows = {}

            for show in self.shows:
                shows[show] = 0

        if not meetings:
            meetings = []

        for week_number in range(0, week_count):
            meeting_date = first_meeting + (ONE_WEEK * week_number)
            print(meeting_date.isoformat())
            episodes = defaultdict(list)
            current = 0
            
            meeting_prop = (week_number + 1) / week_count
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

        return (meetings, shows)

    def distribute_terms(self, dates, min_eps, max_eps):
        """
        Returns a list of Meeting objects, making a best effort to distribute the shows between the given dates,
        along with state for distributing over longer periods

        Arguments:
        start_date -- the first possible day for a meeting to occur
        end_date   --  the last possible day for a meeting to occur
        min_eps    -- the minimum number of episodes in a meeting
        max_eps    -- the maximum number of episodes in a meeting
        """

        meetings = False
        shows = False
        for start_date, end_date in dates:
            meetings, shows = self._distribute(start_date, end_date, min_eps, max_eps, meetings, shows)

        return meetings
        

    def distribute(self, start_date, end_date, min_eps, max_eps):
        """Returns a list of Meeting objects, making a best effort to distribute the shows between the given dates

        Arguments:
        start_date -- the first possible day for a meeting to occur
        end_date   --  the last possible day for a meeting to occur
        min_eps    -- the minimum length of a meeting in minutes
        max_eps    -- the maximum length of a meeting in minutes
        """
        return self._distribute(start_date, end_date, min_eps, max_eps, False, False)[0]

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
        lines.append("  time: {}&#8203;-&#8203;{}".format(self.type.start_time,
            self.type.end_time))
        lines.append("  venue: {}".format(self.type.venue))
        lines.append("  event: {}".format(self.type.event))
        lines.append("  shows:")
        for show,episodes in self.episodes:
            for line in show.format(episodes):
                lines.append("   - " + line) 
        return lines


def generate_term(term, start_date, end_date, meeting_types):
    """Generate the YAML for a term's schedule

    Arguments:
    term          -- the term name (eg. Michaelmas)
    start_date    -- the start date of the term (also used to determine display year)
    end_date      -- the end date of the term
    meeting_types -- a list of MeetingType objects
    """

    lines = []
    lines.append("- term: {} {}".format(term, start.year))
    lines.append("  meetings:")
    
    meetings = []
    for meeting_type in meeting_types:
        meetings += meeting_type.distribute()

    meetings.sort(key=extract_date)

    for meeting in meetings:
        lines += indent_all(meeting.to_yaml(), 2)

    return lines

def extract_date(x):
    return x.date

def indent(line, spaces):
    return " " * spaces + line

def indent_all(lines, spaces):
    return [indent(line, spaces) for line in lines]


# YAML stuff

# TODO(WJBarnes456): Implement YAML input


# CLI stuff

# TODO(WJBarnes456): Implement CLI

def run_cli():
    print("This script will eventually have a CLI. Give it some time.\nHit enter to exit.")
    input()
    
if __name__ == '__main__':
    run_cli()