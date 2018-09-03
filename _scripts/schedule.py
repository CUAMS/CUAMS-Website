# A lil' script which generates a schedule given a series of dates
# Written by Will Barnes 03/09/2018

# Dependencies: PyYaml - `pip install PyYaml`

from datetime import date, timedelta

TERMS = ["Michaelmas", "Lent", "Easter"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

ADD = "add"
REMOVE = "remove"
ONE_WEEK = timedelta(7)


def main():
    term = get_term();
    start_date = get_date("start", term)
    end_date = get_date("end", term)
    day = get_day()
    venue = get_venue()
    start_time = get_time("start")
    end_time = get_time("end")
    shows = get_shows()
    generate_schedule(term, start_date, end_date, day, venue, start_time, end_time, shows)

# General stuff

class MeetingType:
    """A helper class encapsulating a meeting type"""
    def __init__(self, venue, meeting_type, start_time, end_time, shows):
        """Build a meeting. This is the only constructor.
        venue         -- the venue of the meeting
        meeting_type  -- the type of a meeting
        start_time    -- the start time of the meeting
        end_time      -- the end time of the meeting
        shows         -- a list of (title, episode count) tuples
        """

        self.venue = venue
        self.type = meeting_type
        self.start_time = start_time
        self.end_time = end_time
        self.shows = shows

def generate_schedule(term, start_date, end_date, day, venue, start_time, end_time, shows):
    """Generate a schedule

    Arguments:
    term       -- the term name (eg. Michaelmas)
    start_date -- the start date of the term (also used to determine display year)
    end_date   -- the end date of the term
    day        -- the day of the week (integer where Monday is 0 and Sunday is 6)
    venue      -- the venue (eg. Angevin Room, Queens')
    start_time -- the start time
    end_time   -- the end time
    shows      -- a list of (title, episode count) tuples
    """

    lines = []
    lines.append("- term: {} {}".format(term, start.year))
    lines.append("  meetings:")
    
    days_til_first = (7 + day - start.day) % 7
    first_meeting = start + timedelta(days_til_first)

    days_before_last = (7 + day - end.day) % 7
    last_meeting = end - timedelta(days_before_last)

    weeks = (last_meeting - first_meeting).days // 7

    meeting = MeetingType(venue, meeting_type, start_time, end_time, shows)

    for i in range(weeks):
        lines += indent_all(generate_meeting(first_meeting, i, weeks, meeting), 2)

def generate_meeting(first_meeting, week_number, total_weeks, meeting):
    """Get the YAML for a meeting

    Arguments:
    first_meeting -- the date object for the first meeting
    week_number   -- the number of weeks through the total schedule
    total_weeks   -- the total number of weeks
    meeting       -- a MeetingType encapsulating the meeting details
    """

    lines = []
    meeting_date = first_meeting + (ONE_WEEK * 7)
    lines.append("- date: {}".format(this_meeting.isoformat()))
    lines.append("  time: {}&#8203;-&#8203;{}".format(meeting.start_time, meeting.end_time))
    lines.append("  event: " + meeting.type);
    lines.append("  shows: ")
    lines.append(indent_all(generate_shows(meeting.shows, week_number, total_weeks), 2))

def generate_shows(shows, week_number, total_weeks):
    """Get the YAML for the shows at a given meeting

    Arguments:
    shows       -- a list of (title, episode count) tuples
    week_number -- the week number of the term
    total_weeks -- the total number of weeks in the term
    """

    lines = []
    
    # TODO(WJBarnes456): Decide on how we'll compute this

def indent(line, spaces):
    return " " * spaces + line

def indent_all(lines, spaces):
    return [indent(line, spaces) for line in lines]



# YAML stuff

# TODO(WJBarnes456): Implement YAML input

# CLI stuff

def get_term():
    while True:
        user_term = input("Please enter the term you would like to make a schedule for " +
                get_options(TERMS))
        for term in TERMS:
            if user_term in term:
                return term
        print("That doesn't seem to be a valid term. Please try again.")

def get_options(options):
    return "(available options " + ", ".join(options) + ")\n"

def get_date(date_type, term):
    while True:
        user_date = input("What is the " + date_type + " date of this " + term + " term? (YYYY-mm-dd)\n")
        try:
            parts = user_date.split("-")
            year, month, day = [int(part) for part in parts]
            return date(year, month, day)
        except ValueError:
            print("That doesn't seem to be a valid date. Please try again.")

def get_day():
    while True:
        user_day = input("What day of the week is the meeting occurring on? " +
                get_options(DAYS))
        for day in DAYS:
            if user_day in day:
                return DAYS.index(day)
            else:
                print("That doesn't seem to be a valid day. Please try again.")

def get_shows():
    shows = []
    while True:
        if len(shows) == 0:
            print("There are currently no shows on the schedule.")
        else:
            print("Current schedule: ")
            for show in shows: print_show(show)
        
        choice = menu();

        if choice == ADD:
            add_show(shows)
        elif choice == REMOVE:
            remove_show(shows)
        elif choice == EXIT:
            return shows

def get_time(time_type):
    return input("When will the meeting " + time_type + "? ")

def print_show(show):
    title, episodes = show
    print("{}: {} episodes".format(title, episodes))

def menu():
    while True:
        print("Options: ")
        print("1. Add show")
        print("2. Remove show")
        print("0. Exit")

        choice = input();
        
        if choice == "1":
            return ADD
        elif choice == "2":
            return REMOVE
        elif choice == "0":
            return EXIT
        else:
            print("Unknown choice, please try again\n")

if __name__ == '__main__':
    main()
