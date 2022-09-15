import csv
import json
import operator
from re import L
from objects import Party, SharingAgreement
import math
import requests
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import secrets

THRESHOLD_PERCENT = 3.25
TOTAL_SEATS = 120
VOTESHARE_DOC = 'votesharing.json'

def load_votes():
    response = requests.get(
        f'https://docs.google.com/spreadsheet/ccc?key={secrets.SHEET_ID}&output=csv')
    assert response.status_code == 200, 'Wrong status code'
    responses = response.content.decode('utf-8').split('\r\n')[1:]
    responses = [x[20:] for x in responses]
    counts = Counter(responses)
    return counts


def create_parties(parties_dict):
    parties = list()
    with open(VOTESHARE_DOC, 'r') as f:
        votesharings = json.load(f)
    for party, votes in parties_dict.items():
        if party != '':
            parties.append(Party(party, votes, votesharings[party]))
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
        partnerships.append(SharingAgreement(party, party.partner))
        if party.partner != None:
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
    parties_dict = load_votes()
    parties = create_parties(parties_dict)
    calculate_seats(parties)
    parties = sorted(parties, key=lambda x: (
        x.seats, x.percentage), reverse=True)
    for party in parties:
        if party.seats > 0:
            print(party.name, party.seats)
        else:
            print(f"{party.name} {party.percentage}%")


if __name__ == "__main__":
    main()
