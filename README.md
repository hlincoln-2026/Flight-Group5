## Tasks

#Part 3
1. (Done) Verify that the distances you computed in part 1 are roughly equal to the dis- tances in the variable distance in the table flights . If they are much off, recall that latitude and longitude represent angles expressed in degrees, while the functions sin and cos expects entries in radial angles
2. (Done) For each flight, the origin from which it leaves can be fount in the variable origin in the table . Identify all different airports in NYC from
which flights depart and save a contain the information about those
airports from airports.
3. (Dion) Write a function that takes a month and day and an airport in NYC as input,
and produces a figure similar to the one from part 1 containing all destinations
of flights on that day.
4. (Dion) Also write a function that returns statistics for that day, i.e. how many flights,
how many unique destinations, which destination is visited most often, etc.
5. (Done) Write a function that, given a departing airport and an arriving airport, returns a dict describing how many times each plane type was used for that flight
trajectory. For this task you will need to match the columns to type
in the table planes and match this to the tailnum s in the table .
6. (Done) Compute the average departure delay per flight for each of the airlines. Visualize
the results in a barplot with the full (rotated) names of the airlines on the x-axis.
7. (Done) Write a function that takes as input a range of months and a destination and
returns the amount of delayed flights to that destination.
8. (Done) Write a function that takes a destination airport as input and returns the top 5
airplane manufacturers with planes departing to this destination. For this task,
you have to combine data from flights and planes.
9. (Atish) Investigate whether there is a relationship between the distance of a flight and
the arrival delay time.
10. Group the table flights by plane model using the tailnum . For each model,
compute the average speed by taking the average of the distance divided by flight time over all flights of that model. Use this information to fill the column speed
in the table planes .
11. The wind direction is given in weather in degrees. Compute for each airport the direction the plane follows when flying there from New York.
12. (Julie) Write a function that computes the inner product between the flight direction and the wind speed of a given flight.
13. (Julie) Is there a relation between the sign of this inner product and the air time?

# Part 4
1. (Hunter) Check the table flights for missing values think of ways to resolve them.
2. (Hunter) Look for duplicates in the flights table. Take into account that here a flight number can occur multiple times, only count it as duplicate when the same flight
appears multiple times.
3. (Hunter) Convert the (schedueled and actual) arrival departure and departure moments
to datetime objects.
4. Write a function that checks whether the data in   is in order. That
is, verify that the air time , dep time ,   etc. match for each
flight. If not, think of ways to resolve it if this is not the case.
5. Create a column that contains the local arrival time, incorporating the time
difference between arrival and departure airport.
6. In addition, information on the different types of planes and airlines will be
important. Consider studying what the effect of the wind or precipitation is on
different plane types.
7. Next week, the specifics of the dashboard will be released. Count on requirements asking for the statistics for different departure and arrival airports. Consider making functions that take these airports as input and generate numerical or graphical representations of the data grouped by them. Many of the tasks from the previous parts can be grouped!
   
9. (Atish) The dashboard will also contain a general results tab that can show anything you find remarkable in the data. Think of things you would like to display here. Are there interesting relations to be seen in the data? Are there airports that stand out when it comes to delay? Are there plane times that fly considerable faster? Which plane routes are taken most often from NYC? Is there a significant relation between (some) weather variables and the delay time? Come up with convincing graphical or numerical summaries that can be displayed in this part of the dashboard to display the results of the study.



# Flight Information Monitoring Project Group 5

# Introduction

This project analyzes and visualizes flight data for flights departing from New York City in 2023. The final output will be a dashboard that provides various insights into flight patterns, distances, delays, and other key information.

## Table of Contents

1. [Getting Started]()
2. [Project Structure]()
3. [Installation]()
4. [Usage]()
5. [Features]()
6. [Contributing]()
7. [License]()

## Getting Started

This project uses Python for data analysis and visualization, along with libraries such as pandas, plotly, and sqlite3. The dataset includes information about flights, airports, airlines, planes, and weather conditions.

## Project Structure

```

```

## Installation

To set up the environment, follow these steps:

1. Clone this repository:
   ```
   git clone <https://github.com/hlincoln-2026/Flight-Group5.git>
   ```
2. 

## Usage

### Part 1: Airport Data Visualization

* Load** **`<span>airports.csv</span>` using pandas
* 

## License

This project is licensed under the MIT License.
