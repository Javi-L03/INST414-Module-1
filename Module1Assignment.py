import requests
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_team_stats(code):
    url = f"https://api.football-data.org/v4/competitions/{code}/standings/?season={2023}"
    headers = {'X-Auth-Token': '688dd35f488d40be979519139030157d'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        resJson = response.json()
        return resJson
    else:
        print('Error:', response.status_code)
        return None
    
def get_player_stats(code):
    url = f"https://api.football-data.org/v4/competitions/{code}/scorers/?season={2023}"
    headers = {'X-Auth-Token': '688dd35f488d40be979519139030157d'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        resJson = response.json()
        return resJson
    else:
        print('Error:', response.status_code)
        return None   
    

def main():
    league_codes = ["PL", "FL1", "BL1", "SA", "PD"]
    
    
    for codes in league_codes:
        data = get_player_stats(codes)
        file = open(f"{codes}.json", "w")
        json.dump(data, file, indent = 5)
        file.close()
      
    stats = []
    for codes in league_codes:
        with open(f"{codes}.json", "r") as file:
            data = json.load(file)
            league_name = data['competition']['name']
            competition_code = data["competition"]["code"]
            for item in data['scorers']:
                player_stats = []
                player_stats.append(item["player"]["name"])
                player_stats.append(item["team"]["name"])
                player_stats.append(item["goals"])
                player_stats.append(item["assists"])
                player_stats.append(item["penalties"])
                player_stats.append(league_name)
                player_stats.append(competition_code)
                player_stats.append(item["team"]["id"])
                
                stats.append(player_stats)
    
    
    
    df = pd.DataFrame(stats, columns=["Names", "Teams", "Goals", "Assists", "Penalties", "League", "League Code", "Team ID"])
    #print(df["Names"])
    
    team_goals = []
    team_goals_against = []
    team_position=[]
    total_goals = []
    for codes in league_codes:
        teams_data = get_team_stats(codes)
        players = df[df["League Code"] == codes]
        goals = 0
        for _, player in players.iterrows():
            teams = teams_data["standings"][0]["table"]
            for i in range(len(teams_data["standings"][0]["table"])):
                goals += teams[i]["goalsFor"]
                if(player["Teams"] == teams[i]["team"]["name"]):
                    team_goals.append(teams[i]["goalsFor"])
                    team_goals_against.append(teams[i]["goalsAgainst"])
                    team_position.append(teams[i]["position"])
        total_goals.append(goals)
    
    total_league_goals = dict(zip(league_codes, total_goals))
    #print(total_league_goals)
    
    df["Team Goals"] = team_goals
    df["Team Goals Against"] = team_goals_against
    df["Team Position"] = team_position
    #print(df.isnull().sum())
    #print(total_goals)
    
    df.fillna({
        "Assists" : 0,
        "Penalties": 0
    }, inplace=True)
    
    df["Assists"] = df["Assists"].astype(int)
    df["Penalties"] = df["Penalties"].astype(int)
    
    #print(df.isnull().sum())
    #print(df)
    
    avg_goals = df.groupby("League")["Goals"].mean().astype(int).reset_index()
    plt.figure(figsize=(8,5))
    sns.barplot(x="League", y="Goals", data=avg_goals, hue="League")
    plt.title("Average Top Scorer Goals Per League")
    plt.xlabel("League")
    plt.ylabel("Average Goals")
    plt.show()
    
    league_goals = list(total_league_goals.keys())
    sns.barplot(x = league_goals, y = list(total_league_goals.values()), data = total_league_goals, hue = league_goals)
    plt.title("Total League Goals")
    plt.xlabel("League")
    plt.ylabel("Total Goals")
    plt.show()
    
    #print(avg_goals)
    
    df_numeric = df.select_dtypes(include=['number'])
    # Plot correlation heatmap
    sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap")
    plt.show()
    
    
if __name__ == '__main__':
    main()