from schedule import MeetingType, Meeting, Show, Slot
from datetime import date

def print_meetings(meets):
    print("\n".join(["\n".join(meet.to_yaml()) for meet in meets]))
    

mainMeeting = MeetingType(1, "Angevin Room, Queens'", "Main Meeting", "7", "10pm",
                          [Show("Baccano!", 13, 24),
                           Show("Flip Flappers", 13, 24),
                           Show("The Tatami Galaxy", 11, 24)])

testLent = MeetingType(1, "Angevin Room, Queens'", "Main Meeting", "7", "10pm",
                          [Show("Nichijou", 26, 24),
                           Slot([Show("MiA", 13, 24), Show("Princess Principal", 13, 24)]),
                           Show("Samurai Champloo", 26, 24)])
startM = date(2017,10,14)
endM = date(2017,11,21)

print_meetings(mainMeeting.distribute(startM, endM, 130, 180))

startL = date(2018, 1,21)
endL = date(2018, 3, 14)

startE = date(2018, 4, 4)
endE = date(2018, 6, 2)

print_meetings(testLent.distribute_terms([(startL, endL), (startE, endE)], 120, 180))

input()
