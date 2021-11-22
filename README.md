# 21COA122cw

## Overview

Simple library management system for a librarian

- Search for books by title to check availability
- Check out available books
- Return any books the members currently have

### Database (book info)

- unique ID number (help identify diff copies of same book)
- Genre
- Title
- Author
- Purchase date
- Current loan status (is it available - if no, who has it)

`database.txt` has to be organised as:

| ID  | Genre | Title | Author | Purchase Date | Member |
| --- | ----- | ----- | ------ | ------------- | ------ |
| 1 | Sci-Fi | Book_1 | Author_1 | 1/8/2010 | coai |
| 2 | Fantasy | Book_3 | Author_2 | 1/8/2014 | 0 |

### Members

- Should be identified using their email address,
member-ID is 4 letters - first part of email address (e.g.: “coai” for coai@lboro.ac.uk)

### Search for books

- Need functionality to search for a book based on its title
- Given a search term, return a complete list of books with that title and all their associated information
- Additionally, must highlight the books which are on loan more than 60 days (GUI?)

## File Structure

- [x] [database.txt](database.txt)
- [x] [logfile.txt](logfile.txt)
- [x] [booksearch.py](booksearch.py) - can probably add more to module docstring
- [x] [bookcheckout.py](bookcheckout.py)
- [x] [bookreturn.py](bookreturn.py)
- [x] [bookrecommend.py](bookrecommend.py) - no test code
- [x] [database.py](database.py)
- [x] [menu.py](menu.py) - no test code
- [ ] [README](README) (optional)

## Restrictions

- NO Class types
- NO SQL statements
- NO nested functions
- ONLY use standard python libraries and Matplotlib

## How I'm doing things

- As I can't use classes, store books as `dicts` (see [database.py](database.py)) - use SimpleNamespace???
- Also store logs as `dicts`
- Recommending books
  - Uses a score system (based on how much the user likes the genre and how popular the book is)
  - Users with only 1 genre, shows the 3 books of that genre
  - Users with 2 genres, shows the 6 books of those genres
  - ... 3 genres, shows the 9 books ...

## Notes

Need tests at the end of each module

## Extra features

- booksearch.py
  - [x] ignore case
  - [x] contains
- bookcheckout.py
- bookreturn.py
- bookrecommend.py


## database
10 genres, 3 books each, 3 copies each = 90 entries
```text
1,Action,Avengers,Stan Lee,01/07/2003,0
2,Action,Avengers,Stan Lee,01/07/2003,0
3,Action,Avengers,Stan Lee,01/07/2003,0
4,Action,Reflex Conquest,Jim Bob,08/07/2011,0
5,Action,Reflex Conquest,Jim Bob,14/03/2012,0
6,Action,Reflex Conquest,Jim Bob,14/03/2012,0
7,Action,Soldier of Impact,Luke Rissacher,08/12/2015,0
8,Action,Soldier of Impact,Luke Rissacher,08/12/2015,0
9,Action,Soldier of Impact,Luke Rissacher,08/12/2015,0
10,Crime,Burn the Past,Eva Smith,03/10/2007,0
11,Crime,Burn the Past,Eva Smith,03/10/2007,0
12,Crime,Burn the Past,Eva Smith,03/10/2007,0
13,Crime,An Inspector Calls,John Priestley,06/07/1995,0
14,Crime,An Inspector Calls,John Priestley,06/07/1995,0
15,Crime,An Inspector Calls,John Priestley,06/07/1995,0
16,Crime,Kill the Truth,Robin Messer,03/10/1995,0
17,Crime,Kill the Truth,Robin Messer,03/10/1995,0
18,Crime,Kill the Truth,Robin Messer,03/10/1995,0
19,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
20,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
21,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
22,Fantasy,Titan's Legacy,Malini Smolak,14/05/2015,0
23,Fantasy,Titan's Legacy,Malini Smolak,14/05/2015,0
24,Fantasy,Titan's Legacy,Malini Smolak,14/05/2015,0
25,Fantasy,Call of Shadows,Odila Veith,30/07/2005,0
26,Fantasy,Call of Shadows,Odila Veith,30/07/2005,0
27,Fantasy,Call of Shadows,Odila Veith,30/07/2005,0
28,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
29,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
30,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
31,Mystery,Clue of the Forgotten Staircase,Albina Smith,09/10/2011,0
32,Mystery,Clue of the Forgotten Staircase,Albina Smith,09/10/2011,0
33,Mystery,Clue of the Forgotten Staircase,Albina Smith,09/10/2011,0
34,Mystery,?,Albina Smith,10/10/2010,0
35,Mystery,?,Albina Smith,10/10/2010,0
36,Mystery,?,Albina Smith,10/10/2010,0
37,Romance,Sinful Duty,Sally Young,07/09/2003,0
38,Romance,Sinful Duty,Sally Young,07/09/2003,0
39,Romance,Sinful Duty,Sally Young,07/09/2003,0
40,Romance,Love...,Ben Daly,30/12/2012,0
41,Romance,Love...,Ben Daly,30/12/2012,0
42,Romance,Love...,Ben Daly,30/12/2012,0
43,Romance,Toxic,Rhys Herbert,29/07/2000,0
44,Romance,Toxic,Rhys Herbert,29/07/2000,0
45,Romance,Toxic,Rhys Herbert,29/07/2000,0
46,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
47,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
48,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
49,Sci-Fi,Wonderland,Daniel Lena,17/08/1999,0
50,Sci-Fi,Wonderland,Daniel Lena,17/08/1999,0
51,Sci-Fi,Wonderland,Daniel Lena,17/08/1999,0
52,Sci-Fi,Triple Science,Irving Adjei,06/10/1994,0
53,Sci-Fi,Triple Science,Irving Adjei,06/10/1994,0
54,Sci-Fi,Triple Science,Irving Adjei,06/10/1994,0
55,Tragedy,Who's True?,Dennis Odunwo,01/09/1993,0
56,Tragedy,Who's True?,Dennis Odunwo,01/09/1993,0
57,Tragedy,Who's True?,Dennis Odunwo,01/09/1993,0
58,Tragedy,Say My Name,Riley Davies,17/09/2002,0
59,Tragedy,Say My Name,Riley Davies,17/09/2002,0
60,Tragedy,Say My Name,Riley Davies,17/09/2002,0
61,Tragedy,Macbeth,William Shakespeare,25/10/1990,0
62,Tragedy,Macbeth,William Shakespeare,25/10/1990,0
63,Tragedy,Macbeth,William Shakespeare,25/10/1990,0
64,Drama,Are You Mad,Devonte Perkins,21/10/1995
65,Drama,Are You Mad,Devonte Perkins,21/10/1995
66,Drama,Are You Mad,Devonte Perkins,21/10/1995
67,Drama,Wait Til' I Finish,Marvin Huncho,17/11/1993,0
68,Drama,Wait Til' I Finish,Marvin Huncho,17/11/1993,0
69,Drama,Wait Til' I Finish,Marvin Huncho,17/11/1993,0
70,Drama,Money Talks,Marvin Bailey,06/03/1994,0
71,Drama,Money Talks,Marvin Bailey,06/03/1994,0
72,Drama,Money Talks,Marvin Bailey,06/03/1994,0
73,Adventure,The Great Escape,Joshua Eduardo,08/03/1999,0
74,Adventure,The Great Escape,Joshua Eduardo,08/03/1999,0
75,Adventure,The Great Escape,Joshua Eduardo,08/03/1999,0
76,Adventure,Bad Habits,Oakley Caesar-Su,04/06/1998,0
77,Adventure,Bad Habits,Oakley Caesar-Su,04/06/1998,0
78,Adventure,Bad Habits,Oakley Caesar-Su,04/06/1998,0
79,Adventure,'Till I Collapse,Marshall Mathers III,17/10/1972,0
80,Adventure,'Till I Collapse,Marshall Mathers III,17/10/1972,0
81,Adventure,'Till I Collapse,Marshall Mathers III,17/10/1972,0
82,Horror,Thriller,Michael Jackson,25/06/2009,0
83,Horror,Thriller,Michael Jackson,25/06/2009,0
84,Horror,Thriller,Michael Jackson,25/06/2009,0
85,Horror,Untitled,Darren Diggs,10/11/1999,0
86,Horror,Untitled,Darren Diggs,10/11/1999,0
87,Horror,Untitled,Darren Diggs,10/11/1999,0
88,Horror,Robbery,Abra Cadabara,04/11/2016,0
89,Horror,Robbery,Abra Cadabara,04/11/2016,0
90,Horror,Robbery,Abra Cadabara,04/11/2016,0
```
