# A Problem with Presidents; a data to information challenge.

- Author: Christopher P. Barnes, Samantha Emerson
- Date: October 27, 2026

## Problem Statement:

A fairly common statement you may hear is that data becomes information, information becomes knowledge, and knowledge becomes wisdom. Our job is primarily involved in using computer code, mathematics and experience to convert data into information. To become information, the data must be taken from a source, transformed into input, processed by a set of algorithms, transformed into output, and delivered to a consumer.

Date math and basic exploratory data analysis using descriptive statistics are a corner stone of writing computer code to manage real world data that occurs in a longitudinal manner. The goal of this problem is to give you a simple data set to allow you to demonstrate your understanding of how to apply computer code to solve a problem and then further use computer code to communicate your new information to people.

To complete your application, follow these steps:

First fork this repo to your own github account. 

Second, using the given data and Python or R; add new variables called year_of_birth, lived_years, lived_months, lived_days then make two well formatted output tables ranking the top 10 Presidents from longest lived to shortest lived and then the top 10 presidents from shortest lived to longest lived.

*Note: Using agents to aid with coding is OK. In that case, you must include the infrastructure required for a coding agent to operate in your repository (agents.md, etc).*

Then, using your newly-created data and **Python or R**, calculate the mean, weighted average, median, mode, max, min and standard deviation of lived_days for your data set. Output these measures in a well-formatted table. Then, make a plot of a type that you think best shows the distribution of this data.

Assemble your tables and plot into a single report with a title, author and date. Start the report with a 3 or 4 sentence summary of what you found, the body should have your tables and plot and any commentary about your methods or assumptions you think the reader would need to know. Finish the report with a conclusions section, where you state the conclusions you reached through this analysis.

To finish, commit all your code and your report in pdf form to your personal Github fork of this repository, and then email back CTS-IT with a link to your completed problem.

During the interview phase, we will ask for a tour of your code. You must be able to explain your methodology, the results, your choice in plot(s), and what you chose to include in your report.

Good Luck!   


References:
https://eng.libretexts.org/Bookshelves/Industrial_and_Systems_Engineering/Book%3A_Chemical_Process_Dynamics_and_Controls_(Woolf)/13%3A_Statistics_and_Probability_Background/13.01%3A_Basic_statistics-_mean%2C_median%2C_average%2C_standard_deviation%2C_z-scores%2C_and_p-value

Reference:
Birthplace, Birthdate, and Death information of the U.S. Presidents. (n.d.). PresidentsUSA.Net. Retrieved September 28, 2021, from https://www.presidentsusa.net/birth.html

## Solution — Zlata Kovrigina

Run `python3 analyze.py` to create `report.pdf` and `presidents_with_lifespans.csv`.

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 analyze.py
```