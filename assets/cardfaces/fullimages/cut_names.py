import json
from pathlib import Path
import os

# Read in the JSON
tarot_json_path = Path("./assets/tarot_deck_numbered.json")
with open(tarot_json_path, 'r') as json_file:
    deck_array = json.load(json_file, parse_int=lambda id: int(id) if id.isnumeric() else id)
print(deck_array)

# Find the JPEGs
full_image_path = Path("./assets/cardfaces/fullimages")
tarot_jpgs = sorted(full_image_path.glob("*.jpg"))

# For each of the files, also look at the supposed corresponding ID
for (card_file,card) in zip(tarot_jpgs,deck_array):
    card_stem = card_file.stem
    found_id = card_stem.split("_")[1]
    # Each file has numbers_id_numbers.jpg
    if card["ordering"]+1 == int(found_id):
        # Have a match on the cards and can rename
        new_card = Path(card_file.parent,f'{card["ordering"]}_{card["name"].replace(" ","_")}.jpg')
        print(f'Renaming: {card_file} to {new_card}')
        os.rename(card_file,new_card)
    else:
        # Did not fit pattern, probably already converted
        print(f'Could not rename: {card_file}')
