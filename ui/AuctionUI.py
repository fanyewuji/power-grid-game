# auction_ui.py
import tkinter as tk
from tkinter import messagebox

class AuctionUI:
    def __init__(self, root, auction_logic, card_image_tk):
        self.root = root
        self.auction_logic = auction_logic
        self.card_image_tk = card_image_tk

        self.create_bid_window()

    def create_bid_window(self):
        self.bid_window = tk.Toplevel(self.root)
        self.bid_window.title(f"Bid for Power Plant {self.auction_logic.card_id}")
        self.bid_window.geometry("400x300+800+300")
        self.bid_window.protocol("WM_DELETE_WINDOW", self.on_close)  # Disable close button

        # Frame for the card image
        card_frame = tk.Frame(self.bid_window)
        card_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        card_label = tk.Label(card_frame, image=self.card_image_tk)
        card_label.image = self.card_image_tk  # Keep a reference to avoid garbage collection
        card_label.pack()

        # Frame for the bid info and controls
        bid_info_frame = tk.Frame(self.bid_window)
        bid_info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # Current highest bid
        self.current_bid_var = tk.IntVar(value=self.auction_logic.current_bid + 1)
        tk.Label(bid_info_frame, text="Current:").grid(row=0, column=0)
        tk.Label(bid_info_frame, textvariable=self.current_bid_var).grid(row=0, column=1)

        # Input box for current player's bid
        self.bid_value = tk.IntVar(value=self.auction_logic.current_bid + 1)
        bid_entry = tk.Entry(bid_info_frame, textvariable=self.bid_value, width=8)
        bid_entry.grid(row=1, column=0, columnspan=2)

        # Plus and minus buttons for bid adjustment
        plus_button = tk.Button(bid_info_frame, text="+", command=self.increase_bid)
        plus_button.grid(row=1, column=2, padx=5)

        minus_button = tk.Button(bid_info_frame, text="-", command=self.decrease_bid)
        minus_button.grid(row=1, column=3)

        # Submit and Pass buttons
        submit_button = tk.Button(bid_info_frame, text="Submit Bid", bg="#8FBC8F", command=self.submit_bid)
        submit_button.grid(row=2, column=0, columnspan=2, pady=5)

        pass_button = tk.Button(bid_info_frame, text="Pass", bg="#D3D3D3", command=self.pass_bid)
        pass_button.grid(row=2, column=2, columnspan=2, pady=5)

        # Frame for bid order
        bid_order_frame = tk.Frame(self.bid_window)
        bid_order_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

        tk.Label(bid_order_frame, text="Bid Order").grid(row=0, column=0, columnspan=4)

        self.player_labels = []
        for i, player in enumerate(self.auction_logic.players):
            label_text = player.name
            player_label = tk.Label(bid_order_frame, text=label_text, fg=player.color, font=("Arial", 10))
            player_label.grid(row=1, column=i)
            self.player_labels.append(player_label)

            # Set underline for the current player
            if i == self.auction_logic.active_bidder_index:
                player_label.config(font=("Arial", 10, "underline"))

            # Set strikethrough for players who have passed
            if player in self.auction_logic.passed_players:
                player_label.config(fg="gray", font=("Arial", 10, "overstrike"))
    
    def increase_bid(self):
        self.bid_value.set(self.bid_value.get() + 1)
    
    def decrease_bid(self):
        if self.auction_logic.decrease_bid(self.bid_value.get() - 1):
            self.bid_value.set(self.bid_value.get() - 1)
        else:
            self.show_error("Invalid Bid", "Your bid must be higher than the current bid.")

    def update_bid_display(self):
        # update current bid value and bid input value 
        self.current_bid_var.set(self.auction_logic.current_bid)
        self.bid_value.set(self.auction_logic.current_bid + 1)

        # update player labels            
        for i, player_label in enumerate(self.player_labels):
            player_label.config(font=("Arial", 10))  # Reset font
            if self.auction_logic.players[i] == self.auction_logic.players[self.auction_logic.active_bidder_index]:
                player_label.config(font=("Arial", 10, "underline"))
            if self.auction_logic.players[i] in self.auction_logic.passed_players:
                player_label.config(fg="gray", font=("Arial", 10, "overstrike"))

    def submit_bid(self):
        try:
            new_bid = int(self.bid_value.get())
        except ValueError:
            self.show_error("Invalid Bid", "Your bid must be an integer.")
            return

        success, error_message = self.auction_logic.submit_bid(new_bid)
        if success:
            if not self.auction_logic.auction_ended:
                self.update_bid_display()
        else:
            self.show_error("Bid Error", error_message)

    def pass_bid(self):
        success, error_message = self.auction_logic.pass_bid()

        if success and not self.auction_logic.auction_ended:
            self.update_bid_display()
        elif not success:
            self.show_error("Unable to Pass", error_message)

    def on_close(self):
        # Disable closing the window manually
        pass

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.bid_window)
    
    def close_window(self):
        self.bid_window.destroy()
