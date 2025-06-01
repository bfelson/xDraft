import os
from storage import DB_FILE, initialize_db, save_data, load_data, get_last_updated
from fetch_data import get_statcast_batters, get_statcast_pitchers, get_position_eligibility_list

def initialize_data():
    if not os.path.exists(DB_FILE):
        initialize_db()

        df_hitters = get_statcast_batters()
        df_pitchers = get_statcast_pitchers()

        eligibility_dict = get_position_eligibility_list(list(df_hitters.index))
        df_hitters["Eligible Positions"] = df_hitters.map(
            lambda name: ",".join(eligibility_dict.get(name, []))
        )

        save_data(df_hitters, "hitters")
        save_data(df_pitchers, "pitchers")

    df_hitters = load_data("hitters")
    df_pitchers = load_data("pitchers")

    return df_hitters, df_pitchers