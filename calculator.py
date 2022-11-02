import json
import operator
from re import L
from objects import Party, SharingAgreement
import math
import requests
from collections import Counter
import hidden
import visualizer
import scraper
from bidi.algorithm import get_display

THRESHOLD_PERCENT = 3.25
TOTAL_SEATS = 120
VOTESHARE_DOC = 'votesharing.json'
TOTAL_VOTES = 6788804 * 0.713
RENAME_FILE = 'namereplace.json'

def rename_parties(parties):
    party_names = [x.name for x in parties]
    with open(RENAME_FILE, 'r', encoding="utf8") as f:
        data = json.load(f)
        for i, name in enumerate(party_names):
            try:
                party_names[i] = data[name]
            except KeyError as e:
                continue
    return party_names

def create_parties(parties_dict):
    parties = list()
    with open(VOTESHARE_DOC, 'r', encoding="utf8") as f:
        votesharings = json.load(f)
    for party, votes in parties_dict.items():
        if party != '':
            try:
                parties.append(Party(party, votes, votesharings[party]))
            except KeyError as e:
                parties.append(Party(party, votes, ""))
    for party in parties:
        party.set_partner(
            next((x for x in parties if x.name == party.votesharing), None))
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
    left_to_partnerize = legit_parties
    partnerships = list()
    for party in left_to_partnerize:
        if party.partner != None:
            if party.partner.seats > 0:
                partnerships.append(SharingAgreement(party, party.partner))
                left_to_partnerize.remove(party.partner)
    while left_to_distribute > 0:
        partnerships = sorted(
            partnerships, key=operator.attrgetter("standard"), reverse=True)
        partnerships[0].add_seat()
        left_to_distribute -= 1
    for partnership in partnerships:
        partnership.distrib_bonus_seats()


def calculate_seats(parties):
    total_votes = sum(party.votes for party in parties)
    for party in parties:
        party.set_percentage(round(party.votes/total_votes*100, 2))
    threshold_votes = total_votes * THRESHOLD_PERCENT / 100
    legit_parties = [
        party for party in parties if party.votes >= threshold_votes]
    legit_votes = sum(party.votes for party in legit_parties)
    seat_parameter = legit_votes / TOTAL_SEATS
    bader_ofer(legit_parties, seat_parameter)


def main():
    table, counted = scraper.get_page()
    parties_dict = scraper.get_parties(table)
    parties = create_parties(parties_dict)
    calculate_seats(parties)
    parties = sorted(parties, key=lambda x: (
        x.seats, x.percentage), reverse=True)
    counted_percent = counted / TOTAL_VOTES * 100
    print(f"**Results with about {round(counted_percent, 2)}% of the votes counted:**")
    party_names = rename_parties(parties)
    party_seats = [x.seats for x in parties]
    for id, party in enumerate(party_names):
        if party_seats[id] > 0:
            print(get_display(f"{party} {party_seats[id]}"))
        else:
            print(get_display(f"{party} {parties[id].percentage}%"))
    visualizer.create_chart(parties)


if __name__ == "__main__":
    main()
