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
from AuctionLogic import AuctionLogic
from utils.constants import PHASES
import random

class PowerPlantMarket:
    def __init__(self):
        self.current_market = [] # List of card_ids

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


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.power_plants = []
        self.resources = {}
        self.money = 50
        self.cities = 0
        self.phase_completed = False

    def __repr__(self):
        return f"Player {self.name}, {self.color}, Money: {self.money}, Cities: {self.cities}, Resources: {self.resources}, Power Plants: {self.power_plants})"


class Game:
    def __init__(self, root):
        self.deck = Deck()
        self.players = []
        self.power_plant_market = PowerPlantMarket()
        self.colors = ['#FF0000', '#0000FF', '#008000', '#655802', '#800080', '#FFA500']  # Red, Blue, Green, Dark Yellow, Purple, Orange
        self.resources = Resources()
        
        self.step = 1
        self.phase_index = -1
        # round is useful when determining player order
        self.round = 1

        self.current_player_index = 0
        
        self.ui = PowerGridUI(root, self.get_game_state, self.handle_action)

        self.initialize_game_state()
        self.initialize_game_ui()
        self.sort_players()
        self.next_phase()
    
    def __repr__(self):
        return f"Game(Players: {self.players}, Power Plant Market: {self.power_plant_market})"
    
    def next_phase(self):
        self.phase_index = (self.phase_index + 1) % len(PHASES)
        self.current_player_index = 0
        for player in self.players:
            player.phase_completed = False

        self.ui.update_status(PHASES[self.phase_index], self.players[self.current_player_index].name)


    def initialize_game_state(self):
        self.initialize_players()
        self.initialize_power_plant_market()
    
    def initialize_game_ui(self):
        self.ui.create_power_plant_market(self.step, self.power_plant_market.current_market)
        self.ui.load_resources(self.resources.cur_resources)
        self.ui.create_resource_section(self.resources.remaining_resources)

    def initialize_players(self):
        player_names = ["Player 1", "Player 2", "Player 3", "Player 4", ]
        power_plants = [["16", "21"], ["19"], ["11", "18", "12"], ["15", "34"]]
        resources = [{"16": {"oil": 4}, "21": {"coal": 1, "oil": 1}}, {"19": {"trash": 3}}, {"11": {"uranium": 1}, "18": {}, "12": {"coal": 2}}, {"15": {"coal": 2}, "34": {"uranium": 2}}]
        random.shuffle(self.colors)
        pp_res_index = [i for i in range(len(player_names))]
        random.shuffle(pp_res_index)

        for i, name in enumerate(player_names):
            player = Player(name, self.colors[i])
            player.power_plants = power_plants[pp_res_index[i]]
            player.resources = resources[pp_res_index[i]]
            self.players.append(player)

    def initialize_power_plant_market(self):
        self.power_plant_market.current_market = self.deck.prepare_initial_deck()

    def handle_action(self, action, **kwargs):
        if action == 'start_auction':
            self.start_auction(kwargs['card_id'], kwargs['card_image_tk'])
        elif action == 'player_pass':
            self.player_pass()
        # Handle other actions...
    
    def sort_players(self):
        if self.round == 1:
            random.shuffle(self.players)
        else:
            self.players.sort(key=lambda player: (-player.cities, -max(map(int, player.power_plants))))
        self.ui.create_player_info(self.players)  # Update the UI with the new player order
    
    def get_game_state(self):
        game_state = {"power_plant_market": self.power_plant_market, "players": self.players, "resources": self.resources, "step": self.step, "phase": PHASES[self.phase_index], "round": self.round}

        return game_state
    
    def start_auction(self, card_id, card_image_tk):
        auction_players = [player for player in self.players if not player.phase_completed]
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
        winner.power_plants.append(card_id)  # Store card_id
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
        self.ui.create_power_plant_market(self.step, self.power_plant_market.current_market)
        
        # Update the player info UI
        self.ui.create_player_info(self.players)
        
        # Determine the next player to start the auction
        self.determine_next_player()

    
    def determine_next_player(self):
        print('next player')
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
                self.ui.update_status(PHASES[self.phase_index], self.players[self.current_player_index].name)
                self.ui.update_player_control(self.players[self.current_player_index].name)


    def player_pass(self):
        self.players[self.current_player_index].phase_completed = True
        self.determine_next_player()



if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    # Print the game state to verify
    print(game)
    root.mainloop()