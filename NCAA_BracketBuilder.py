import streamlit as st
import graphviz as graphviz #installed with pip

## Data manipulation
import pandas as pd
import numpy as np
from pathlib import Path

## Choose men or women ( 'M' for men, 'W' for women) and make sure your submission file name is correct
mw = 'M'
submission_file = 'mens_submission.csv' #Type file name here. File should be located in input folder

##loading function
@st.cache
def load_submission(df,slots,seeds,season_info):
    df[['Season','LeftTeamID','RightTeamID']] = df['ID'].str.split('_',expand=True)
    df.reset_index(inplace=True, drop=True)
    df = df[['ID','Season','LeftTeamID','RightTeamID','Pred']]
    df.columns = ['ID','Season','LeftTeamID','RightTeamID','Pred']
    season = int(df['Season'].unique()[0])
    season_info = season_info.loc[season_info['Season']==season].copy()
    region_dict = {'W':season_info['RegionW'].values[0],
                   'X':season_info['RegionX'].values[0],
                   'Y':season_info['RegionY'].values[0],
                   'Z':season_info['RegionZ'].values[0],
                   }

    df_rev = df[['ID','Season','RightTeamID','LeftTeamID','Pred']].copy()
    df_rev.columns = ['ID','Season','LeftTeamID','RightTeamID','Pred']
    df_rev['Pred'] = 1-df_rev['Pred']
    df_rev['ID'] = str(season)+'_'+ df_rev['LeftTeamID'].astype(str)+'_'+df_rev['RightTeamID'].astype(str)
    df = pd.concat([df,df_rev])

    seeds = seeds.loc[seeds['Season']==season,:].copy()
    seeds.drop(columns='Season',inplace=True)
    seeds['Region'] = seeds['Seed'].str.extract(r'([WXYZ]).*')
    seeds['Region'].replace(region_dict,inplace=True)
    seeds['Number'] = seeds['Seed'].str.extract(r'[WXYZ](.*)')
    seeds['NewSeed'] = seeds['Region']+'-'+seeds['Number']
    
    oldseeds_dict = seeds.set_index('Seed')['NewSeed'].to_dict()
    seeds_dict = seeds.set_index('NewSeed')['TeamID'].to_dict()

    if mw == 'W': #womens csv does not have a column for season so we will fake it.
        slots['Season']=season
    else: pass
    slots = slots.loc[slots['Season']==season,:].copy()
    slots.drop(columns='Season',inplace=True)
    slots['StrongSeed'].replace(oldseeds_dict,inplace=True)
    slots['WeakSeed'].replace(oldseeds_dict,inplace=True)
    slots['Round'] = slots['Slot'].str.extract(r'(R.)[WXYZC].').fillna('R0')
    slots['Game'] = slots['Slot'].str.extract(r'.*([WXYZC].*)')

    return df, slots, seeds_dict, season

path = Path('./input/')
season_info = pd.read_csv(path/(mw+'Seasons.csv'))
teams_dict = pd.read_csv(path/(mw+'Teams.csv')).set_index('TeamID')['TeamName'].to_dict() # Create team dictionary to go from team ID to team name
seeds = pd.read_csv(path/(mw+'NCAATourneySeeds.csv'))
slots = pd.read_csv(path/(mw+'NCAATourneySlots.csv'))
submission = pd.read_csv(path/submission_file)

submission, slots, seeds_dict, season = load_submission(submission,slots,seeds,season_info)

games = slots.copy()
games['WinnerSeed'] = ''
games['StrongName'] = ''
games['WeakName'] = ''
games['WinnerName'] = ''
games['StrongID'] = ''
games['WeakID'] = ''
games['WinnerID'] = ''
games.loc[:,'Pred'] = -1.0
games.sort_values('Round',inplace=True)
games.reset_index(inplace=True,drop=True)

def update_games(games,round,next_round):

    for idx,row in games[games['Round']==round].iterrows():
        games.loc[idx,'StrongID'] = seeds_dict[row['StrongSeed']]
        games.loc[idx,'WeakID'] = seeds_dict[row['WeakSeed']]
        games.loc[idx,'StrongName'] = teams_dict[games.loc[idx,'StrongID']]
        games.loc[idx,'WeakName'] = teams_dict[games.loc[idx,'WeakID']]

    
    for idx,row in games[games['Round']==round].iterrows():



        game = row['Game']
        id = (str(season)+'_'+ str(row['StrongID'])+'_'+ str(row['WeakID']))
        pred = submission.loc[submission['ID']==id,'Pred'].values[0]
        if pred> .5:
            winslot = row['StrongSeed']
            winID = row['StrongID']
            winname = teams_dict[winID]
            loseslot = row['WeakSeed']
            loseID = row['WeakID']
            losename = teams_dict[loseID]
        else:
            winslot = row['WeakSeed']
            winID = row['WeakID']
            winname = teams_dict[winID]
            loseslot = row['StrongSeed']
            loseID = row['StrongID']
            losename = teams_dict[loseID]
            pred = 1 - pred

        st.subheader( row['StrongSeed'] +' **' + row['StrongName'] + '** vs ' + 
                 row['WeakSeed'] + ' **' + row['WeakName'] + '**')
        if pred < thresh:
            st.write( str(winname) + ' predicted to win with a ' + str(np.round(pred*1000)/10) + '% chance')
            overwrite = st.radio(label='Manual pick:',options=[winname,losename])
            if overwrite == losename:
                winslot = loseslot
                winID = loseID
                winname = losename
                pred = 1 - pred
            else: pass


        st.write('**' + winname + '** advances!')
        games.loc[idx,'WinnerSeed'] = winslot
        games.loc[idx,'WinnerID'] = winID
        games.loc[idx,'WinnerName'] = winname
        games.loc[idx,'Pred'] = pred

        if round == 'R0':
            next_slot = game
            games.loc[games['Round']==next_round,'StrongSeed'] = (games.loc[games['Round']==next_round,'StrongSeed']
                                                                    .replace({next_slot:winslot}))
            games.loc[games['Round']==next_round,'WeakSeed'] = (games.loc[games['Round']==next_round,'WeakSeed']
                                                                    .replace({next_slot:winslot}))
        elif round == 'R5':
            if game == 'X':
                games.loc[games['Round']==next_round,'StrongSeed'] = winslot
            else:
                games.loc[games['Round']==next_round,'WeakSeed'] = winslot

        else:
            next_slot = round+game
            games.loc[games['Round']==next_round,'StrongSeed'] = (games.loc[games['Round']==next_round,'StrongSeed']
                                                                    .replace({next_slot:winslot}))
            games.loc[games['Round']==next_round,'WeakSeed'] = (games.loc[games['Round']==next_round,'WeakSeed']
                                                                    .replace({next_slot:winslot}))
    st.write('**Check your picks here before moving on**') 
    st.dataframe(games)

    return games

thresh = st.slider(label='Threshold for manual picking (use 1 to pick all games - less for close games)',min_value=.5,max_value=1.0,value=.6)

if mw == 'M': # no play-in for the womens tourney
    st.header('Play-in games')
    games = update_games(games,'R0','R1')
else: pass

st.header('Round 1 - Let the madness begin!')
games = update_games(games,'R1','R2')

st.header('Round 2 - Are you worn out yet?')
games = update_games(games,'R2','R3')

st.header('Round 3 - Sweet 16')
games = update_games(games,'R3','R4')

st.header('Round 4 - Elite 8')
games = update_games(games,'R4','R5')

st.header('Round 5 - Final 4')
games = update_games(games,'R5','R6')

st.header('Round 6 - Championship!')
games = update_games(games,'R6','')

bracket_odds = int(round(1/np.multiply.reduce(np.array(games['Pred']))))
bracket_odds_noPI = int(round(1/np.multiply.reduce(np.array(games.loc[games['Round']!= 'R0','Pred']))))

if mw=='W':
    st.write('''
            According to these probabilities, your odds of a perfect bracket are 1 in **{a:,d}**...  
            Yikes! Good luck! :)
            '''.format(a=bracket_odds))
else:
    st.write('''
            According to these probabilities, your odds of a perfect bracket are 1 in **{a:,d}** including
            the play-in games or **{b:,d}** not including the play-in games...  
            Yikes! Good luck! :)
            '''.format(a=bracket_odds,b=bracket_odds_noPI))



if st.button('Export Picks to .csv'):
    games.to_csv(Path('./output/My_NCAA_Bracket.csv'))

## Quick bracket viz

st.header('**Bracket below! Find \'wide mode\' in the upper right to make bigger**')

graph = graphviz.Digraph(node_attr={'shape': 'rounded','color': 'lightblue2'})

round_dict = {'R0':'R1',
              'R1':'R2',
              'R2':'R3',
              'R3':'R4',
              'R4':'R5',
              'R5':'R6',
              'R6':'CH',
              'CH':'Winner!'
              }
for _,row in games.iterrows():

    T1 = row['Round']+'-'+row['StrongSeed']+'-'+row['StrongName']
    T2 = row['Round']+'-'+row['WeakSeed']+'-'+row['WeakName']
    W = round_dict[row['Round']]+'-'+row['WinnerSeed']+'-'+row['WinnerName']
    if row['StrongSeed'] == row['WinnerSeed']:

        T1_params = {'color':'green', 'label': (str(int(row['Pred']*100))+'%')}
        T2_params = {'color': 'red'}
        
    else:
        T2_params = {'color':'green', 'label': (str(int(row['Pred']*100))+'%')}
        T1_params = {'color': 'red'}

    graph.edge(T1,W,**T1_params)
    graph.edge(T2,W,**T2_params)

graph.graph_attr['rankdir'] = 'LR'
graph.graph_attr['size'] = '30'

graph.node_attr.update(style='rounded')

st.graphviz_chart(graph)