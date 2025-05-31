import pandas as pd
from fetch_data import get_position_eligibility_list, get_statcast_batters, get_statcast_pitchers

# Test getting statcast batters
sc_bats = get_statcast_batters()
print(sc_bats)

# Test getting statcast pitchers
sc_pits = get_statcast_pitchers
print(sc_pits)

# Test getting position eligibilities for a list
player_names = sc_bats.index.values
print(get_position_eligibility_list(player_names[0:20]))