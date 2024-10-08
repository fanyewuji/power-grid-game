import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json
from utils.constants import RES_TOKEN_POS

class PowerGridUI:
    def __init__(self, root, get_game_state, action_handler):
        self.root = root
        self.root.title("Power Grid")
        self.root.geometry("1080x700+120+10")

        self.get_game_state = get_game_state
        self.game_state = self.get_game_state()
        print(f'get state: {self.get_game_state()}')
        self.resources = self.game_state["resources"]
        self.resource_image_ids = []

        self.action_handler = action_handler
        
        # Create main layout frames
        self.create_scrollable_container()
        self.create_main_frames()
        
        # Load and place the map image
        self.load_map()

        # Load the tile image containing all power plant cards
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tile_image_path = os.path.join(current_dir, '..', 'assets', 'cards.png')
        self.tile_image = Image.open(tile_image_path)

        coal_image_path = os.path.join(current_dir, '..', 'assets', 'coal.png')
        oil_image_path = os.path.join(current_dir, '..', 'assets', 'oil.png')
        trash_image_path = os.path.join(current_dir, '..', 'assets', 'trash.png')
        uranium_image_path = os.path.join(current_dir, '..', 'assets', 'uranium.png')
        
        coal_image = ImageTk.PhotoImage(Image.open(coal_image_path).resize((10, 15), Image.Resampling.LANCZOS))
        oil_image = ImageTk.PhotoImage(Image.open(oil_image_path).resize((10, 15), Image.Resampling.LANCZOS))
        trash_image = ImageTk.PhotoImage(Image.open(trash_image_path).resize((10, 15), Image.Resampling.LANCZOS))
        uranium_image = ImageTk.PhotoImage(Image.open(uranium_image_path).resize((10, 15), Image.Resampling.LANCZOS))
        self.resource_images = {'coal': coal_image, 'oil': oil_image, 'trash': trash_image, 'uranium': uranium_image}

        coal_image_sm = ImageTk.PhotoImage(Image.open(coal_image_path).resize((8, 12), Image.Resampling.LANCZOS))
        oil_image_sm = ImageTk.PhotoImage(Image.open(oil_image_path).resize((8, 12), Image.Resampling.LANCZOS))
        trash_image_sm = ImageTk.PhotoImage(Image.open(trash_image_path).resize((8, 12), Image.Resampling.LANCZOS))
        uranium_image_sm = ImageTk.PhotoImage(Image.open(uranium_image_path).resize((8, 12), Image.Resampling.LANCZOS))
        self.resource_images_sm = {'coal': coal_image_sm, 'oil': oil_image_sm, 'trash': trash_image_sm, 'uranium': uranium_image_sm}

        self.power_plant_cards = self.load_power_plant_cards()


    def create_scrollable_container(self):
        # Create a frame to contain everything and make it scrollable
        self.container_frame = tk.Frame(self.root)
        self.container_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        # Configure weight for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a canvas to enable scrolling
        self.canvas = tk.Canvas(self.container_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        self.scrollbar = tk.Scrollbar(self.container_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create another frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas)

        # Create a window inside the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Update the scroll region
        self.scrollable_frame.bind("<Configure>", lambda e: self.update_scroll_region())

        self.scrollable_frame.grid_rowconfigure(0, weight=0)
        self.scrollable_frame.grid_rowconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)


    def update_scroll_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def create_main_frames(self):
        # Create frame for the map
        self.map_frame = tk.Frame(self.scrollable_frame, width=590, height=800)
        self.map_frame.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsew")

        # Create frame for the power plant market
        self.market_frame = tk.Frame(self.scrollable_frame, width=460, height=230, bd=2, relief="solid")
        self.market_frame.grid(row=0, column=1, padx=0, pady=5, sticky="new")

        # Create frame for player info
        self.player_info_frame = tk.Frame(self.scrollable_frame, width=460, height=600, bd=2, relief="solid")
        self.player_info_frame.grid(row=1, column=1, padx=5, pady=5, sticky="new")


    def load_map(self):
        # Load the map image (replace 'path_to_map_image' with the actual path)
        self.map_canvas = tk.Canvas(self.map_frame, width=590, height=800)
        self.map_canvas.pack()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the map image
        map_image_path = os.path.join(current_dir, '..', 'assets', 'power_grid_germany_2.jpg')
        self.map_image = Image.open(map_image_path)
        self.map_image = self.map_image.resize((590, 800))
        self.map_image_tk = ImageTk.PhotoImage(self.map_image)
        
        # Display the image on the canvas
        self.map_canvas.create_image(0, 0, anchor=tk.NW, image=self.map_image_tk)

        # Add status labels on top of the canvas
        self.phase_label_canvas = self.map_canvas.create_text(
            30, 45, anchor=tk.NW, text="Phase: ", fill="yellow", font=("Helvetica", 11, "bold")
        )
        self.current_player_label_canvas = self.map_canvas.create_text(
            30, 65, anchor=tk.NW, text="Current Player: ", fill="yellow", font=("Helvetica", 11, "bold")
        )

        # Bind mouse click event to the canvas
        self.map_canvas.bind("<Button-1>", self.on_canvas_click)
    

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        print(f"Canvas clicked at ({x}, {y})")
        self.resources.refill_resources(4, 2)
        # Reload the resources on the canvas
        self.load_resources(self.resources.cur_resources)
        self.update_resource_section(self.resources.remaining_resources)
    
    
    def update_status(self, phase_name, current_player_name):
        self.map_canvas.itemconfig(self.phase_label_canvas, text=f"Phase: {phase_name}")
        self.map_canvas.itemconfig(self.current_player_label_canvas, text=f"Current Player: {current_player_name}")
    

    def load_resources(self, resources):
        # Clear existing resource images
        for image_id in self.resource_image_ids:
            self.map_canvas.delete(image_id)
        self.resource_image_ids.clear()

        for res_type, positions in RES_TOKEN_POS.items():
            for i, (cost, available) in enumerate(resources[res_type]):
                if available:
                    pos = positions[i]
                    image_id = self.map_canvas.create_image(pos[0], pos[1], anchor=tk.NW, image=self.resource_images_sm[res_type])
                    self.resource_image_ids.append(image_id)
    

    def load_power_plant_cards(self):
        # Load the JSON file into a dictionary
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, '..', 'power_plant_cards.json')
        with open(json_path, 'r') as json_file:
            cards_dict = json.load(json_file)
        return cards_dict


    def create_power_plant_market(self, step, power_plants_market):
        # Clear existing widgets in the market_frame
        for widget in self.market_frame.winfo_children():
            widget.destroy()
        
        # Determine the layout based on the game step
        if step == 3:
            cols, rows = 3, 2
        else:
            cols, rows = 4, 2
        
        # Create a canvas for the power plant market
        self.market_frame.grid_rowconfigure(0, weight=1)
        self.market_frame.grid_rowconfigure(1, weight=1)
        for i in range(cols):
            self.market_frame.grid_columnconfigure(i, weight=1)

        # Display power plant cards
        for idx, card_id in enumerate(power_plants_market):
            i, j = divmod(idx, cols)
            card_image = self.load_card_image(card_id=card_id)
            card_image_tk = ImageTk.PhotoImage(card_image)
            card_label = tk.Label(self.market_frame, image=card_image_tk)
            card_label.image = card_image_tk  # Keep a reference
            card_label.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

            # [TODO] step 3 would allow click event on all cards, step 1 and 2 only needs to add click event on row 1
            # Bind the click event to the card label
            card_label.bind("<Button-1>", lambda event, card_id=card_id: self.on_card_click(event, card_id))


    def on_card_click(self, event, card_id):
        response = messagebox.askyesno("Start Auction", f"Do you want to start an auction for power plant {card_id}?")
        if response:
            card_image = self.load_card_image(card_id=card_id)
            card_image = card_image.resize((100, 100), Image.Resampling.LANCZOS)
            card_image_tk = ImageTk.PhotoImage(card_image)
            self.action_handler('start_auction', card_id=card_id, card_image_tk=card_image_tk)


    def load_card_image(self, card_id):
        # Example coordinates and dimensions for each card in the tile image        
        if str(card_id) in self.power_plant_cards.keys():
            power_plant_card = self.power_plant_cards[str(card_id)]
            x, y, width, height = power_plant_card["col_index"] * 100, power_plant_card["row_index"] * 100, 100, 100
            card_image = self.tile_image.crop((x, y, x + width, y + height))
            return card_image
        else:
            raise ValueError("Invalid card_id")


    def create_player_info(self, players):
        # Clear existing widgets in player_info_frame
        for widget in self.player_info_frame.winfo_children():
            widget.destroy()
        
        self.control_frames = {} # Keep references to control frames

        power_plant_card_size = 60 if len(players) > 4 else 80
        for player in players:
            player_section = tk.Frame(self.player_info_frame, bd=2, relief="solid", padx=10, pady=0)
            player_section.pack(fill=tk.BOTH, pady=5)

            player_name_label = tk.Label(player_section, text=player.name, fg=player.color)
            player_name_label.grid(row=0, column=0, columnspan=3, sticky="w")

            player_city_label = tk.Label(player_section, text=f"Cities: {player.cities}")
            player_city_label.grid(row=0, column=1, sticky="n")

            player_money_label = tk.Label(player_section, text=f"Money: {player.money}")
            player_money_label.grid(row=0, column=2, sticky="n")

            for j, power_plant_id in enumerate(player.power_plants):
                if j < 3:  # Ensure only up to 3 power plant cards are displayed
                    card_image = self.load_card_image(card_id=power_plant_id)
                    card_image = card_image.resize((power_plant_card_size, power_plant_card_size), Image.Resampling.LANCZOS)
                    card_image_tk = ImageTk.PhotoImage(card_image)
                    power_plant_label = tk.Label(player_section, image=card_image_tk)
                    power_plant_label.image = card_image_tk  # Keep a reference
                    power_plant_label.grid(row=1, column=j, padx=5, pady=5, sticky="nsew")
        
                    # Create labels for resources below each card
                    resource_frame = tk.Frame(player_section)
                    resource_frame.grid(row=2, column=j)
        
                    resources_for_card = player.resources.get(power_plant_id, {})
                    for res_type, amount in resources_for_card.items():
                        for _ in range(amount):
                            resource_label = tk.Label(resource_frame, image=self.resource_images[res_type])
                            resource_label.image = self.resource_images[res_type]  # Keep a reference
                            resource_label.pack(side=tk.LEFT)

            # Make the columns expand equally
            for j in range(3):
                player_section.grid_columnconfigure(j, weight=1)
            
            player_section.grid_columnconfigure(3, minsize=80)

            # Control panel in column 3
            control_frame = tk.Frame(player_section)
            control_frame.grid(row=0, column=3, rowspan=3, sticky="nsew")
            self.control_frames[player.name] = control_frame
    

    def update_player_control(self, current_player_name):
        current_state = self.get_game_state()
        cur_phase = current_state["phase"]
        cur_round = current_state["round"]

        for player_name, control_frame in self.control_frames.items():
            for widget in control_frame.winfo_children():
                widget.destroy()
            
            if player_name == current_player_name:
                if cur_phase == 'Auction' and cur_round > 1:
                    button = tk.Button(control_frame, text='Pass Auction', command=lambda pn=current_player_name: self.handle_pass(pn))
                    button.grid(row=1, column=0, pady=5)
    

    def handle_pass(self, player_name):
        response = messagebox.askyesno("Pass", f"{player_name}, are you sure you want to pass?")
        if response:
            self.action_handler('player_pass')
    

    def create_resource_section(self, remaining_resources):
        # Create a frame for resources under the map
        self.resource_frame = tk.Frame(self.map_frame, width=590, height=100, bd=2, relief="solid")
        self.resource_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.resource_frame.grid_rowconfigure(0, weight=1)
        self.resource_frame.grid_rowconfigure(1, weight=1)
        self.resource_frame.grid_columnconfigure(0, weight=1)
        self.resource_frame.grid_columnconfigure(1, weight=1)

        # Dictionary to hold resource labels for easy updating
        self.resource_labels = {}

        # Create labels for resources in a 2x2 grid
        resource_types = list(remaining_resources.keys())
        for i in range(2):
            for j in range(2):
                res_type = resource_types[i*2 + j]
                res_count = remaining_resources[res_type]
                resource_label = tk.Label(self.resource_frame, image=self.resource_images[res_type], text=f"{res_type.capitalize()} Left: {res_count}", compound="top")
                resource_label.image = self.resource_images[res_type]  # Keep a reference to avoid garbage collection
                resource_label.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.resource_labels[res_type] = resource_label

    
    def update_resource_section(self, remaining_resources):
        # Update the text of each resource label
        for res_type, label in self.resource_labels.items():
            res_count = remaining_resources[res_type]
            label.config(text=f"{res_type.capitalize()} Left: {res_count}")

