import json
from pathlib import Path
import os

# Read in the JSON
tarot_json_path = Path("./assets/tarot-deck-setup.json")
with open(tarot_json_path, 'r') as json_file:
    deck_dict = json.load(json_file)
# Flatten out the list
flat_deck = deck_dict["MajorArcana"]+\
    deck_dict["MinorArcana"]["Wands"]+\
    deck_dict["MinorArcana"]["Cups"]+\
    deck_dict["MinorArcana"]["Swords"]+\
    deck_dict["MinorArcana"]["Pentacles"]
print(flat_deck)
flat_deck = [(f"{i:02d}",card) for (i,card) in zip(range(1,79),flat_deck)]
print(flat_deck)

# Find the JPEGs
full_image_path = Path("./assets/cardfaces/fullimages")
tarot_jpgs = sorted(full_image_path.glob("*.jpg"))

# For each of the files, also look at the supposed corresponding ID
for (card_file,(id,name)) in zip(tarot_jpgs,flat_deck):
    card_stem = card_file.stem
    found_id = card_stem.split("_")[1]
    # Each file has numbers_id_numbers.jpg
    if id == found_id:
        # Have a match on the cards and can rename
        new_card = Path(card_file.parent,f'{id}_{name.replace(" ","_")}.jpg')
        print(f'Renaming: {card_file} to {new_card}')
        os.rename(card_file,new_card)
    else:
        # Did not fit pattern, probably already converted
        print(f'Could not rename: {card_file}')
