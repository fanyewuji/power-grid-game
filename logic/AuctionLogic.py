import tkinter as tk
from tkinter import messagebox

class AuctionLogic:
    def __init__(self, card_id, players, on_auction_end_callback):
        self.card_id = card_id
        self.players = players
        self.current_bid = int(card_id) - 1
        self.active_bidder_index = 0
        self.passed_players = []
        self.initial_bid_submitted = False
        self.auction_ended = False
        self.on_auction_end = on_auction_end_callback  # Callback to notify when auction ends

    def decrease_bid(self, bid_amount):
        if not self.initial_bid_submitted and bid_amount >= self.current_bid:
            return True
        elif self.initial_bid_submitted and bid_amount > self.current_bid:
            return True
        else:
            return False

    def submit_bid(self, bid_amount):
        active_player = self.players[self.active_bidder_index]
        if bid_amount > self.current_bid and bid_amount <= active_player.money:
            self.current_bid = bid_amount
            self.next_bidder()
            if not self.initial_bid_submitted:
                self.initial_bid_submitted = True
            return True, None  # Success
        elif bid_amount > active_player.money:
            return False, "Insufficient Funds. You do not have enough money to make this bid."
        else:
            return False, "Invalid Bid. Your bid must be higher than the current bid."

    def pass_bid(self):
        if not self.initial_bid_submitted:
            return False, "The player who started the bid can not pass."
        else:
            self.passed_players.append(self.players[self.active_bidder_index])
            self.next_bidder()
            return True, None

    def next_bidder(self):
        remaining_bidders = [player for player in self.players if player not in self.passed_players]
        if len(remaining_bidders) == 1:
            self.auction_ended = True
            self.end_auction(remaining_bidders[0])
        else:
            self.active_bidder_index = (self.active_bidder_index + 1) % len(self.players)
            while self.players[self.active_bidder_index] in self.passed_players:
                self.active_bidder_index = (self.active_bidder_index + 1) % len(self.players)

    def end_auction(self, winner):
        # Notify the game that the auction has ended
        self.on_auction_end(winner, self.card_id, self.current_bid)
