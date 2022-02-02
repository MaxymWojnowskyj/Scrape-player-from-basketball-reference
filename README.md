Prompts the user to input a basketball player name. The user then selected which player they would like to scrape info on. The scraped player info will be displayed in the following format:

```yaml
{
	'Coach': 'pop', 
	'Games': [
    		{
			'Player': {'Min': 25, 'Pts': 11},
    			'Teammates': [ {'Name': 'a', 'Mins': 20}, {'Name': 'b', 'Mins': 15} ],
       			'Opponents': [ {'Name': 'x', 'Mins': 20}, {'Name': 'y', 'Mins': 15} ],
    			'OppCoach': 'guy',
    			'Referees': ['greg bob', 'orange obi', 'jog yor']     
    		},
    		{
    			'Player': {'Min': 30, 'Pts': 15},
    			'Teammates': [ {'Name': 'a', 'Mins': 10}, {'Name': 'b', 'Mins': 25} ],
    			'Opponents': [ {'Name': 'p', 'Mins': 30}, {'Name': 'q', 'Mins': 5} ],
    			'OppCoach': 'guy'     
    			'Referees': ['greg bob', 'orange obi', 'jog yor']
      		},
    		#   etc... 
     		] 	
}
```
The Player object is the minutes played and pts scored of our selected player.
We also store the players teammates, opponents, and the referees for the specific game. 
We store the other players names and minutes played so that we can create a relationship between a players points scored based on the players predicted playing time and other players predicted playing time wether that be teammates or opponents. 
We can also create a relationship based on who the team coach, opponent coach, and the referees for the game. 
(felt redundant to store the teamcoach for everysingle game so stored for season (incase our player gets a new coach for a new season).
