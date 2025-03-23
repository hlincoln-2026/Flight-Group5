# Flight Information Dashboard

## Overview

This project provides an interactive dashboard to monitor and analyze flight information from New York City for the year 2023. The dashboard aggregates data from several sources (flights, airlines, airports, planes, and weather) stored in a SQLite database and visualizes various flight statistics using Streamlit and Plotly.

## Features

* **Flight Statistics:** Displays total flights, unique destinations, most/least frequent routes, and flight lengths.
* **Airline Market Share:** Visualizes the number of flights per airline.
* **Monthly Flight Trends:** Shows flight counts by month, with optional filtering by airline.
* **Plane Performance:** Lists the top 10 fastest plane models based on calculated average speeds.
* **Manufacturer Analysis:** Compares the top airplane manufacturers for selected international destinations.
* **Delay & Weather Analysis:** Compares departure delays across major NYC airports, including related weather information.
* **Interactive Maps:** Visualizes airports on global and US-specific maps with flight paths.

## Project Structure

* **dashboard.py** – Main dashboard script that ties all the functionalities together.
* **part1.py** – Contains functions related to airport map visualizations and flight paths.
* **part3.py** – Includes functions for computing NYC airport statistics and departure delay analysis.
* **part4.py** – Provides additional data wrangling utilities.
* **flights_database.db** – SQLite database containing the flight, airlines, airports, planes, and weather data.

## Installation

1. **Clone the Repository:**

   ```
   git clone < https://github.com/hlincoln-2026/Flight-Group5.git>
   ```
2. **Install Dependencies:**

   ```
   pip install -r requirements.txt
   ```
3. **Run the Dashboard:**

   ```
   streamlit run app.py
   ```

## Usage

* Use the sidebar to select departure and arrival airports and to input a date.
* Navigate through the different sections to view general flight statistics, map visualizations, delay comparisons, and more.
* The dashboard provides interactive elements for filtering data and exploring specific flight details.
