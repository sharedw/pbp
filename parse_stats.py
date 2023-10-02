import pandas as pd
import re

df = pd.read_csv("pbp_raw\\0022200002_pbp.csv", index_col=0)
game_id = '0022200002'

def str_to_tuple(s):
    return tuple(s.strip("() ").replace(" ", "").split(","))

eventdict = {
    1: "FGM",
    2: "FGA",
    3: "FTA",
    4: "TRB",
    5: "TURNOVER",
    6: "FOUL",
    8: "SUB",
    9: "TIMEOUT",
    10: "JUMP_BALL",
    12: "Q_START",
    13: "Q_END",
    18: "REPLAY",
}
#def get_play_credit_df()
    
df["h_lineup"] = df.h_lineup.apply(lambda x: str_to_tuple(x))
df["a_lineup"] = df.a_lineup.apply(lambda x: str_to_tuple(x))

def get_rebound_types(df):#adds rebound_type column to df so ORB and DRB can be distinguished
#allll this ugly stuff just to get a column called 'rebound_type'
    mask = (df.eventmsgtype == 4) & (~df.homedescription.isnull() | ~df.visitordescription.isnull())
    pattern = r'Off:(\d+) Def:(\d+)'
    #getting rebound counts from play description and filling nulls, and casting to int
    df[['offensive_rebounds', 'defensive_rebounds']] = df['homedescription'].str.extract(pattern)
    df[['offensive_rebounds_v', 'defensive_rebounds_v']] = df['visitordescription'].str.extract(pattern)
    df[['offensive_rebounds', 'defensive_rebounds']] = df[['offensive_rebounds', 'defensive_rebounds']].fillna(0)
    df[['offensive_rebounds', 'defensive_rebounds']] = df[['offensive_rebounds', 'defensive_rebounds']].astype(int)
    df[['offensive_rebounds_v', 'defensive_rebounds_v']] = df[['offensive_rebounds_v', 'defensive_rebounds_v']].fillna(0)
    df[['offensive_rebounds_v', 'defensive_rebounds_v']] = df[['offensive_rebounds_v', 'defensive_rebounds_v']].astype(int)

    df.sort_values(by=['player1_id','period','total_elapsed_time','eventnum'], inplace=True)

    #comparing reb total to previous to check what type of rebound occurred
    df['def_reb_previous'] = df[mask].groupby('player1_id')['defensive_rebounds'].shift(fill_value=0)
    df['off_reb_previous'] = df[mask].groupby('player1_id')['offensive_rebounds'].shift(fill_value=0)
    df.sort_values(by=['period','total_elapsed_time','eventnum'],inplace=True)
    df['rebound_type'] = ''
    df.loc[(df.defensive_rebounds > df.def_reb_previous), 'rebound_type'] = 'DRB'
    df.loc[(df.offensive_rebounds > df.off_reb_previous), 'rebound_type'] = 'ORB'
    df.loc[(df.defensive_rebounds_v > df.def_reb_previous), 'rebound_type'] = 'DRB'
    df.loc[(df.offensive_rebounds_v > df.off_reb_previous), 'rebound_type'] = 'ORB'
    df.drop([ 'offensive_rebounds', 'defensive_rebounds',
        'offensive_rebounds_v', 'defensive_rebounds_v', 'def_reb_previous',
        'off_reb_previous'],inplace=True,axis=1)
    df.sort_values(by=['period','total_elapsed_time','eventnum'],inplace=True)
    return df

def get_play_credit_df(df):#returns data frame with one row per stat credited
    #filters to get all rows of specific stat type
    fga_filter = (df.eventmsgtype == 1) | (df.eventmsgtype == 2)
    two_pt_filter = (df.eventmsgtype == 1) & ~(
        (df.homedescription.str.contains("3PT", na=False))
        | (df.visitordescription.str.contains("3PT", na=False))
    )
    three_pt_filter = (df.eventmsgtype == 1) & (
        (df.homedescription.str.contains("3PT", na=False))
        | (df.visitordescription.str.contains("3PT", na=False))
    )
    three_a_filter = (df.homedescription.str.contains("3PT", na=False)) | (
        df.visitordescription.str.contains("3PT", na=False)
    )
    ft_filter = (df.eventmsgtype == 3) & (
        (df.homedescription.str.contains("PTS", na=False))
        | (df.visitordescription.str.contains("PTS", na=False))
    )
    fta_filter = df.eventmsgtype == 3
    assist_filter = (df.eventmsgtype == 1) & ~df.player2_name.isnull()
    stl_filter = df.homedescription.str.contains(
        "STEAL", na=False
    ) | df.visitordescription.str.contains("STEAL", na=False)
    blk_filter = df.homedescription.str.contains(
        "BLOCK", na=False
    ) | df.visitordescription.str.contains("BLOCK", na=False)
    to_filter = df.eventmsgtype == 5
    foul_filter = df.eventmsgtype == 6

    def get_stat_df(pbp_df, filter, stat_type, stat_value, player_num="1"):
        filtered_df = pbp_df.loc[filter][
            [
                "game_id",
                "eventnum",
                f"player{player_num}_id",
                f"player{player_num}_name",
                "h_lineup",
            ]
        ]
        filtered_df["stat"] = stat_type
        filtered_df["value"] = stat_value
        return filtered_df.values.tolist()

    #getting a list of every stat earned
    results = get_stat_df(df, two_pt_filter, "PTS", 2)
    results += get_stat_df(df, three_pt_filter, "PTS", 3)
    results += get_stat_df(df, ft_filter, "PTS", 1)
    results += get_stat_df(df, assist_filter, "AST", 1, player_num="2")

    results += get_stat_df(df, fga_filter, "FGA", 1)
    results += get_stat_df(df, fta_filter, "FTA", 1)
    results += get_stat_df(df, three_a_filter, "3PA", 1)

    results += get_stat_df(df, stl_filter, "STL", 1, player_num=2)
    results += get_stat_df(df, blk_filter, "BLK", 1, player_num=3)
    results += get_stat_df(df, to_filter, "TOV", 1, player_num=1)
    results += get_stat_df(df, foul_filter, "PF", 1)

    play_credit_df = pd.DataFrame(
        results,
        columns=[
            "game_id",
            "eventnum",
            "player_id",
            "player_name",
            "lineup",
            "stat_type",
            "stat_value",
        ],
    )
    return play_credit_df

df = get_rebound_types(df)

play_credit_df = get_play_credit_df(df)

play_credit_df.to_csv(f'play_credits/play_creds_{game_id}.csv')
