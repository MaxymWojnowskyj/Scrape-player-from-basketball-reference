from os import getsid
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

URL = "https://www.basketball-reference.com"


def prompt_for_player():
    player_search = True
    while (player_search):
        player_name = input("Player name (enter first, last, or both (seperate by space): ")

        first = player_name.split(" ")[0] # this could be just last name as well (search works for only first and only last as well)
        last = ""
        if len(player_name.split(" ")) > 1:
            last = "+"+player_name.split(" ")[1] # if a last name is added then add a + to the string query

        player_url = URL+f"/search/search.fcgi?search={first}{last}"

        req_results_page = urlopen(player_url)
        results_page = BeautifulSoup(req_results_page, features="lxml")

        players_div = results_page.find(id="players")
        players = players_div.findAll("a")

        print(f"\n{len(players)} Players found (on first page): \n")

        for player in players:
            print(player.text)
        
        select_idx = input(f"\nEnter the index of the selected player (1 to {len(players)}), q to quit, or any other character (non integer and not q) to search again: ")
        try: # try to convert users input to an integer, if it cannot be converted then it is not an integer so either quit the program or go back to top of while loop
            select_idx = int(select_idx)
            while (select_idx < 1 or select_idx > len(players)):
                try:
                    select_idx = int(input("Please enter a selectable index integer value (in range of found players) or q to quit: "))
                except ValueError:
                    pass # keep reprompting until valid index is inputted
            player_search = False #if correct index was enterd in the while loop then exit the outer outer while loop
        except ValueError:
            if select_idx == 'q': quit() #will exit the program here, otherwise a idx number was entered and can carry on
    
    return {"Name": players[select_idx-1].text, "URL": URL+players[select_idx-1]['href']} 

def get_season_stats(url, season_dict, player_name):
    req_season_page = urlopen(url)
    season_page = BeautifulSoup(req_season_page, features="lxml")
    season_table = season_page.find(id="pgl_basic")
    game_rows = season_table.findAll("tr")
    
    #get team coach name for the season 
    team_url = URL+game_rows[1].find("td", {"data-stat": "team_id"}).find("a")["href"] # will be second row in table so [1]
    season_dict["Coach"] = get_coach_name(team_url)
    ###
    
    #get the boxscore link for each game in the season along with the status of if the player played in said game
    team_tkr = ""
    game_boxscores = []
    for row in game_rows:
        if row.find("a"): # if a is not None then add link to list
            
            if team_tkr == "": team_tkr = row.find("td", {"data-stat": "team_id"}).text
            # [{url: 'https...', played: false}, {url: 'https...', played: true}]
            played = True
            if row.find("td", {"data-stat": "reason"}): played = False # if we find the reason column then that means that the player did not play this game
            game_boxscores.append({"URL": URL+row.find("a")["href"], "Played": played})
    ###    
    
    games_arr = []
    for game_obj in game_boxscores:
        print(f"Scraping Game #{len(games_arr)+1}", end='\r') # doing +1 so user can see what current game is being added
        req_game_page = urlopen(game_obj.get("URL"))
        game_page = BeautifulSoup(req_game_page, features="lxml")
        game = {}
        if (not game_obj.get("Played")): game["Player"] = {"Min": "0:00", "Pts": "0"} 
        opp_ticker = ""
        found_tables = game_page.findAll("table", {"class":["sortable", "stats_table", "now_sortable"]}) 
        boxscore_tables = [] 
        for table in found_tables: # save the two tables that contain the players, their mins played, and points scored then iterate over them
            if "game-basic" in table.get("id"):
                boxscore_tables.append(table)

        team_mates = False #set states of teammates so we know which array of players to save as teammates and opponents
        for table in boxscore_tables:
            table_tkr = table.get("id").split("x-")[1].split("-g")[0] # example id looks like this: box-DEN-game-basic we are splitting to get DEN 
            players = []
            for row in table.findAll("tr"):
                if row.find("a") and row.find("td", {"data-stat": "mp"}): # if the row is a player and they have minutes played (they played in the game)
                    row_name = row.find("a").text
                    row_mp = row.find("td", {"data-stat": "mp"}).text # minutes played for that specific player
                    # if the player we are scraping for is found then create an obj for them otherwise add the teammate or opponent to the players array
                    if player_name == row_name: game["Player"] = {"Min": row_mp, "Pts": row.find("td", {"data-stat": "pts"}).text}
                    else: players.append({"Name": row_name, "Mins": row_mp})

            # if the current table we just scraped is from our team then set the players array to teammates otherwise we just scraped the opponents for this game
            if table_tkr == team_tkr:
                game["Teammates"] = players
            else: 
                game["Opponents"] = players
                opp_ticker = table.get("id").split("x-")[1].split("-g")[0]


        # get opponent team coach
        hdr_links = game_page.find("div", class_="scorebox").findAll("a")
        for link in hdr_links:
            if f"/{opp_ticker}/" in link["href"]:
                game["OppCoach"] = get_coach_name(URL+link["href"]) 
        ###

        # get referees for this specific game (no unique id for this div and doesnt seem to be at a consistent index between all divs)
        #refs = []
        #print(game_page.find(id="bottom_nav").previous_sibling)
        #div_range = game_page.findAll("div")
        #for div in div_range:
            #if div.find("a") and div.find("a")["href"] and "referees" in div.find("a")["href"]:
                #for a in div.findAll("a"):
                    #if len(refs) < 3:
                    #refs.append(a["href"].text)
                    #else: break
            #else: break
        #all_as = game_page.findAll("a")
        #for a in all_as:
            #if a["href"] and "referees" in a["href"]:
                #if len(refs) == 3:
                    #break
                #else:
                    #refs.append(a["href"])


        #print(refs)

        #game["Referees"] = refs
        games_arr.append(game) # after the game dict is created then add it to the list of games for the specific season

    season_dict["Games"] = games_arr
    return season_dict

def get_coach_name(url):
    req_team_page = urlopen(url)
    team_page = BeautifulSoup(req_team_page, features="lxml")
    coach_name = team_page.find("div", {"data-template": "Partials/Teams/Summary"}).findAll("a")[3].text
    return coach_name    

def main():
    prompt = prompt_for_player() 
    player_url = prompt.get("URL")
    print(f"\nScraping for {prompt.get('Name')}:\n")
    data = {} 

    #get link for each season played by player then save year of season as key in dictionary
    req_player_page = urlopen(player_url) 
    player_page = BeautifulSoup(req_player_page, features="lxml")
    player_name = player_page.find(id="meta").find("span").text
    seasons_table = player_page.find(id="per_game")
    seasons_rows = seasons_table.findAll("tr")
    season_links = []
    for row in seasons_rows:
        if row.find("a") and "gamelog" in row.find("a")["href"]: # if row is not None and includes a season href then add to list
            season_links.append(URL+row.find('a')['href'])
            data[row.find('a').text] = {} #OrderedDict()
    ###
    
    # iterate over each season grabbing game stats for each
    season_count = 0
    for season_dict in data.values():
        current_season = list(data.keys())[season_count]
        print(f"Scraping season: {current_season}")
        # { current_season: {"Coach": "...", "Games": [...]}, }
        data[current_season] = get_season_stats(season_links[season_count], season_dict, player_name)
        print ("\033[A                             \033[A") # clear scrapping game # line in stdout
        print(f"Season {current_season} scraped")
        season_count += 1
    ###

    #save player dict to json file
    with open(player_name.replace(" ", "_")+'.json', 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)
    ###
    print("JSON file created")

main()

