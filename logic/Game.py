import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import tkinter as tk
from tkinter import messagebox
from ui.PowerGridUI import PowerGridUI
from ui.AuctionUI import AuctionUI
from Deck import Deck
from Resource import Resources
from Cities import Cities
from AuctionLogic import AuctionLogic
from utils.constants import PHASES, CITIES, REGION_LIMITS
import random


class PowerPlantMarket:
    def __init__(self):
        self.current_market = []  # List of card_ids

    def add_card_to_market(self, card_id):
        self.current_market.append(card_id)
        if card_id != "step3":
            self.current_market.sort(key=lambda x: int(x))

    def remove_lowest_card(self):
        self.current_market.pop(0)

    def remove_card_from_market(self, card_id):
        if card_id in self.current_market:
            self.current_market.remove(card_id)

    def __repr__(self):
        return f"PowerPlantMarket({self.current_market})"


class OwnedPowerPlant:
    def __init__(self, card):
        self.card = card  # The static card info from Deck.cards
        # Initialize dynamic resource state
        self.resources_on_card = {}
        self.resources_to_purchase = {}
        self.resources_to_power = {}

    def __repr__(self):
        return (
            f"OwnedPowerPlant({self.card.card_id}, Resources: {self.resources_on_card})"
        )


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.power_plants = []
        self.owned_power_plants = {}
        self.money = 50
        self.cities = []
        self.phase_completed = False
        self.money_to_pay = 0

    def __repr__(self):
        return (
            f"Player {self.name}, {self.color}, Money: {self.money}, "
            f"Cities: {self.cities}, Power Plants: {self.owned_power_plants}"
        )


class Game:
    def __init__(self, root):
        self.deck = Deck()
        self.players = []
        self.power_plant_market = PowerPlantMarket()
        self.colors = [
            "#FF0000",
            "#0000FF",
            "#008000",
            "#655802",
            "#800080",
            "#FFA500",
        ]  # Red, Blue, Green, Dark Yellow, Purple, Orange
        self.resources = Resources()
        self.cities = Cities()
        self.occupied_regions = set()

        self.step = 3
        self.phase_index = 1
        # round is useful when determining player order
        self.round = 1

        self.current_player_index = 0

        self.ui = PowerGridUI(root, self.get_game_state, self.handle_action)

        self.initialize_game_state()
        self.initialize_game_ui()
        self.sort_players()
        self.next_phase()

        self.max_regions = REGION_LIMITS[len(self.players)]

    def __repr__(self):
        return f"Game(Players: {self.players}, Power Plant Market: {self.power_plant_market})"

    def next_phase(self):
        self.phase_index = (self.phase_index + 1) % len(PHASES)
        print(f"NEXT PHASE: {self.phase_index}")
        self.current_player_index = 0
        for player in self.players:
            player.phase_completed = False

        self.ui.update_status(
            PHASES[self.phase_index], self.players[self.current_player_index].name
        )
        # [TODO] May need to sort players
        self.ui.create_player_info(self.players, PHASES[self.phase_index])
        self.ui.update_player_control()

    def initialize_game_state(self):
        self.initialize_players()
        self.initialize_power_plant_market()

    def initialize_game_ui(self):
        self.ui.create_power_plant_market(
            self.step, self.power_plant_market.current_market
        )
        self.ui.load_resources(self.resources.cur_resources)
        self.ui.create_resource_section(self.resources.remaining_resources)

    def initialize_players(self):
        player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
        power_plants = [["16", "21"], ["19"], ["11", "18", "12"], ["15", "34"]]
        pp_resources = [
            {"16": {"oil": 3}, "21": {"coal": 1, "oil": 1}},
            {"19": {"trash": 3}},
            {"11": {"uranium": 1}, "18": {}, "12": {"coal": 2}},
            {"15": {"coal": 2}, "34": {"uranium": 2}},
        ]
        random.shuffle(self.colors)
        pp_res_index = [i for i in range(len(player_names))]
        random.shuffle(pp_res_index)

        for i, name in enumerate(player_names):
            player = Player(name, self.colors[i])
            owned_pp_dict = {}
            for pp_card_id in power_plants[i]:
                pp_card_obj = self.deck.cards[pp_card_id]
                owned_pp = OwnedPowerPlant(pp_card_obj)
                owned_pp.resources_on_card = pp_resources[i].get(pp_card_id, {})
                owned_pp_dict[pp_card_id] = owned_pp
            player.owned_power_plants = owned_pp_dict
            self.players.append(player)

    def initialize_power_plant_market(self):
        self.power_plant_market.current_market = self.deck.prepare_initial_deck()

    def handle_action(self, action, **kwargs):
        if action == "start_auction":
            self.start_auction(kwargs["card_id"], kwargs["card_image_tk"])
        elif action == "player_pass":
            self.player_pass()
        elif action == "purchase_resources":
            self.confirm_purchase()
        elif action == "add_res_to_purchase":
            return self.add_res_to_purchase(kwargs["res_type"], kwargs["cost"])
        elif action == "put_back_res_to_purchase":
            return self.put_back_res_to_purchase(kwargs["card_id"], kwargs["res_type"])
        elif action == "can_build_house":
            return self.can_build_house(kwargs["city_name"])
        elif action == "build_house":
            return self.build_house(kwargs["city_name"], kwargs["cost"])

    def sort_players(self):
        if self.round == 1:
            random.shuffle(self.players)
        else:
            self.players.sort(
                key=lambda player: (
                    -len(player.cities),
                    -max(
                        [int(card_id) for card_id in player.owned_power_plants.keys()]
                    ),
                )
            )

    def get_game_state(self):
        game_state = {
            "power_plant_market": self.power_plant_market,
            "players": self.players,
            "resources": self.resources,
            "step": self.step,
            "phase": PHASES[self.phase_index],
            "round": self.round,
            "current_player_index": self.current_player_index,
        }

        return game_state

    def start_auction(self, card_id, card_image_tk):
        auction_players = [
            player for player in self.players if not player.phase_completed
        ]
        self.auction_logic = AuctionLogic(card_id, auction_players, self.on_auction_end)
        self.auction_ui = AuctionUI(self.ui.root, self.auction_logic, card_image_tk)

    def on_auction_end(self, winner, card_id, final_bid):
        # Close the auction window
        self.auction_ui.close_window()

        # Show a message box to announce the winner
        message = f"{winner.name} won the auction for power plant {card_id} with a bid of {final_bid}."
        messagebox.showinfo("Auction Result", message)

        # Update the player's money and power plants
        winner.money -= final_bid
        # Create a new OwnedPowerPlant using the card from the deck:
        card_obj = self.deck.cards.get(card_id)
        new_owned_pp = OwnedPowerPlant(card_obj)
        winner.owned_power_plants[card_id] = new_owned_pp

        winner.phase_completed = True

        # Remove the purchased power plant from the market
        self.power_plant_market.remove_card_from_market(card_id)

        # Draw the next card from the deck and add it to the market
        new_card_id = self.deck.draw_card()
        if new_card_id:
            self.power_plant_market.add_card_to_market(new_card_id)
        else:
            # Handle case when deck is empty
            pass  # Placeholder

        # Update the power plant market UI
        self.ui.create_power_plant_market(
            self.step, self.power_plant_market.current_market
        )

        # Update the player info UI
        self.ui.create_player_info(self.players, PHASES[self.phase_index])

        # Determine the next player to start the auction
        self.determine_next_player()

    def determine_next_player(self):
        print("next player")
        if not self.players[self.current_player_index].phase_completed:
            pass
        else:
            while self.current_player_index < len(self.players):
                if self.players[self.current_player_index].phase_completed:
                    self.current_player_index += 1
                else:
                    break

            # check if the last player has completed the current phase
            if self.current_player_index >= len(self.players):
                self.next_phase()
            else:
                self.ui.update_status(
                    PHASES[self.phase_index],
                    self.players[self.current_player_index].name,
                )
                self.ui.update_player_control()

    def player_pass(self):
        self.players[self.current_player_index].phase_completed = True
        self.determine_next_player()

    def can_hold_resource(self, owned_pp, res_type):
        card_type = owned_pp.card.card_type
        print(f"CARD TYPE: {card_type}")
        print(f"RES TYPE: {res_type}")
        if card_type == "renewable":
            return False
        if card_type == "hybrid":
            if res_type not in ["coal", "oil"]:
                return False
        else:
            if card_type != res_type:
                return False

        cur_token_num = sum(owned_pp.resources_on_card.values())
        purchase_token_num = sum(owned_pp.resources_to_purchase.values())
        if cur_token_num + purchase_token_num < 2 * owned_pp.card.resource_number:
            return True
        return False

    def get_valid_cards_for_res(self, res_type):
        current_player = self.players[self.current_player_index]
        valid_cards = []
        for card_id, owned_pp in current_player.owned_power_plants.items():
            if self.can_hold_resource(owned_pp, res_type):
                valid_cards.append(card_id)
        return valid_cards

    def add_res_to_purchase(self, res_type, cost):
        current_player = self.players[self.current_player_index]
        valid_cards = self.get_valid_cards_for_res(res_type)

        if not valid_cards:
            return {
                "success": False,
                "message": "You don't have a power plant card to hold this, please choose another resource type.",
            }

        if cost > current_player.money:
            return {"success": False, "message": "You don't have enough money to pay"}

        if len(valid_cards) == 1:
            card_id = valid_cards[0]
        else:
            # More than one valid card: ask the UI to display a selection menu.
            card_id = self.ui.show_power_plant_selection_menu(
                valid_cards, res_type, cost
            )
            if not card_id:
                return {"success": False, "message": "No power plant selected."}

        owned_pp = current_player.owned_power_plants[card_id]
        owned_pp.resources_to_purchase[res_type] = (
            owned_pp.resources_to_purchase.get(res_type, 0) + 1
        )
        current_player.money_to_pay += cost
        if self.resources.remove_left_most_resources(res_type):
            self.ui.load_resources(self.resources.cur_resources)
            self.ui.update_player_info(current_player, PHASES[self.phase_index])
            self.ui.update_player_control()

            return {"success": True}
        else:
            return {"success": False, "message": "No available resource token found."}

    def put_back_res_to_purchase(self, card_id, res_type):
        current_player = self.players[self.current_player_index]
        owned_pp = current_player.owned_power_plants.get(card_id)
        if not owned_pp:
            return {"success": False, "message": "Power plant not found."}
        if owned_pp.resources_to_purchase.get(res_type, 0) <= 0:
            return {
                "success": False,
                "message": f"No {res_type} resource in purchase list.",
            }

        # Retrieve the cost of the token being put back.
        cost = self.resources.add_back_left_most_resource(res_type)
        if cost > 0:
            owned_pp.resources_to_purchase[res_type] -= 1
            current_player.money_to_pay -= cost

            self.ui.load_resources(self.resources.cur_resources)
            self.ui.update_player_info(current_player, PHASES[self.phase_index])
            self.ui.update_player_control()
            return {"success": True}
        else:
            return {
                "success": False,
                "message": "Could not add resource back to market.",
            }

    def confirm_purchase(self):
        current_player = self.players[self.current_player_index]

        for card_id, owned_pp in current_player.owned_power_plants.items():
            # For each resource type, move resources from resources_to_purchase to resources_on_card
            for res_type, purchase_amount in owned_pp.resources_to_purchase.items():
                owned_pp.resources_on_card[res_type] = (
                    owned_pp.resources_on_card.get(res_type, 0) + purchase_amount
                )
            owned_pp.resources_to_purchase = {}

        current_player.money -= current_player.money_to_pay
        current_player.money_to_pay = 0
        self.ui.update_player_info(current_player, PHASES[self.phase_index])
        current_player.phase_completed = True
        self.determine_next_player()

    def can_build_house(self, city_name):
        current_player = self.players[self.current_player_index]
        # Region‐limit check
        region = CITIES[city_name]["region"]
        is_new_region = region not in self.occupied_regions
        if is_new_region and len(self.occupied_regions) + 1 > self.max_regions:
            return {
                "success": False,
                "message": f"Cannot build a house in region {region!r}: limit is {self.max_regions}",
            }

        if city_name in current_player.cities:
            return {
                "success": False,
                "message": f"You have built a house in {city_name}",
            }

        # Step limit check
        if len(self.cities.built_cities.get(city_name, [])) >= self.step:
            return {
                "success": False,
                "message": f"Cannot build another house in {city_name} at current step",
            }

        # Zero‐cost neighbor rule
        for neighbor, cost in CITIES[city_name]["neighbors"]:
            if cost == 0 and neighbor in current_player.cities:
                return {
                    "success": False,
                    "message": f"Cannot build in {city_name} because you have built in its 0‑cost neighbor {neighbor}",
                }
            
        # Compute costs
        build_cost = self.cities.get_build_cost(city_name)
        connection_cost = self.cities.get_connection_cost(city_name, current_player.cities)
        total_cost = build_cost + connection_cost

        # Affordability
        if total_cost > current_player.money:
            return {
                "success": False,
                "message": f"Not enough money to build the city: need {total_cost}",
            }

        return {"success": True, "cost": total_cost}

    def build_house(self, city_name, cost):
        current_player = self.players[self.current_player_index]

        current_player.money -= cost
        current_player.cities.append(city_name)
        self.occupied_regions.add(CITIES[city_name]["region"])
        if city_name in self.cities.built_cities:
            self.cities.built_cities[city_name].append(current_player.name)
        else:
            self.cities.built_cities[city_name] = [current_player.name]
        
        self.ui.update_player_info(current_player, PHASES[self.phase_index])
        print(f"Built Citeis: {self.cities.built_cities}")
        self.ui.add_house(
            city_name, current_player.color, len(self.cities.built_cities[city_name])
        )


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    # Print the game state to verify
    print(game)
    root.mainloop()
