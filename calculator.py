import csv
import operator
from re import L
from objects import Party, SharingAgreement
import math

THRESHOLD_PERCENT = 3.25
TOTAL_SEATS = 120
VOTE_FILE = 'votes.csv'

def load_votes():
    with open(VOTE_FILE, 'r', encoding="utf8") as f:
        a = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
        return a

def create_parties(parties_dict):
    parties = list()
    for party in parties_dict:
        parties.append(Party(party["name"], party["votes"], party["votesharing"]))
    for party in parties:
        party.set_partner(next((x for x in parties if x.name == party.votesharing), None))
    return parties

def calc_seat_leftover(party, receiving, seat_parameter):
    receiving_new_total = receiving.leftovers + party.leftovers
    if receiving_new_total >= seat_parameter:
        receiving.add_seat()
        receiving.set_leftovers(receiving_new_total - seat_parameter)
        party.set_leftovers(0)

def bader_ofer(legit_parties, seat_parameter):
    for party in legit_parties:
        seats = math.floor(party.votes/seat_parameter)
        leftovers = (seats+1)*seat_parameter-party.votes
        party.set_seats(seats)
        party.set_leftovers(leftovers)
    left_to_distribute = 120 - sum(party.seats for party in legit_parties)
    distrib_lists = dict()
    left_to_partnerize = legit_parties
    partnerships = list()
    for party in left_to_partnerize:
        partnerships.append(SharingAgreement(party, party.partner))
        if party.partner != None:
            left_to_partnerize.remove(party.partner)
    while left_to_distribute > 0:
        partnerships = sorted(partnerships, key=operator.attrgetter("standard"), reverse=True)
        print("adding to", partnerships[0].party1.name)
        partnerships[0].add_seat()
        left_to_distribute -= 1
    for partnership in partnerships:
        partnership.distrib_bonus_seats()

def calculate_seats(parties):
    total_votes = sum(party.votes for party in parties)
    threshold_votes = total_votes * THRESHOLD_PERCENT / 100
    legit_parties = [party for party in parties if party.votes >= threshold_votes]
    legit_votes = sum(party.votes for party in legit_parties)
    seat_parameter = legit_votes / TOTAL_SEATS
    bader_ofer(legit_parties, seat_parameter)
    


def main():
    parties_dict = load_votes()
    parties = create_parties(parties_dict)
    calculate_seats(parties)
    for party in parties:
        print(party.name, party.seats)

if __name__ == "__main__":
    main()