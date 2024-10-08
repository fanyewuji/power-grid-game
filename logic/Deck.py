import json
import random
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
cards_json_path = os.path.join(current_dir, '..', 'power_plant_cards.json')

class Card:
    def __init__(self, card_id, row_index, col_index, card_type, resource_number, cities_to_power):
        self.card_id = card_id
        self.row_index = row_index
        self.col_index = col_index
        self.card_type = card_type
        self.resource_number = resource_number
        self.cities_to_power = cities_to_power

    def __repr__(self):
        return f"Card({self.card_id}, {self.card_type}, {self.resource_number}, {self.cities_to_power})"

class Deck:
    def __init__(self):
        self.cards = {}
        self.stack_card_ids = []
        self.load_cards(cards_json_path)
    
    def __repr__(self):
        return f"Deck({self.stack_card_ids})"

    def load_cards(self, json_path):
        with open(json_path, 'r') as json_file:
            cards_data = json.load(json_file)
            for card_id, card_info in cards_data.items():
                card = Card(
                    card_id=card_id,
                    row_index=card_info['row_index'],
                    col_index=card_info['col_index'],
                    card_type=card_info['type'],
                    resource_number=card_info['resource_number'],
                    cities_to_power=card_info['cities_to_power']
                )
                self.cards[card_id] = card

        # Initialize stack_card_ids with all card IDs
        self.stack_card_ids = list(self.cards.keys())

    def prepare_initial_deck(self):
        # Remove specific card IDs from the initial deck
        initial_removals = ['3', '4', '5', '6', '7', '8', '9', '10']
        for card_id in initial_removals:
            if card_id in self.stack_card_ids:
                self.stack_card_ids.remove(card_id)
        
        # Shuffle the remaining deck, except 13 and step3
        self.stack_card_ids.remove('13')
        self.stack_card_ids.remove('step3')
        random.shuffle(self.stack_card_ids)
        
        # Put 13 on top and step3 on the bottom
        self.stack_card_ids.insert(0, '13')
        self.stack_card_ids.append('step3')
        
        return initial_removals

    def draw_card(self):
        if self.stack_card_ids:
            return self.stack_card_ids.pop(0)
        return None

    def put_back(self, card_id):
        self.stack_card_ids.append(card_id)
    
    def shuffle(self):
        random.shuffle(self.current_card_ids)


