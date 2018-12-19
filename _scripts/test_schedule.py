from schedule import MeetingType, Meeting, Show, Slot, Term, generate_terms
from datetime import date

def print_meetings(meets):
    print("\n".join(["\n".join(meet.to_yaml()) for meet in meets]))
    

mainMeeting = MeetingType(1, "Angevin Room, Queens'", "Main Meeting", "7", "10pm",
                          [Show("Baccano!", 13, 1),
                           Show("Flip Flappers", 13, 2),
                           Show("The Tatami Galaxy", 11, 3)])

mainLentEaster = MeetingType(1, "Bowett Room, Queens'", "Main Meeting", "7", "10pm",
                          [Slot([Show("Spice and Wolf", 13, 1), Show("Spice and Wolf II", 13, 1)]),
                           Show("Tengen Toppa Gurren Lagann", 27, 2),
                           Slot([Show("Kids on the Slope", 12, 3), Show("Girls' Last Tour", 12, 3) ])])
                           
sundayLentEaster = MeetingType(6, "Bowett Room, Queens'", "Sunday Meeting", "2.30", "5.30pm",
                          [Slot([Show("Oregairu", 13, 1), Show("Oregairu Zoku", 13, 1)]),
                           Slot([Show("Ga-Rei-Zero", 12, 2), Show("Revue Starlight", 12, 2)]),
                           Show("Shirobako", 24, 3)])


startM = date(2017,10,14)
endM = date(2017,11,21)

lines = generate_terms([Term("Michaelmas", startM, endM)],
                       [mainMeeting],
                       5, 7)

print("\n".join(lines))

startL = date(2019, 1, 20)
endL = date(2019, 3, 12)

startE = date(2019, 4, 28)
endE = date(2019, 5, 22)

lines = generate_terms([Term("Lent", startL, endL), Term("Easter", startE, endE)],
                       [mainLentEaster, sundayLentEaster],
                       5, 7)

print("\n".join(lines))


input()
 
