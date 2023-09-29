import pandas as pd

df = pd.read_csv('pbp_test.csv',index_col=0)

eventdict = {1:'FGM',
             2:'FGA',
             3:'FTA',
             4:'TRB',
             5:'TURNOVER',
             6:'FOUL',
             8:'SUB',
             9:'TIMEOUT',
             10:'JUMP_BALL',
             12:'Q_START',
             13:'Q_END',
             18:'REPLAY'             
            }

df['stat1'] = ''
df['stat1_value'] = 0
df['stat1_player_id']=''
df['stat2']= ''
df['stat2_value'] = 0
df['stat2_player_id'] = ''

#assisted baskets
df['stat2'].mask((df.eventmsgtype==1) & ~df.player2_name.isnull(), 'AST',inplace=True)
df['stat2_value'].mask((df.eventmsgtype==1) & ~df.player2_name.isnull(), 1,inplace=True)
df['stat2_player_id'].mask((df.eventmsgtype==1) & ~df.player2_name.isnull(),df.player2_id ,inplace=True)

#pts from baskets, 2pt default, overwrite with 3pt
df['stat1'].mask((df.eventmsgtype==1), 'PTS',inplace=True)
df['stat1_value'].mask((df.eventmsgtype==1), 2,inplace=True)
df['stat1_value'].mask((df.eventmsgtype==1) & (df.visitordescription.str.contains('3PT',na=False)
                      | df.homedescription.str.contains('3PT',na=False)), 3,inplace=True)
df['stat1_player_id'].mask((df.eventmsgtype==1),df.player1_id ,inplace=True)


df['stat1'] = ''
df['stat1_value'] = 0
df['stat2_value'] = 0
df['stat2']= ''
df.loc[df.eventmsgtype==1,'stat1'] = 'PTS'
df.loc[df.eventmsgtype==1 & (~df.homedescription.isnull()),['stat1_value']] = 2
df.loc[df.eventmsgtype==1 & (~df.visitordescription.isnull()),['stat1_value']] = 2
df.loc[df.eventmsgtype==1 & (df.homedescription.str.contains('3PT',na=False)),['stat1_value']] = 3
df.loc[df.eventmsgtype==1 & (df.visitordescription.str.contains('3PT',na=False)),['stat1_value']] = 3


def assign_made_ft(pbp_df):
    ft_filter = (pbp_df.eventmsgtype==3) & (pbp_df.homedescription.str.contains('PTS',na=False))
    ft_filter_visitor = (pbp_df.eventmsgtype==3) & (pbp_df.visitordescription.str.contains('PTS',na=False))

    pbp_df.loc[ft_filter,'stat1'] = 'PTS'
    pbp_df.loc[ft_filter,'stat1_value'] = 1
    pbp_df['stat1_player_id'].mask(ft_filter,pbp_df['player1_id'],inplace=True)
    pbp_df.loc[ft_filter_visitor,'stat1'] = 'PTS'
    pbp_df.loc[ft_filter_visitor,'stat1_value'] = 1
    pbp_df['stat1_player_id'].mask(ft_filter_visitor,pbp_df['player1_id'],inplace=True)
    return pbp_df

df = assign_made_ft(df)




df.to_csv('parsed_pbp.csv')

