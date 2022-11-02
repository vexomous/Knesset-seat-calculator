class Party():
    def __init__(self, name=None, votes=0, vote_sharing=None):
        self.name = name
        self.votes = int(votes)
        self.votesharing = vote_sharing
        self.seats = 0
        self.percentage = 0

    def get_name(self):
        return self.name

    def set_partner(self, partner):
        self.partner = partner

    def set_seats(self, seats):
        self.seats = seats

    def add_seat(self):
        self.seats += 1

    def set_leftovers(self, votes):
        self.leftovers = votes

    def set_percentage(self, percentage):
        self.percentage = percentage


class SharingAgreement():
    def __init__(self, party1, party2):
        self.party1 = party1
        self.party2 = party2
        self.bonus_seats = 0
        self.party1_bonus_seats = 0
        self.party2_bonus_seats = 0
        self.calc_standard()

    def calc_individual_standards(self):
        self.party1_standard = (self.party1.votes) / \
            (self.party1.seats + self.party1_bonus_seats + 1)
        if self.party2 != None:
            self.party2_standard = (
                self.party2.votes) / (self.party2.seats + self.party2_bonus_seats + 1)
        else:
            self.party2_standard = 0

    def calc_standard(self):
        if self.party2 == None:
            self.standard = self.party1.votes / \
                (self.party1.seats + self.bonus_seats + 1)
        else:
            self.standard = (self.party1.votes + self.party2.votes) / \
                (self.party1.seats + self.party2.seats + self.bonus_seats + 1)

    def distrib_bonus_seats(self):
        while self.bonus_seats > 0:
            self.calc_individual_standards()
            if self.party1_standard >= self.party2_standard:
                self.party1.add_seat()
                # self.party1_bonus_seats += 1
            else:
                self.party2.add_seat()
                # self.party2_bonus_seats += 1
            self.bonus_seats -= 1

    def add_seat(self):
        self.bonus_seats += 1
        self.calc_standard()
