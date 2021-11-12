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
- [---] [bookrecommend.py](bookrecommend.py)
- [x] [database.py](database.py)
- [x] [menu.py](menu.py) - no test code
- [ ] [README](README) (optional)
- [x] [utils.py](utils.py)

Key:
- \-:  started
- \--: done functionality
- \---: started gui
- o: need to do module docstring
- xx: need to write test code
- x: DONE DONE

## Restrictions

- NO Class types
- NO SQL statements
- NO nested functions
- ONLY use standard python libraries and Matplotlib

## How I'm doing things

- As I can't use classes, store books as `dicts` (see [database.py](database.py))
- Also store logs as `dicts`

## Notes

Needs tests at the end of each module


## database
```text
1,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
2,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
3,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
4,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
5,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
6,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
7,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
8,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
9,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
10,Sci-Fi,A Sci-Fi Adventure,John Smith,01/08/2010,0
11,Action,Avengers,Stan Lee,01/07/2003,0
12,Action,Avengers,Stan Lee,01/07/2003,0
13,Action,Avengers,Stan Lee,01/07/2003,0
14,Action,Avengers,Stan Lee,01/07/2003,0
15,Action,Avengers,Stan Lee,01/07/2003,0
16,Action,Avengers,Stan Lee,01/07/2003,0
17,Action,Avengers,Stan Lee,01/07/2003,0
18,Action,Avengers,Stan Lee,01/07/2003,0
19,Action,Avengers,Stan Lee,01/07/2003,0
20,Action,Avengers,Stan Lee,01/07/2003,0
21,Action,Avengers,Stan Lee,08/11/2003,0
22,Action,Avengers,Stan Lee,08/11/2003,0
23,Action,Avengers,Stan Lee,08/11/2003,0
24,Action,Avengers,Stan Lee,08/11/2003,0
25,Action,Avengers,Stan Lee,08/11/2003,0
26,Action,Avengers,Stan Lee,08/11/2003,0
27,Action,Avengers,Stan Lee,08/11/2003,0
28,Action,Avengers,Stan Lee,08/11/2003,0
29,Action,Avengers,Stan Lee,08/11/2003,0
30,Action,Avengers,Stan Lee,08/11/2003,0
31,Crime,Burn the Past,Eva Smith,03/10/2007,0
32,Crime,Burn the Past,Eva Smith,03/10/2007,0
33,Crime,Burn the Past,Eva Smith,03/10/2007,0
34,Crime,Burn the Past,Eva Smith,03/10/2007,0
35,Crime,Burn the Past,Eva Smith,03/10/2007,0
36,Crime,Burn the Past,Eva Smith,03/10/2007,0
37,Crime,Burn the Past,Eva Smith,03/10/2007,0
38,Crime,Burn the Past,Eva Smith,03/10/2007,0
39,Crime,Burn the Past,Eva Smith,03/10/2007,0
40,Crime,Burn the Past,Eva Smith,03/10/2007,0
41,Crime,An Inspector Calls,John Priestley,06/07/1945,0
42,Crime,An Inspector Calls,John Priestley,06/07/1945,0
43,Crime,An Inspector Calls,John Priestley,06/07/1945,0
44,Crime,An Inspector Calls,John Priestley,06/07/1945,0
45,Crime,An Inspector Calls,John Priestley,06/07/1945,0
46,Crime,An Inspector Calls,John Priestley,06/07/1945,0
47,Crime,An Inspector Calls,John Priestley,06/07/1945,0
48,Crime,An Inspector Calls,John Priestley,06/07/1945,0
49,Crime,An Inspector Calls,John Priestley,06/07/1945,0
50,Crime,An Inspector Calls,John Priestley,06/07/1945,0
51,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
52,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
53,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
54,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
55,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
56,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
57,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
58,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
59,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
60,Tragedy,Macbeth,William Shakespeare,25/10/2019,0
61,Romance,Sinful Duty,Sally Young,07/09/2003,0
62,Romance,Sinful Duty,Sally Young,07/09/2003,0
63,Romance,Sinful Duty,Sally Young,07/09/2003,0
64,Romance,Sinful Duty,Sally Young,07/09/2003,0
65,Romance,Sinful Duty,Sally Young,07/09/2003,0
66,Romance,Sinful Duty,Sally Young,07/09/2003,0
67,Romance,Sinful Duty,Sally Young,07/09/2003,0
68,Romance,Sinful Duty,Sally Young,07/09/2003,0
69,Romance,Sinful Duty,Sally Young,07/09/2003,0
70,Romance,Sinful Duty,Sally Young,07/09/2003,0
71,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
72,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
73,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
74,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
75,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
76,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
77,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
78,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
79,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
80,Mystery,Secret of the Misshapen Headmaster,John Oakes,01/04/1995,0
81,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
82,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
83,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
84,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
85,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
86,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
87,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
88,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
89,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
90,Fantasy,Blade of Fire,Stuart Hill,04/09/2006,0
91,Romance,Love...,Ben Daly,30/12/2012,0
92,Romance,Love...,Ben Daly,30/12/2012,0
93,Romance,Love...,Ben Daly,30/12/2012,0
94,Romance,Love...,Ben Daly,30/12/2012,0
95,Romance,Love...,Ben Daly,30/12/2012,0
96,Romance,Love...,Ben Daly,30/12/2012,0
97,Romance,Love...,Ben Daly,30/12/2012,0
98,Romance,Love...,Ben Daly,30/12/2012,0
99,Romance,Love...,Ben Daly,30/12/2012,0
100,Romance,Love...,Ben Daly,30/12/2012,0
```
