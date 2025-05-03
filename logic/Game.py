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
from utils.constants import PHASES, CITIES, REGION_LIMITS, CITIES_TO_CASH
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
        self.resources_on_hold = {}

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
        self.left_resources_from_removed_pp = {}

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

        self.step = 1
        self.phase_index = -1
        # round is useful when determining player order
        self.round = 0

        self.current_player_index = 0

        self.initialize_game_state()

        self.ui = PowerGridUI(root, self.get_game_state, self.handle_action)
        self.initialize_game_ui()
        self.next_phase()

        # [TODO] choose regions before game starts
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
        if PHASES[self.phase_index] == "Auction":
            self.round += 1
            self.sort_players()
            print(f"Round: {self.round}")
        elif PHASES[self.phase_index] == "Resources":
            if self.round == 1:
                self.sort_players()
            self.players.reverse()
        
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
        power_plants = [["16", "21", "29"], ["19"], ["11", "12"], ["15", "34"]]
        pp_resources = [
            {"16": {"oil": 3}, "21": {"coal": 1, "oil": 1}},
            {"19": {"trash": 3}},
            {"11": {"uranium": 1}, "12": {"coal": 1, "oil": 1}},
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

            # [TODO] Can be removed later when the last phase is implemented
            for city_name, player_names in self.cities.built_cities.items():
                for city_owner_name in player_names:
                    if name == city_owner_name:
                        player.cities.append(city_name)
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
        
        elif action == "confirm_left_over_res_allocation":
            self.confirm_left_over_res_allocation(kwargs["player"])
        
        elif action == "get_possible_pp_for_left_res":
            return self.get_possible_pp_for_left_res(kwargs["player"], kwargs["res_type"])
        
        elif action == "add_left_over_res_on_hold":
            return self.add_left_over_res_on_hold(kwargs["player"], kwargs["card_id"], kwargs["res_type"])

        elif action == "put_back_res_to_left_over":
            return self.put_back_res_to_left_over(kwargs["player"], kwargs["card_id"], kwargs["res_type"])
        
        elif action == "add_res_to_power":
            return self.add_res_to_power(kwargs["card_id"], kwargs["res_type"])
        
        elif action == "remove_res_from_power":
            return self.remove_res_from_power(kwargs["card_id"], kwargs["res_type"])
        
        elif action == "can_build_house":
            return self.can_build_house(kwargs["city_name"])
        
        elif action == "build_house":
            self.build_house(kwargs["city_name"], kwargs["cost"])
        
        elif action == "generate_power":
            return self.generate_power()
        
        elif action == "get_valid_cards_for_resource_move":
            return self.get_valid_cards_for_resource_move(kwargs["player"], kwargs["card_id"], kwargs["res_type"])
        elif action == "execute_move_resource":
            return self.execute_move_resource(kwargs["player"], kwargs["source_card_id"], kwargs["target_card_id"], kwargs["res_type"])

    def sort_players(self):
        if self.round == 1 and PHASES[self.phase_index] == "Auction":
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
            "built_cities": self.cities.built_cities,
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

        winner.money -= final_bid
        card_obj = self.deck.cards.get(card_id)
        new_owned_pp = OwnedPowerPlant(card_obj)
        # Add the new owned power plant first
        winner.owned_power_plants[card_id] = new_owned_pp

        need_to_allocate_resources = False
        if len(winner.owned_power_plants) > 3:
            power_plant_to_remove = self.ui.show_power_plant_removal_menu(
                [cp for cp in list(winner.owned_power_plants.keys()) if cp != card_id]
            )
            removed_pp = winner.owned_power_plants.pop(power_plant_to_remove)
            if sum(removed_pp.resources_on_card.values()) > 0:
                # Move resources from the removed power plant to new_owned_pp if possible,
                # If not, leave them unallocated.
                can_move_res_to_new_pp = self.can_move_resources_to_new_pp(new_owned_pp, removed_pp.resources_on_card)

                print("CAN MOVE RES: ", can_move_res_to_new_pp)
                if not can_move_res_to_new_pp:
                    need_to_allocate_resources = True
                    winner.left_resources_from_removed_pp = removed_pp.resources_on_card
                    self.ui.update_player_info(winner, PHASES[self.phase_index])
                    self.ui.update_player_control(winner)
        
        self.remove_power_plant_from_market(card_id)

        if not need_to_allocate_resources:
            winner.phase_completed = True

            # Update the player info UI
            self.ui.create_player_info(self.players, PHASES[self.phase_index])

            # Determine the next player to start the auction
            self.determine_next_player()
    
    def remove_power_plant_from_market(self, card_id):
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
        self.ui.create_power_plant_market(self.step, self.power_plant_market.current_market)
        

    def determine_next_player(self):
        print("next player")
        if not self.players[self.current_player_index].phase_completed:
            self.ui.update_player_control()
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
        phase = PHASES[self.phase_index]

        if card_type == "renewable":
            return False
        if card_type == "hybrid":
            if res_type not in ["coal", "oil"]:
                return False
        else:
            if card_type != res_type:
                return False

        cur_token_num = sum(owned_pp.resources_on_card.values())
        if phase == "Resources":
            purchase_token_num = sum(owned_pp.resources_to_purchase.values())
        else:
            # this is the case when the player is in the auction phase and has not confirmed left-over resource allocation   
            purchase_token_num = sum(owned_pp.resources_on_hold.values())
        
        print(
            f"cur_token_num: {cur_token_num}, purchase_token_num: {purchase_token_num}, resource_number: {owned_pp.card.resource_number}")
        if cur_token_num + purchase_token_num < 2 * owned_pp.card.resource_number:
            return True
        return False
    
    def get_possible_pp_for_left_res(self, player, res_type):
        candidates = []
        for card_id, owned_pp in player.owned_power_plants.items():
            if self.can_hold_resource(owned_pp, res_type):
                candidates.append(card_id)
        
        return candidates

    def can_move_resources_to_new_pp(self, new_owned_pp, removed_resources):
        """
        Attempts to move resource tokens from removed_resources to new_owned_pp.
        If True, also move the resources to new_owned_pp.
        """
        if new_owned_pp.card.card_type == "renewable":
            return False

        if len(removed_resources) > 1 and new_owned_pp.card.card_type != "hybrid":
            return False

        if len(removed_resources) > 1 and sum(removed_resources.values()) > 2 * new_owned_pp.card.resource_number:
            return False
        
        if len(removed_resources) ==1:
            if new_owned_pp.card.card_type != "hybrid":
                if next(iter(removed_resources.keys())) != new_owned_pp.card.card_type:
                     return False
            else:
                if next(iter(removed_resources.keys())) not in ["coal", "oil"]:
                    return False

        if len(removed_resources) ==1 and next(iter(removed_resources.values())) > 2 * new_owned_pp.card.resource_number:
            return False
        
        for res, count in removed_resources.items():
            new_owned_pp.resources_on_card[res] = count
    
        return True

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
            return {"success": False, "message": "Could not add resource back to market."}
    
    def put_back_res_to_left_over(self, player, card_id, res_type):
        owned_pp = player.owned_power_plants.get(card_id)
        if not owned_pp:
            return {"success": False, "message": "Power plant not found."}
        if owned_pp.resources_on_hold.get(res_type, 0) <= 0:
            return {
                "success": False,
                "message": f"No {res_type} resource on hold for this card {card_id}.",
            }
    
        owned_pp.resources_on_hold[res_type] -= 1
        player.left_resources_from_removed_pp[res_type] = player.left_resources_from_removed_pp.get(res_type, 0) + 1
        self.ui.update_player_info(player, PHASES[self.phase_index])

        return {"success": True}
    
    def add_res_to_power(self, card_id, res_type):
        current_player = self.players[self.current_player_index]
        owned_pp = current_player.owned_power_plants.get(card_id)
        if not owned_pp:
            return {"success": False, "message": "Power plant not found."}
        if owned_pp.resources_on_card.get(res_type, 0) <= 0:
            return {
                "success": False,
                "message": f"No {res_type} resource on card.",
            }
        
        owned_pp.resources_on_card[res_type] -= 1
        owned_pp.resources_to_power[res_type] = (
            owned_pp.resources_to_power.get(res_type, 0) + 1
        )
        self.ui.update_player_info(current_player, PHASES[self.phase_index])
        return {"success": True}

    def remove_res_from_power(self, card_id, res_type):
        current_player = self.players[self.current_player_index]
        owned_pp = current_player.owned_power_plants.get(card_id)
        if not owned_pp:
            return {"success": False, "message": "Power plant not found."}
        
        if owned_pp.resources_to_power.get(res_type, 0) <= 0:
            return {
                "success": False,
                "message": f"No {res_type} resource in power list.",
            }
        
        owned_pp.resources_to_power[res_type] -= 1
        owned_pp.resources_on_card[res_type] = (
            owned_pp.resources_on_card.get(res_type, 0) + 1
        )
        self.ui.update_player_info(current_player, PHASES[self.phase_index])
        return {"success": True}

    def add_left_over_res_on_hold(self, player, card_id, res_type):
        print(f"left resources: {player.left_resources_from_removed_pp}")

        owned_pp = player.owned_power_plants.get(card_id)
        print("owned pp: ", owned_pp)

        if player.left_resources_from_removed_pp[res_type] < 0:
            return False

        player.left_resources_from_removed_pp[res_type] -= 1
        owned_pp.resources_on_hold[res_type] = owned_pp.resources_on_hold.get(res_type, 0) + 1

        self.ui.update_player_info(player, PHASES[self.phase_index])

        return True

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
    
    def confirm_left_over_res_allocation(self, player):
        for owned_pp in player.owned_power_plants.values():
            for res_type, amount in owned_pp.resources_on_hold.items():
                if amount > 0:
                    owned_pp.resources_on_card[res_type] = owned_pp.resources_on_card.get(res_type, 0) + amount
            owned_pp.resources_on_hold = {}
        
        player.left_resources_from_removed_pp = {}

        player.phase_completed = True
        
        self.ui.create_player_info(self.players, PHASES[self.phase_index])
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
    
    def generate_power(self):
        current_player = self.players[self.current_player_index]
        cities_can_power = 0
        for owned_pp in current_player.owned_power_plants.values():
            if owned_pp.card.card_type == "renewable":
                cities_can_power += owned_pp.card.cities_to_power
            elif sum(owned_pp.resources_to_power.values()) > 0:
                if owned_pp.card.resource_number != sum(owned_pp.resources_to_power.values()):
                    return {"success": False, "message": f"Incorrect number of resources to power for power plant card: {owned_pp.card.card_id}"}
                cities_can_power += owned_pp.card.cities_to_power
        
        cities_can_power = min(cities_can_power, len(current_player.cities))
        cash = CITIES_TO_CASH[cities_can_power]
        self.resources.return_resources_to_remaining(current_player.owned_power_plants)
        current_player.money += cash
        self.ui.update_player_info(current_player, PHASES[self.phase_index])
        print(f'remaining resources: {self.resources.remaining_resources}')
        self.ui.update_resource_section(self.resources.remaining_resources)
        self.player_pass()

        return {"success": True, "message": f"Generated {cash} cash from {cities_can_power} cities"}

    def get_valid_cards_for_resource_move(self, player, source_card_id, res_type):
        valid = [cid for cid, pp in player.owned_power_plants.items() 
                 if cid != source_card_id and self.can_hold_resource(pp, res_type)]
        return valid

    def execute_move_resource(self, player, source_card_id, target_card_id, res_type):
        source_pp = player.owned_power_plants.get(source_card_id)
        target_pp = player.owned_power_plants.get(target_card_id)
        if not source_pp or not target_pp:
            return {"success": False, "message": "Power plant not found."}
        if source_pp.resources_on_card.get(res_type, 0) <= 0:
            return {"success": False, "message": "No resource to move."}
        source_pp.resources_on_card[res_type] -= 1
        target_pp.resources_on_card[res_type] = target_pp.resources_on_card.get(res_type, 0) + 1
        self.ui.update_player_info(player, PHASES[self.phase_index])
        return {"success": True}


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    # Print the game state to verify
    print(game)
    root.mainloop()
