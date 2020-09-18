from requests import get
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# billboard's date format
date_format = '%Y-%m-%d'

# homepage of hot 100 (current week)
# prefix to all weeks
base_url = "https://www.billboard.com/charts/hot-100"

# base_name of the html class which contains the tracks
base_name = "chart-list__element"


# a song dataclass contains all the attributes from the billboard website
# if there is no last_week then set to 101
@dataclass
class Song:
    title: str
    artist: str
    rank: int
    peak_pos: int
    weeks_on_chart: int = 1
    last_week: int = 101


# a week is a date with a list of songs
@dataclass
class Week:
    date: datetime
    songs: List[Song] = field(default_factory=list)


# parse html for a url
def simple_get(url: str) -> BeautifulSoup:
    return BeautifulSoup(get(url).text, 'html.parser')


# format date returned by datetime to billboard's url format
def format_date(date: datetime) -> str:
    return datetime.strftime(date, date_format)


# go back num_days from the start
def date_shift(start: datetime, num_days: int) -> datetime:
    return start - timedelta(days=num_days)


'''
Fetch billboard hot 100 list for a given_date.
Get an html response from https://www.billboard.com/charts/hot-100/yyyy-mm-dd
Fetch all html list items which have belonging to the class "chart-list__element"
For each song, iterate over those items to find spans of interest and 
add them to the song object.
Finally, add the list of all songs from the given_date to the Week object along
with the given_date in date format.
'''


def get_one_week(given_date: datetime) -> Week:
    # the ratings come out on Saturday (sat is 5)
    # if the start date is not a saturday, shift and find the nearest saturday
    shift = (given_date.weekday() - 5) % 7
    chart_date = date_shift(given_date, shift)
    # chart_date is a datetime object. We need to convert it to a string to append it to the url
    chart_date_str = format_date(chart_date)
    html = simple_get(base_url + '/' + chart_date_str)

    list_items = html.findAll("li", {"class": base_name})

    songs = []
    for item in list_items:
        # the required data is stored within spans within different list items
        s = Song(item.find("span", {"class": "chart-element__information__song"}).string,
                 item.find("span", {"class": "chart-element__information__artist"}).string,
                 int(item.find("span", {"class": "chart-element__rank__number"}).string),
                 int(item.find("span", {"class": "chart-element__information__delta__text text--peak"}).string.split(
                     " ")[0]),
                 int(item.find("span", {"class": "chart-element__information__delta__text text--week"}).string.split(
                     " ")[0]))
        # a song might not have a last_week if it is new on the list
        # billiboard puts '-' in the inner HTML of the span in that case
        # conversion of '-' to int causes a ValueError, so we check for that error
        # if that error occurs, we keep the last_week as 101 as specified in the Song class
        try:
            s.last_week = int(
                item.find("span", {"class": "chart-element__information__delta__text text--last"}).string.split(" ")[0])
        except ValueError:
            pass
        songs.append(s)
    return Week(chart_date, songs)


today = datetime.today()
w = get_one_week(today)




'''
Convert the data for one week into a pandas dataframe
Iterate over each song in a week and append it to the dataframe
'''


def one_week_pandas(df_curr, week: Week) -> pd.DataFrame:
    for song in week.songs:
        # create a dictionary of members in the song class
        song_dict = vars(song)
        # add an entry for week which will hold the date
        song_dict['week'] = week.date.date()
        df_curr = df_curr.append(song_dict, ignore_index=True)
    return df_curr



def get_weeks_between(w1: datetime, w2: datetime) -> pd.DataFrame:
    df = pd.DataFrame(columns=["week", "title", "artist", "rank", "last_week", "peak_pos", "weeks_on_chart"])
    df.astype({'week': 'datetime64', "title": "str", "artist": "str", "rank": "int64",
                    "last_week": "int64", "peak_pos": "int64", "weeks_on_chart": "int64"}) #create dataframe

    incrementer = w2 #temp variable, increment, will go from week2 all the way back to week1
    while (incrementer >= w1): #while the date of incrementer is still greater than the 1st week given
        weekSongs = get_one_week(incrementer)#get the first week of incrementer which is the end point and extract data from the week on billboard
        df = one_week_pandas(df, weekSongs) #put date found into the dataframe
        incrementer = date_shift(incrementer, 7) #make incrementer(datetime) go back 7 days
    return df #after looping all the data into the dataframe return the dataframe

def best_week(year: datetime) -> Week:
    df = pd.DataFrame(columns=["week", "title", "artist", "rank", "last_week", "peak_pos", "weeks_on_chart"])
    df.astype({'week': 'datetime64', "title": "str", "artist": "str", "rank": "int64",
                    "last_week": "int64", "peak_pos": "int64", "weeks_on_chart": "int64"})# create dataframe
    year1 = year.year #set the year of the date given into year1
    startyear = datetime(year1, 1, 1) #set startyear to the start of the year of the date given
    endyear = datetime(year1, 12, 31) #set endyear to the end of the year of the date given
    if(year1 == datetime.today().year): #if the date given is the current date
        endyear = datetime.today() #the endpoint will be today because it's the most recent date
        #print(endyear)
    bestweek = startyear #we start by assuming the best week is the first week
    temp = startyear #create a temp variable that will move through every week
    mostone = 0 #set the most number of #1 songs as 0 which will be updated while looping

    while(temp <= endyear): #while the temp variable, which is the start of the year is less than end year (or most recent date)
        c_df = one_week_pandas(df, get_one_week(temp)) #get the week of the temp variable, extract date from billboard, and put into a dataframe
        c_df = c_df.filter(regex='peak_pos') #filter to only peak_position
        tempmode = 0 #temporary variable that will count the number of peak songs
        for i in c_df["peak_pos"]:# loop through to count the number of peak songs in the week
            if(i == 1):
                tempmode += 1
        if(tempmode >= mostone): #if the counted most peak pos is greater than the current most then the current most will be replaced with the counted most
            mostone = tempmode
            bestweek = temp #bestweek will also be updated to the week that has the new most current peak positions
        temp = date_shift(temp, -7) #shift temp variable 7 days ahead


    print(mostone)
    return get_one_week(bestweek) #return the best week as a week class instead of a week datetime



#print(best_week(datetime.today()))

#  #1 peak position and longest on the chart, at the end of the year or current date
def best_song(year: datetime) -> Song:
    df = pd.DataFrame(columns=["week", "title", "artist", "rank", "last_week", "peak_pos", "weeks_on_chart"])
    df.astype({'week': 'datetime64', "title": "str", "artist": "str", "rank": "int64",
                    "last_week": "int64", "peak_pos": "int64", "weeks_on_chart": "int64"}) #Create dataframe
    year1 = year.year #take the year given
    endyear = datetime(year1, 12, 31) #end of the year
    if(year1 == datetime.today().year): #or current date if its the most recent
        endyear = datetime.today()
    longest = 0 #create longest variable
    df = one_week_pandas(df, get_one_week(endyear)) #get the current week or end of the year week
    song = Song("", "", 0, 0, 0, 0) #create song variable to store the best song (temp data)
    artist = df["artist"].loc[0] #create an artist variable to store the artist  (temp data)
    for i in range(0,100): #loop through the entire week
        if(df["peak_pos"].loc[i] == 1): #if the song has been #1
            if(df["weeks_on_chart"].loc[i] >= longest): #if it has the longest time on the chart then update it
                longest = df["weeks_on_chart"].loc[i] #update longest with the longest time on the chart
                artist = df["artist"].loc[i] #update artist with well, the artitst of the song, this was honestly only made just to make it easier to print
                song = Song(df["title"].loc[i], #plug in all the data  for the song
                            df["artist"].loc[i],
                            df["rank"].loc[i],
                            df["peak_pos"].loc[i],
                            df["weeks_on_chart"].loc[i],
                            df["last_week"].loc[i])
    return song #return the best song

#test = best_song(datetime.today())
#print(test.title + " by " + test.artist + ", peaked at: " + str(test.peak_pos) + " and has been on the chart for: " + str(test.weeks_on_chart))

# Part3: Plots

# lifetime trajectories
'''
Write a function number_ones(date1: datetime, date2: datetime) 
On a single plot, display the lifetime trajectory of every song 
that was ever #1, between a pair of given dates. For the purpose 
of this exercise, a song's lifetime corresponds to the set of 
weeks for which it appears on the chart. The song's trajectory 
is a line graph of its rank over those weeks. To do this you 
will write a function called number_ones(date1:datetime, 
date2:datetime) which both shows a plot and saves it to a file 
named num_ones.png.
'''
def number_ones(date1: datetime, date2:datetime):
    df = pd.DataFrame(columns=["week", "title", "artist", "rank", "last_week", "peak_pos", "weeks_on_chart"])
    df.astype({'week': 'datetime64', "title": "str", "artist": "str", "rank": "int64",
                    "last_week": "int64", "peak_pos": "int64", "weeks_on_chart": "int64"}) #Create dataframe

    df = get_weeks_between(date1, date2) #gather data into the dataframe between the first week and second week given

    df = df.loc[df['peak_pos'] == 1] # filter dataframe to songs with peak positions at 1

    print(df)

    fig, ax = plt.subplots()

    for name, group in df.groupby('title'): #create lines for every title in the dataframe
        group.plot(kind = "line", x='week', y='rank', ax=ax, label=name) #line created
    plt.tight_layout() #tight layout
    plt.xlabel('Week') #Label x as week
    plt.ylabel('Rank') #label y as rank
    plt.gca().invert_yaxis() #invert the y axis so that rank has lower at the top and bigger at the bottom (ex: rank 1 will be at the top)
    plt.xticks(rotation=90) #rotate teh xlabels 90 degrees
    plt.savefig('ranks.png') #export the image

#number_ones(date_shift(datetime.today(), 56), datetime.today())

#The best artist has the most weeks with the most singles on the chart (not the person who has the most songs on the chart) in the current year
def best_artist(date:datetime) -> str:
    df = pd.DataFrame(columns=["week", "title", "artist", "rank", "last_week", "peak_pos", "weeks_on_chart"])
    df.astype({'week': 'datetime64', "title": "str", "artist": "str", "rank": "int64",
                    "last_week": "int64", "peak_pos": "int64", "weeks_on_chart": "int64"}) #create a dataframe to collect data from billboard

    bestDf = pd.DataFrame(columns=["time", "num", "artist"]) #create dataframe to store information to find the best artist
    bestDf.astype({'time': 'datetime64', "num": 'int64', "artist": 'str' })
    year = date.year #get the current year
    startyear = datetime(year, 1, 1) #start of the year
    endyear = datetime(year, 12, 31) #end of the year
    if(year == datetime.today().year): #if the year is equal to the current year
        endyear = datetime.today() #set end of year to the most recent date
    df = one_week_pandas(df, get_one_week(endyear)) # get the billboard data at the end of year or current date (depends if went through the if statement)
    while (startyear <= endyear): #loop if the start of the year is greater than the end of the year
        artist = df['artist'].mode().loc[0] #filters the dataframe df to the mode, and get's the first index which is the mode, which is the best artist of that week because they have the most songs on the chart
        songcount = df['artist'].value_counts().max() #counts the number of songs that are on the chart by that artist
        bestDf = bestDf.append({'time': endyear, 'num': songcount, 'artist': artist}, ignore_index=True) #puts the information into the bestDF as he's/she's the best artist of that week
        endyear = date_shift(endyear, 7) #shift end of year back one week to get the next week
        df = df.iloc[0:0] #clear the original dataframe to get a new week
        df = one_week_pandas(df, get_one_week(endyear)) #gather data of the next week and put it into the dataframe
    bestartist = bestDf['artist'].mode().loc[0] #gets the mode of the best artists of the week in a dataframe that counts every week in the year, and he's/she's the best artist of the year
    bestartistfrequency = bestDf['artist'].value_counts().max() #gets the number of times he's/she's been the artist of the week
    #print(bestDf)
    #print(bestartist)
    #print(bestsongcount)
    ax = bestDf.plot.bar(x='artist', y='num', rot=0) #create a bar plot with the x axis being artist of the week and y axis being the number of songs on the chart
    plt.xlabel("Artist") #x axis label is the artist of the week
    plt.ylabel("Number of Songs") #y axis label is the number of songs on the chart that week
    #plt.tight_layout()
    plt.xticks(rotation=90) #rotate the xlabels by 90 degrees so they dont overlap
    plt.savefig('bestartist.png') #export it
    #return the best artist and the amounts of times he's/she's been the best artist of the week, in string form
    return bestartist + " has " + str(bestartistfrequency) + " weeks with the most singles on the chart, making her the best artist this year"



best_artist(datetime.today())


chart_df = get_weeks_between(date_shift(datetime.today(), 14), datetime.today())
chart_df.to_csv("bill_week.csv")
# Initialise the columns of the dataframe and set their types
song_df = pd.DataFrame(columns=["week", "title", "artist", "rank", "last_week", "peak_pos", "weeks_on_chart"])
song_df.astype({'week': 'datetime64', "title": "str", "artist": "str", "rank": "int64",
                "last_week": "int64", "peak_pos": "int64", "weeks_on_chart": "int64"})

# Create a plot
colors = {"red": "#FF0000", "green": "#00FF00", "blue": "#0000FF"}
fig = plt.figure(figsize=(20, 7), dpi=100)
ax = fig.add_subplot(111)

for i in range(0, 100):
    curr_rank = chart_df["rank"].loc[i]
    curr_last_week = chart_df["last_week"].loc[i]
    curr_weeks_on_chart = chart_df["weeks_on_chart"].loc[i]
    if curr_rank == curr_last_week:
        color = colors["blue"]
    elif curr_rank > curr_last_week:
        color = colors["red"]
    else:
        color = colors["green"]
    ax.scatter(curr_rank, curr_weeks_on_chart, color=color)

plt.xticks(chart_df["rank"], chart_df.apply(lambda x: str(x["rank"]) + " " + " ".join(x["title"].split(" ")[:3])
if len(x["title"].split(" ")) > 3
else str(x["rank"]) + " " + x["title"], axis=1), rotation=-90)

plt.xlabel("Ranks and titles")
plt.ylabel("# Weeks on the chart")
# prevent xticks from getting chopped off
plt.tight_layout()
# plt.show()
plt.savefig('testplot.png')
