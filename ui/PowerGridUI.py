import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import json
from utils.constants import RES_TOKEN_POS, CITIES

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
        self.load_city_labels()
        self.load_houses()

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
        print(f"({x}, {y})")
        if event.y < 730:
            self.resources.refill_resources(4, 2)
            # Reload the resources on the canvas
            self.load_resources(self.resources.cur_resources)
            self.update_resource_section(self.resources.remaining_resources)
        
        self.check_click_city(x, y)
    
    def check_click_city(self, x, y):
        # Check if click is within 10px of any city position
        clicked_city = None
        for name, info in CITIES.items():
            cx, cy = info['pos']
            if abs(x - cx) <= 10 and abs(y - cy) <= 10:
                clicked_city = name
                city_x, city_y = cx, cy
                break

        if clicked_city:
            # Ask for build confirmation
            result = self.action_handler('can_build_house', city_name=clicked_city)
            if result is not None and isinstance(result, dict):
                if not result.get("success", False):
                    messagebox.showerror("Error", result.get("message", "Unable to build house"))
                    return
                else:
                    # Show connection costs to neighbors
                    self.city_cost_labels = []
                    for neighbor, cost in CITIES[clicked_city]['neighbors']:
                        nx, ny = CITIES[neighbor]['pos']
                        # midpoint, offset slightly downwards
                        mx = (city_x + nx) // 2
                        my = ((city_y + ny) // 2)
                        r = 12  # radius for circular background
                        # Draw circle
                        oval_id = self.map_canvas.create_oval(
                            mx - r, my - r, mx + r, my + r,
                            fill='white', outline=''
                        )
                        # Draw cost text
                        text_id = self.map_canvas.create_text(
                            mx, my,
                            text=str(cost),
                            font=('Helvetica', 8, 'bold')
                        )
                        self.map_canvas.tag_raise(oval_id)
                        self.map_canvas.tag_raise(text_id)
                        self.city_cost_labels.extend([oval_id, text_id])

                    response = messagebox.askyesno(
                        "Build House",
                        f"Do you want to build a house in {clicked_city}? The cost is {result['cost']}."
                    )

                    # Remove the cost labels regardless of choice
                    for lid in self.city_cost_labels:
                        self.map_canvas.delete(lid)
                    self.city_cost_labels.clear()

                    # If confirmed, call game logic handler
                    if response:
                        self.action_handler('build_house', city_name=clicked_city, cost=result['cost'])
    
    
    def update_status(self, phase_name, current_player_name):
        self.map_canvas.itemconfig(self.phase_label_canvas, text=f"Phase: {phase_name}")
        self.map_canvas.itemconfig(self.current_player_label_canvas, text=f"Current Player: {current_player_name}")
    
    def load_city_labels(self):
        """
        Overlay each city name on the map canvas, 15px below its defined coordinates.
        """
        # Remove any previously drawn city labels
        if hasattr(self, 'city_label_shapes'):
            for cid in self.city_label_shapes:
                self.map_canvas.delete(cid)
        else:
            self.city_label_shapes = []

        for name, info in CITIES.items():
            x, y = info['pos']
            # Draw text directly on the canvas
            text_id = self.map_canvas.create_text(
                x-18, y, 
                text=name, 
                font=('Arial', 8, 'bold'),
                fill='black',
                anchor='nw'
            )
            bbox = self.map_canvas.bbox(text_id)
            rect_id = self.map_canvas.create_rectangle(
                bbox[0]-2, bbox[1]-2,
                bbox[2]+2, bbox[3]+2,
                fill='lightgrey', outline=''
            )
            # Make sure rectangle is just behind its own text
            self.map_canvas.tag_lower(rect_id, text_id)

            self.city_label_shapes.extend([rect_id, text_id])
    
    def add_house(self, city_name, color, house_index):
        """
        Adds a house to the specified city on the map canvas.

        Args:
            city_name (str): The name of the city where the house will be added.
            color (str): The color of the house.
            house_index (int): The index of the house (1, 2, or 3).
        """
        if city_name not in CITIES:
            raise ValueError(f"City '{city_name}' does not exist in the CITIES dictionary.")

        x, y = CITIES[city_name]['pos']

        # Determine the position of the house based on the house index
        if house_index == 1:
            house_x, house_y = x, y - 10
        elif house_index == 2:
            house_x, house_y = x - 6, y
        elif house_index == 3:
            house_x, house_y = x + 6, y
        else:
            raise ValueError("Invalid house_index. Must be 1, 2, or 3.")

        # Draw the house as a square on the canvas
        house_size = 9  # Size of the square
        house_id = self.map_canvas.create_rectangle(
            house_x - house_size // 2, house_y - house_size // 2,
            house_x + house_size // 2, house_y + house_size // 2,
            fill=color, outline="white", width=2
        )

        # Ensure the house is on top of other items
        self.map_canvas.tag_raise(house_id)
    
    def load_houses(self):
        players = self.game_state["players"]
        built_cities = self.game_state["built_cities"]

        for player in players:
            for city_name, player_names in built_cities.items():
                for house_index, player_name in enumerate(player_names):
                    if player_name == player.name:
                        self.add_house(city_name, player.color, house_index + 1)
    
    def load_resources(self, resources):
        # Clear existing resource images
        for image_id in self.resource_image_ids:
            self.map_canvas.delete(image_id)
        self.resource_image_ids.clear()

        for res_type, positions in RES_TOKEN_POS.items():
            is_first_available = True
            for i, (cost, available) in enumerate(resources[res_type]):
                if available:
                    pos = positions[i]
                    image_id = self.map_canvas.create_image(pos[0], pos[1], anchor=tk.NW, image=self.resource_images_sm[res_type])
                    if is_first_available:
                        self.map_canvas.tag_bind(image_id, "<Button-1>", lambda event, res_type=res_type, cost=cost: self.handle_click_res_token(res_type, cost))
                    else:
                        self.map_canvas.tag_bind(image_id, "<Button-1>", lambda event: messagebox.showinfo("Alert", "Please purchase the resource token from the very left"))
                    self.resource_image_ids.append(image_id)
                    is_first_available = False

    def handle_click_res_token(self, res_type, cost):
        result = self.action_handler('add_res_to_purchase', res_type=res_type, cost=cost)
        
        # If the result indicates failure, show an error message.
        if result is not None and isinstance(result, dict) and not result.get("success", False):
            messagebox.showerror("Error", result.get("message", "Error adding resource"))
    
    def show_power_plant_selection_menu(self, valid_cards, res_type, cost):
        # For simplicity, we create a simple dialog with a listbox.
        # In a real implementation you might use a Toplevel window with radio buttons or similar.
        menu = tk.Toplevel(self.root)
        menu.title("Select a Power Plant")
        tk.Label(menu, text=f"Select a power plant to add {res_type} (cost {cost}):").pack(padx=10, pady=10)
        
        var = tk.StringVar(value=valid_cards[0])
        for card in valid_cards:
            tk.Radiobutton(menu, text=f"Power Plant {card}", variable=var, value=card).pack(anchor="w", padx=10)
        
        selected = [None]  # mutable container
        
        def on_confirm():
            selected[0] = var.get()
            menu.destroy()
        
        tk.Button(menu, text="OK", command=on_confirm).pack(pady=10)
        menu.wait_window()
        return selected[0]

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


    def create_player_info(self, players, phase):
        # Clear existing widgets in player_info_frame
        for widget in self.player_info_frame.winfo_children():
            widget.destroy()
        
        # Dictionaries to store references
        self.player_sections = {}            # Maps player name to their base section frame
        self.control_frames = {}             # Maps player name to their control panel
        self.card_image_labels = {}          # (player_name, card_id) -> ppw card image labels
        self.resource_frames = {}            # (player_name, card_id) -> resource frame
        self.resource_purchase_frames = {}   # (player_name, card_id) -> purchase frame
        self.resource_power_frames = {}   # (player_name, card_id) -> power frame

        self.power_plant_card_size = 60 if len(players) > 4 else 80
        for player in players:
            player_section = tk.Frame(self.player_info_frame, bd=2, relief="solid", padx=10, pady=0)
            player_section.pack(fill=tk.BOTH, pady=5)
            self.player_sections[player.name] = player_section

            # Control panel in column 3
            control_frame = tk.Frame(player_section)
            control_frame.grid(row=0, column=3, rowspan=3, sticky="nsew")
            self.control_frames[player.name] = control_frame

            # Iterate over player's owned power plants stored as dict
            self.update_player_info(player, phase)

            # Make the columns expand equally
            for j in range(3):
                player_section.grid_columnconfigure(j, weight=1)
            
            player_section.grid_columnconfigure(3, minsize=80)
    
    def update_player_info(self, player, phase):
        player_section = self.player_sections.get(player.name)
        is_initial_render = True
        if hasattr(player_section, "header_frame"):
            player_section.header_frame.destroy()
            is_initial_render = False

        header_frame = tk.Frame(player_section)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="w")
        player_section.header_frame = header_frame

        tk.Label(header_frame, text=player.name, fg=player.color).pack(side=tk.LEFT, padx=(0,10))
        tk.Label(header_frame, text=f"Cities: {len(player.cities)}").pack(side=tk.LEFT, padx=(0,10))
        tk.Label(header_frame, text=f"Money: {player.money}").pack(side=tk.LEFT)

        for j, (card_id, owned_pp) in enumerate(player.owned_power_plants.items()):
            if j < 3:  # Limit display to 3 power plants
                key = (player.name, card_id)

                if is_initial_render or phase == 'Auction':
                    if key in self.card_image_labels:
                        self.card_image_labels[key].destroy()
                    
                    card_image = self.load_card_image(card_id=card_id)
                    card_image = card_image.resize((self.power_plant_card_size, self.power_plant_card_size), Image.Resampling.LANCZOS)
                    card_image_tk = ImageTk.PhotoImage(card_image)
                    power_plant_label = tk.Label(player_section, image=card_image_tk)
                    power_plant_label.image = card_image_tk  # Keep a reference
                    power_plant_label.grid(row=1, column=j, padx=5, pady=5, sticky="nsew")
                    self.card_image_labels[key] = power_plant_label

                # RESOURCE FRAME: Create or update the resource frame for resources_on_card
                if key in self.resource_frames:
                    resource_frame = self.resource_frames[key]
                    for widget in resource_frame.winfo_children():
                        widget.destroy()

                resource_frame = tk.Frame(player_section)
                resource_frame.grid(row=1, column=j)
                self.resource_frames[key] = resource_frame
                
                for res_type, amount in owned_pp.resources_on_card.items():
                    for _ in range(amount):
                        lbl = tk.Label(resource_frame, image=self.resource_images[res_type])
                        lbl.image = self.resource_images[res_type]  # keep reference
                        lbl.pack(side=tk.LEFT)
                        lbl.bind("<Button-1>", lambda event, card_id=card_id, res_type=res_type: self.handle_click_res_on_card(card_id, res_type, phase))
                
                print(f'PHASE!: {phase}')
                if phase == "Resources": 
                    if key not in self.resource_purchase_frames:
                        purchase_frame = tk.Frame(player_section, bg="lightgray")
                        purchase_frame.grid(row=2, column=j, pady=2)
                        self.resource_purchase_frames[key] = purchase_frame
                    else:
                        purchase_frame = self.resource_purchase_frames[key]
                        for widget in purchase_frame.winfo_children():
                            widget.destroy()
                    
                    # Render resource icons for owned_pp.resources_to_purchase
                    for res_type, amount in owned_pp.resources_to_purchase.items():
                        for _ in range(amount):
                            lbl = tk.Label(purchase_frame, image=self.resource_images[res_type])
                            lbl.image = self.resource_images[res_type]  # keep reference
                            lbl.pack(side=tk.LEFT)
                            lbl.bind("<Button-1>", lambda event, card_id=card_id, res_type=res_type: self.handle_click_res_to_purchase(card_id, res_type))
                
                if phase == "Bureaucracy": 
                    if key not in self.resource_power_frames:
                        power_frame = tk.Frame(player_section, bg="lightgray")
                        power_frame.grid(row=2, column=j, pady=2)
                        self.resource_power_frames[key] = power_frame
                    else:
                        power_frame = self.resource_power_frames[key]
                        for widget in power_frame.winfo_children():
                            widget.destroy()
                    
                    # Render resource icons for owned_pp.resources_to_power
                    for res_type, amount in owned_pp.resources_to_power.items():
                        for _ in range(amount):
                            lbl = tk.Label(power_frame, image=self.resource_images[res_type])
                            lbl.image = self.resource_images[res_type]  # keep reference
                            lbl.pack(side=tk.LEFT)
                            lbl.bind("<Button-1>", lambda event, card_id=card_id, res_type=res_type: self.handle_click_res_to_power(card_id, res_type))
                

    def update_player_control(self):
        current_state = self.get_game_state()
        cur_phase = current_state["phase"]
        cur_round = current_state["round"]
        current_player_index = current_state["current_player_index"]
        current_player = current_state["players"][current_player_index]

        for player_name, control_frame in self.control_frames.items():
            for widget in control_frame.winfo_children():
                widget.destroy()
            
            if player_name == current_player.name and cur_phase == 'Auction' and cur_round > 1:
                button = tk.Button(control_frame, text='Pass Auction', command=lambda pn=current_player.name: self.handle_pass(pn))
                button.grid(row=1, column=0, pady=5)
            
            if player_name == current_player.name and cur_phase == "Resources":
                # Confirm Purchase button: enabled only if money_to_pay is NOT zero
                confirm_btn = tk.Button(
                    control_frame,
                    text="Confirm",
                    width=7,
                    command=self.handle_purchase_resources,
                )
                if current_player.money_to_pay == 0:
                    confirm_btn.config(state=tk.DISABLED)
                confirm_btn.grid(row=0, column=0, pady=5, sticky="en")

                # Pass button: enabled only if money_to_pay is zero
                pass_btn = tk.Button(
                    control_frame,
                    text="Pass",
                    width=7,
                    command=lambda pn=current_player.name: self.handle_pass(pn)
                )
                if current_player.money_to_pay != 0:
                    pass_btn.config(state=tk.DISABLED)
                pass_btn.grid(row=1, column=0, pady=5, sticky="en")

                # Label to display current money to pay
                money_label = tk.Label(control_frame, text=f"Money to Pay: {current_player.money_to_pay}")
                money_label.grid(row=2, column=0, columnspan=2, pady=5)
            
            if player_name == current_player.name and cur_phase == "Houses":
                button = tk.Button(control_frame, text='Pass Building', command=lambda pn=current_player.name: self.handle_pass(pn))
                button.grid(row=1, column=0, pady=5)
            
            if player_name == current_player.name and cur_phase == "Bureaucracy":
                button = tk.Button(control_frame, text='Generate Power', command=lambda pn=current_player.name: self.handle_generate_power(pn))
                button.grid(row=1, column=0, pady=5)


    def handle_pass(self, player_name):
        response = messagebox.askyesno("Pass", f"{player_name}, are you sure you want to pass?")
        if response:
            self.action_handler('player_pass')
        
    def handle_purchase_resources(self):
        current_state = self.get_game_state()
        current_player_index = current_state["current_player_index"]
        current_player = current_state["players"][current_player_index]

        if current_player.money_to_pay > current_player.money:
            messagebox.showerror("Insufficient Funds", f"{current_player.name}, you don't have enough money to pay.")
            return
        
        response = messagebox.askyesno("Confirm Purchase", f"{current_player.name}, do you confirm the purchase?")
        if response:
            self.action_handler('purchase_resources')
    
    def handle_generate_power(self, player_name):
        response = messagebox.askyesno("Confirm to generate power", f"{player_name}, are you ready to generate power?")
        if response:
            result = self.action_handler('generate_power')
            if result is not None and isinstance(result, dict) and not result.get("success", False):
                messagebox.showerror("Error", result.get("message", "Failed to generate power"))
            else:
                messagebox.showinfo("Success", result.get("message"))
            
    def handle_click_res_to_purchase(self, card_id, res_type):
        result = self.action_handler('put_back_res_to_purchase', card_id=card_id, res_type=res_type)
        if result is not None and isinstance(result, dict) and not result.get("success", False):
            messagebox.showerror("Error", result.get("message", "Failed to put back resource"))
        
    def handle_click_res_on_card(self, card_id, res_type, phase):
        if phase == "Bureaucracy":
            result = self.action_handler('add_res_to_power', card_id=card_id, res_type=res_type)
            if result is not None and isinstance(result, dict) and not result.get("success", False):
                messagebox.showerror("Error", result.get("message", "Failed to add resource to power"))
    
    def handle_click_res_to_power(self, card_id, res_type):
        result = self.action_handler('remove_res_from_power', card_id=card_id, res_type=res_type)
        if result is not None and isinstance(result, dict) and not result.get("success", False):
            messagebox.showerror("Error", result.get("message", "Failed to remove resource from power"))
        
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

