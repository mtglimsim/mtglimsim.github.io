# MTG Limited Simulator (AKA MTGLimSim)
# An MTG draft simulator that collects data on people's draft decisions.
# This data can be used post-hoc to...
# - analyze sets and cards from those sets
# - allow players to look at their draft histories and analyses of their decisions
# - train a machine learning model to draft
#
# Strategy:
# Import JSON data (provided by MTGJSON)
# determine the rarities of all the cards in the set
# determine which cards are not present in boosters (like promos)
# determine the number of each rarity in boosters of this set (will probably have to hard-code these?)
# Build virtual packs with the correct number of each rarity, picking randomly from the set.
# Pull images of those cards from Scryfall
# Use a GUI of some kind (web-based?) to actually do the draft
# As the draft progresses, just remove those cards from the "boosters" and into each player's pools.
# Record this process and save it in a file for later analysis.
# Provide a way to export the drafted deck for play on untap.in or some other online MTG sim.


import json
import random
import datetime
import requests

num_players = 8
mythic_modifier = 8  # 1/8th chance the rare will be a mythic
pack_size = 15
base_url = "https://api.scryfall.com/cards/search"


# Getting dictionary
with open('MH1.json', 'r', encoding='utf-8') as json_file:
    set_dict = json.load(json_file)

# Printing JSON string
# print(json.dumps(MH1_dict, indent = 4, sort_keys=True))

# Iterate through the cards in the set and count the number of each rarity.
# Rarity can be: basic, common, uncommon, rare, or mythic
# counted_rarity_in_set = [0, 0, 0, 0, 0]
actual_rarity_in_set = [5, 101, 80, 53, 15]
# actual_rarity_in_set = [0, 101, 80, 53, 15] before adding snow lands to basics
# For MH1, the count should be: [0, 101, 80, 53, 15]
# Our results show 54 rares, because it includes the Buy A Box Promo, which isn't included in boosters!
# For MH1, the extra rare card is Flusterstorm.
# The extra commons are the Snow-Covered Lands.
# I need a way to determine cards like buy a box promos, which are not included in boosters,
# and to exclude them from the sims or use them differently (for the Snow Lands).
# NOTE: isBuyABox is now a field I can check.

# -------------------------------- RARITY COUNTS --------------------------------------------
# Create a list for each rarity
basics = []
commons = []
uncommons = []
rares = []
mythics = []

# Iterate through the dictionary and append the lists for each rarity
for k, v in set_dict.items():
    if k == 'cards':
        for card in v:  # v is a list of cards each with a dictionary of attributes
            # Check MYTHICS
            if card['rarity'] == 'mythic':
                if 'isPromo' in card:
                    print('---------------------PROMO!!!!! NOT INCLUDED!------------------------')
                    print(card['name'])
                    continue
                mythics.append(card)
            # Check RARES
            elif card['rarity'] == 'rare':
                if 'isPromo' in card:
                    print('---------------------PROMO!!!!! NOT INCLUDED!------------------------')
                    print(card['name'])
                    continue
                rares.append(card)
            # Check UNCOMMONS
            elif card['rarity'] == 'uncommon':
                if 'isPromo' in card:
                    print('---------------------PROMO!!!!! NOT INCLUDED!------------------------')
                    print(card['name'])
                    continue
                uncommons.append(card)
            # Check COMMONS
            # Special Case: SNOW LANDS
            elif card['rarity'] == 'common':
                if 'isPromo' in card:
                    print('---------------------PROMO!!!!! NOT INCLUDED!------------------------')
                    print(card['name'])
                    continue
                if 'Snow Land' in card['type']:
                    print('--------------SNOW LAND!!!!!-------------------')
                    print(card['name'])
                    # Add Snow Lands to basics instead.
                    basics.append(card)
                    continue
                commons.append(card)
                print(card['name'])
            # Check BASICS
            elif card['rarity'] == 'basic':
                if 'isPromo' in card:
                    print('---------------------PROMO!!!!! NOT INCLUDED!------------------------')
                    print(card['name'])
                    continue
                basics.append(card)

def rare_count(basics, commons, uncommons, rares, mythics, actual_rarity_in_set):
    print()
    print('Number of cards with each rarity (counted vs actually in set): ')
    print('Basics: ', len(basics), ' counted, vs. ', actual_rarity_in_set[0], 'actual.')
    print('Commons: ', len(commons), ' counted, vs. ', actual_rarity_in_set[1], 'actual.')
    print('Uncommons: ', len(uncommons), ' counted, vs. ', actual_rarity_in_set[2], 'actual.')
    print('Rares: ', len(rares), ' counted, vs. ', actual_rarity_in_set[3], 'actual.')
    print('Mythics: ', len(mythics), ' counted, vs. ', actual_rarity_in_set[4], 'actual.')


# Uncomment to check rarity counts
# rare_count(basics, commons, uncommons, rares, mythics, actual_rarity_in_set)


# -------------------------------- CREATE BOOSTER PACKS --------------------------------------------
# GENERATE PACKS
# 1 basic land (for MH1, SNOW LAND!)
# 10 commons
# 3 uncommons
# 1 rare (7/8 chance) or mythic (1/8 chance)

pack_one = [[0 for x in range(num_players)] for y in range(pack_size)]
pack_two = [[0 for x in range(num_players)] for y in range(pack_size)]
pack_three = [[0 for x in range(num_players)] for y in range(pack_size)]
# 2d array. Number of columns = num_players. Number of rows = # of cards in the pack (15).
for i in range(0, num_players): #
    pack_one[0][i] = random.sample(basics, 1)
    pack_two[0][i] = random.sample(basics, 1)
    pack_three[0][i] = random.sample(basics, 1)
    for j in range(1, 11):
        pack_one[j][i] = random.sample(commons, 1)
        pack_two[j][i] = random.sample(commons, 1)
        pack_three[j][i] = random.sample(commons, 1)
    for j in range(11, 14):
        pack_one[j][i] = random.sample(uncommons, 1)
        pack_two[j][i] = random.sample(uncommons, 1)
        pack_three[j][i] = random.sample(uncommons, 1)

    if mythic_modifier*random.random() < 7:
        pack_one[14][i] = random.sample(rares, 1)
    else:
        pack_one[14][i] = random.sample(mythics, 1)

    if mythic_modifier * random.random() < 7:
        pack_two[14][i] = random.sample(rares, 1)
    else:
        pack_two[14][i] = random.sample(mythics, 1)

    if mythic_modifier * random.random() < 7:
        pack_three[14][i] = random.sample(rares, 1)
    else:
        pack_three[14][i] = random.sample(mythics, 1)


# PRINT PACKS
def print_packs(p_one, p_two, p_three):
    # Print Pack One
    for i in range(0, num_players):
        for j in range(0, pack_size):
            print('Pack: 1   Player: ', i + 1, '  Card #: ', j + 1, ', ', p_one[j][i][0]['name'], ' - ', p_one[j][i][0]['rarity'])

    # Print Pack Two
    for i in range(0, num_players):
        for j in range(0, pack_size):
            print('Pack: 2   Player: ', i + 1, '  Card #: ', j + 1, ', ', p_two[j][i][0]['name'], ' - ', p_two[j][i][0]['rarity'])

    # Print Pack Three
    for i in range(0, num_players):
        for j in range(0, pack_size):
            print('Pack: 3   Player: ', i + 1, '  Card #: ', j + 1, '  ', p_three[j][i][0]['name'], ' - ', p_three[j][i][0]['rarity'])


# print_packs(pack_one, pack_two, pack_three)

# ------------------------------ OUTPUT SCRYFALL IMG URLS FOR PACKS ---------------------------------------
# Request img urls from Scryfall
def request_card(requested_card):

    # print('')
    # print(f"==========Processing: {requested_card}==========")

    processed = True
    failure = ""
    details = None

    # print(f"requesing card {requested_card}")

    resp = requests.get(base_url, params={'q' : requested_card})

    if resp.status_code == requests.codes['ok']:

        print(f"request for {requested_card} successful")
        image_url = resp.json()['data'][0]['image_uris']['png']

    else:
        print(f"Bad response from API query for card {requested_card}, status code {resp.status_code}")
        processed = False
        failure = "bad response from query API"
        details = resp.status_code
        exit(1)

    return image_url


# Collect PNG image links from Scryfall into a dict "boosters"
def save_packs(p_one, p_two, p_three, num_players, pack_size):
    booster1 = [['' for x in range(num_players)] for y in range(pack_size)]
    booster2 = [['' for x in range(num_players)] for y in range(pack_size)]
    booster3 = [['' for x in range(num_players)] for y in range(pack_size)]
    for i in range(0, num_players):
        for j in range(0, pack_size):
            print('Card: ', j+1, ' Player: ', i+1)
            booster1[j][i] = request_card(p_one[j][i][0]['name'])
            booster2[j][i] = request_card(p_two[j][i][0]['name'])
            booster3[j][i] = request_card(p_three[j][i][0]['name'])
    boosters = [booster1, booster2, booster3]
    return boosters


boosters_to_draft = save_packs(pack_one, pack_two, pack_three, num_players, pack_size)

now = datetime.datetime.now()
t = str(now.strftime("%Y-%m-%d_%H-%M"))

booster1 = 'pack1_img_urls_' + t + '.txt'
with open(booster1, 'w') as outfile:
    json.dump(boosters_to_draft[0], outfile)

booster2 = 'pack2_img_urls_' + t + '.txt'
with open(booster2, 'w') as outfile:
    json.dump(boosters_to_draft[1], outfile)

booster3 = 'pack3_img_urls_' + t + '.txt'
with open(booster3, 'w') as outfile:
    json.dump(boosters_to_draft[2], outfile)

