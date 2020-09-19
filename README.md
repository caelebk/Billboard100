# Project 1 -- Billboard 

Learning objectives:

- Become more adept at web scraping
- Use pandas data frames as a fundamental structure
- Filter, project, reassemble data frames to extract information
- Report and visualize information using a variety of plots

In class we explored a technique for extracting data from a web page using a web-scraping library called Beautiful Soup. 
This project extends that work to include not just a single week's rankings, but many *years* of rankings!

### Part 1 -- Assembling the data

Write a function called `get_weeks_between(date1:datetime, date2:datetime) -> pd.DataFrame`, which takes two dates as input
and which returns a data frame including every week from the billboard hot-100 between (and including) the two dates. 

Use that function to create a csv file called "songs_of_my_life.csv" containing all the charts within your lifetime.

### Part 2 -- Using the data

Write the following two functions:

- `best_week(year:datetime) -> Week` given a date, this function returns the best week of the year following that date.
A *best week* is the week that has the largest number of songs that were #1 at some point.

- `best_song(year:datetime) -> Song` given a date, this function returns the best song of the year following that date.
We leave it to you to define what it means for a song to be the best! 

Determination of Best Song:
The best song of the year has been both #1 rank and has to still be on the chart at the end of year/the most recent date. Therefore, I looked for the longest song on the chart and made sure that song has also been number one before.


### Part 3 -- Visualizing the data

Complete the following plots based on the data you assembled in Part 1:

- On a single plot, 
display the lifetime trajectory of every song that was ever #1, between a pair of given dates. 
For the purpose of this exercise, a 
song's *lifetime* corresponds to the set of weeks for which it appears on the chart. The song's *trajectory* is a line graph 
of its rank over those weeks. To do this you will write a function called `number_ones(date1:datetime, date2:datetime)`
which both shows a plot and saves it to a file named `num_ones.png`.

### Part 4 -- Who's the best artist?

Use the data from the Billboard Hot 100, over any time span, to answer "Who's the Best Artist?" 

Justification of the best Artist:
The best artist of the year is the artist that has the most best artists of the week. Best artist of the week is the artist with the most songs on the chart. Therefore, the best artist of the year is represented by the number of times, he/she has had the most songs on the chart. 
I did this by first collecting all the best artists of the week into one dataframe, and then getting the artist that appeared the most!
I also created a bar plot here to show that you don't have to have the most songs on the chart to be the best artist of the year,
you just have to have the most consistent record of being the best.








