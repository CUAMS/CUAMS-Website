from schedule import MeetingType, Meeting, Show, Slot, Term, generate_terms
from datetime import date

def print_meetings(meets):
    print("\n".join(["\n".join(meet.to_yaml()) for meet in meets]))
    

mainMeeting = MeetingType(1, "Angevin Room, Queens'", "Main Meeting", "7", "10pm",
                          [Show("Baccano!", 13, 1),
                           Show("Flip Flappers", 13, 2),
                           Show("The Tatami Galaxy", 11, 3)])

mainLentEaster = MeetingType(1, "Bowett Room, Queens'", "Main Meeting", "7", "10pm",
                          [Slot([Show("Humanity has Declined!", 12, 1), Show("Angel Beats!", 13, 1)]),
                           Slot([Show("Shouwa Genroku Rakugo Shinjuu", 13, 2), Show("Rakugo S2", 12, 2)]),
                           Slot([Show("Spice and Wolf", 13, 3), Show("Spice and Wolf OVA", 1, 3), Show("Spice and Wolf II", 12, 3)])])
                           
sundayLentEaster = MeetingType(6, "Bowett Room, Queens'", "Sunday Meeting", "2.30", "5.30pm",
                          [Slot([Show("Kekkai Sensen", 12, 1), Show("Kekkai Sensen & Beyond", 12, 1)]),
                           Slot([Show("Plastic Memories", 13, 2), Show("Granbelm", 13, 2)]),
                           Show("Hyouka (TBC)", 22, 3)])


startM = date(2017,10,14)
endM = date(2017,11,21)

lines = generate_terms([Term("Michaelmas", startM, endM)],
                       [mainMeeting],
                       5, 7)

print("\n".join(lines))

startL = date(2020, 1, 15)
endL = date(2020, 3, 11)

startE = date(2020, 4, 25)
endE = date(2020, 5, 20)

lines = generate_terms([Term("Lent", startL, endL), Term("Easter", startE, endE)],
                       [mainLentEaster, sundayLentEaster],
                       5, 7)

print("\n".join(lines))


input()
 
