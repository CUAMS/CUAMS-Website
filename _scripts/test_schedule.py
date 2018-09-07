from schedule import MeetingType, Meeting, Show, Slot
from datetime import date

def print_meetings(meets):
    print("\n".join(["\n".join(meet.to_yaml()) for meet in meets]))
    

mainMeeting = MeetingType(1, "Angevin Room, Queens'", "Main Meeting", "7", "10pm",
                          [Show("Baccano!", 13, 1),
                           Show("Flip Flappers", 13, 2),
                           Show("The Tatami Galaxy", 11, 3)])

testLent = MeetingType(1, "Angevin Room, Queens'", "Main Meeting", "7", "10pm",
                          [Show("Nichijou", 26, 1),
                           Slot([Show("MiA", 13, 2), Show("Princess Principal", 13, 2)]),
                           Show("Samurai Champloo", 26, 3)])
startM = date(2017,10,14)
endM = date(2017,11,21)

print_meetings(mainMeeting.distribute(startM, endM, 5, 7))

startL = date(2018, 1,21)
endL = date(2018, 3, 13)

startE = date(2018, 5, 1)
endE = date(2018, 5, 23)

print_meetings(testLent.distribute_terms([(startL, endL), (startE, endE)], 5, 7))

input()
