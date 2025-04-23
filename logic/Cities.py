from utils.constants import CITIES
import heapq

class Cities:
    def __init__(self):
        # Track built cities: city_name -> list of owners
        self.built_cities = {}  # only store cities once built
        # Track regions where cities have been built
        self.occupied_regions = []
        # Validate neighbor consistency on initialization
        self._validate_neighbors()

    def _validate_neighbors(self):
        errors = []
        for city, info in CITIES.items():
            for neighbor, cost in info['neighbors']:
                rev = CITIES.get(neighbor, {}).get('neighbors', [])
                match = next((c for c in rev if c[0] == city), None)
                if match is None or match[1] != cost:
                    errors.append(
                        f"Neighbor mismatch: {city}->{neighbor} ({cost}), "
                        f"reverse is {match}"
                    )
        for err in errors:
            print(f"[Cities Validation Error for Connection Cost] {err}")
        if len(errors) == 0:
            print("Validated City Connection Cost!\n")

    def build_house(self, city_name, player_name, max_regions):
        """
        Place a house for player_name in city_name. Enforce max distinct regions can be built.
        """
        if city_name not in CITIES:
            raise ValueError(f"Unknown city: {city_name}")
        
        if city_name in self.built_cities and player_name in self.built_cities[city_name]:
            raise ValueError(f"{player_name} has built a house in {city_name}")

        region = CITIES[city_name]['region']

        # If this is a new region, check limit
        if region not in self.occupied_regions:
            if len(self.occupied_regions) + 1 > max_regions:
                raise ValueError(f"Cannot build in new region '{region}', exceeds limit {max_regions}")
            self.occupied_regions.append(region)

        # Add to built_cities map
        if city_name in self.built_cities:
            self.built_cities[city_name].append(player_name)
        else:
            self.built_cities[city_name] = [player_name]
    
    def get_connection_cost(self, city_name, owned_cities, regions=[]):
        """
        Calculate the minimum connection cost from any city in owned_cities to city_name
        using Dijkstra's algorithm. Returns 0 if owned_cities is empty, or None if no path exists.
        """
        if not owned_cities:
            return 0
        
        if len(regions) > 0 and city_name not in regions:
            raise ValueError(f"City {city_name} not in regions {regions}")

        dist = {c: float('inf') for c in CITIES}
        dist[city_name] = 0
        pq = [(0, city_name)]
        visited = set()
        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            # If we reached an owned city, return cost
            if u in owned_cities:
                return d
            for v, cost in CITIES[u]['neighbors']:
                if len(regions) > 0 and CITIES[v]['region'] not in regions:
                    continue
                nd = d + cost
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))

        return None

    def get_build_cost(self, city_name):
        """
        Return the cost to build the next house in city_name:
        first costs 10, second 15, third 20.
        """
        count = len(self.built_cities.get(city_name, []))
        if count == 0:
            return 10
        elif count == 1:
            return 15
        else:
            return 20

    def __repr__(self):
        return f"Cities(built={self.built_cities}, occupied_regions={self.occupied_regions})"