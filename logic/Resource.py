INITIAL_RESOURCES = {
    'coal': [(1, True), (1, True), (1, True), (2, True), (2, True), (2, True), 
                (3, True), (3, True), (3, True), (4, True), (4, True), (4, True), 
                (5, True), (5, True), (5, True), (6, True), (6, True), (6, True), 
                (7, True), (7, True), (7, True), (8, True), (8, True), (8, True)],
    'oil': [(1, False), (1, False), (1, False), (2, False), (2, False), (2, False),
                (3, True), (3, True), (3, True), (4, True), (4, True), (4, True), 
                (5, True), (5, True), (5, True), (6, True), (6, True), (6, True), 
                (7, True), (7, True), (7, True), (8, True), (8, True), (8, True)],
    'trash': [(1, False), (1, False), (1, False), (2, False), (2, False), (2, False),
                (3, False), (3, False), (3, False), (4, False), (4, False), (4, False), 
                (5, False), (5, False), (5, False),(6, False), (6, False), (6, False), 
                (7, True), (7, True), (7, True), (8, True), (8, True), (8, True)],
    'uranium': [(1, False), (2, False), (3, False), (4, False), (5, False), (6, False), 
                (7, False), (8, False), (10, False), (12, False), (14, True), (16, True)]
}

TOTAL_RESOURCES = {
    'coal': 24,
    'oil': 24,
    'trash': 24,
    'uranium': 12
}

REFILL_RATES = {
    1: {  # Step 1
        2: {'coal': 3, 'oil': 2, 'trash': 1, 'uranium': 1},
        3: {'coal': 4, 'oil': 2, 'trash': 1, 'uranium': 1},
        4: {'coal': 5, 'oil': 3, 'trash': 2, 'uranium': 1},
        5: {'coal': 5, 'oil': 4, 'trash': 3, 'uranium': 2},
        6: {'coal': 7, 'oil': 5, 'trash': 3, 'uranium': 2},
    },
    2: {  # Step 2
        2: {'coal': 4, 'oil': 2, 'trash': 2, 'uranium': 1},
        3: {'coal': 5, 'oil': 3, 'trash': 2, 'uranium': 1},
        4: {'coal': 6, 'oil': 4, 'trash': 3, 'uranium': 2},
        5: {'coal': 7, 'oil': 5, 'trash': 3, 'uranium': 2},
        6: {'coal': 9, 'oil': 6, 'trash': 5, 'uranium': 3},
    },
    3: {  # Step 3
        2: {'coal': 3, 'oil': 4, 'trash': 3, 'uranium': 1},
        3: {'coal': 3, 'oil': 4, 'trash': 3, 'uranium': 1},
        4: {'coal': 4, 'oil': 5, 'trash': 4, 'uranium': 2},
        5: {'coal': 5, 'oil': 6, 'trash': 5, 'uranium': 2},
        6: {'coal': 6, 'oil': 7, 'trash': 6, 'uranium': 3},
    }
}


class Resources:
    def __init__(self):
        self.cur_resources = INITIAL_RESOURCES
        self.remaining_resources = {
            'coal': TOTAL_RESOURCES['coal'] - self.get_current_market_resources()['coal'],
            'oil': TOTAL_RESOURCES['oil'] - self.get_current_market_resources()['oil'],
            'trash': TOTAL_RESOURCES['trash'] - self.get_current_market_resources()['trash'],
            'uranium': TOTAL_RESOURCES['uranium'] - self.get_current_market_resources()['uranium']
        }

    def get_current_market_resources(self):
        return {res_type: sum(available for _, available in res_list) for res_type, res_list in self.cur_resources.items()}

    def refill_resources(self, num_players, step):
        if step not in [1, 2, 3]:
            print('Wrong step for refill resources')

        rates = REFILL_RATES[step][num_players]
        for res_type, count in rates.items():
            available_slots = [i for i, (cost, available) in enumerate(self.cur_resources[res_type]) if not available]
            available_slots.sort(reverse=True)
            count = min(count, len(available_slots), self.remaining_resources[res_type])
            for i in range(count):
                self.cur_resources[res_type][available_slots[i]] = (self.cur_resources[res_type][available_slots[i]][0], True)
                self.remaining_resources[res_type] -= 1
    
    def remove_left_most_resources(self, res_type):
        found = False
        for i, (cost, available) in enumerate(self.cur_resources[res_type]):
            if available:
                self.cur_resources[res_type][i] = (cost, False)
                found = True
                break
        return found
    
    def add_back_left_most_resource(self, res_type):
        """ also return cost for this resource token, -1 if no available slot to add back 
        """
        last_unavailable_idx = -1
        for i, (cost, available) in enumerate(self.cur_resources[res_type]):
            if not available:
                last_unavailable_idx = i
            else:
                break
        if last_unavailable_idx == -1:
            return -1
        
        cost, available = self.cur_resources[res_type][last_unavailable_idx]
        self.cur_resources[res_type][last_unavailable_idx] = (cost, True)
        return cost
        
    
    def validate_purchase(self, res_purchases, available_money):
        current_market_resources = self.get_current_market_resources()
        total_cost = 0
        for res_type, amount in res_purchases.items():
            if current_market_resources.get(res_type, 0) < amount:
                return (False, f'{res_type} not available for the amount: {amount}')
            available_resources = [(cost, idx) for idx, (cost, available) in enumerate(self.cur_resources[res_type]) if available]
            total_cost += sum(cost for cost, _ in available_resources[:amount])
        return (total_cost <= available_money, f'resources cost : {total_cost}')


    def proceed_purchases(self, res_purchases):
        for res_type, amount in res_purchases.items():
            available_resources = [(cost, idx) for idx, (cost, available) in enumerate(self.cur_resources[res_type]) if available]
            available_resources.sort(reverse=True)
            for cost, idx in available_resources[:amount]:
                self.cur_resources[res_type][idx] = (cost, False)

    def __repr__(self):
        return f"Resources({self.cur_resources})"

# resouces = Resources()
# resouces.refill_resources(4, 1)
# print(resouces)
