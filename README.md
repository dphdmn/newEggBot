# eggbot
Egg bot for sliding puzzle discord server
https://discord.gg/7vXrWAS3yZ

WR commands:
- !getwr [NxM] - get WR single for NxM puzzle
- !wrsby [username] - get all WRs by that username
- !wrupdate - update WR pages

FMC commands
- !fmc - get current fmc information
- !submit [solution] - submit solution to current fmc
- !results - get results of current fmc
- !startfmc - start new 10 minute fmc

Movesgame commands
- !movesgame - start new movesgame
- !tournament - start new movesgame tournament
- !results - view lifetime results of movesgame

PB/ranks commands
- !getpb [user] [puzzle=NxN] - get user's PBs for 3x3 to 10x10 puzzle. default puzzle size is 4x4, or the channel size in the 3x3-10x10 channels
- !getreq [tier] [puzzle] - get time requirement for a tier
- !getlb - get current version of the webpage as a text file
- !update - update the ranks webpage
- !datecompare [date1] [date2] - compare two states of leaderboard (!datecompare 2021-06-14 2021-06-13)
- !anoncmp - compare from last anon date to today's date

Solver-related commands:
- !solve [scramble] - optimally solve a scramble (3x3 or 4x4)
- !eggsolve [scramble] - find all optimal solutions (3x3 or 4x4)
- !goodm [scramble] - find good moves for a scramble (3x3 or 4x4)
- !video [scramble] - same as !solve but also generates a video
- !analyse [solution] - analyse a solution and find mistakes
- !analyse3x3 - upload a file containing solutions (one per line). calculates how many were optimal, +2, +4, etc.

Scramble/solution-related commands:
- !rev [solution] - reverse the solution of scramble, use RLUD notation, you can also use numbers like in slidysim
- !not [solution] - change notation (R = L, U = D) etc. of the solution
- !draw [scramble] - draws image of a 4x4 scramble
- !animate [scramble=solution-inverse] [solution] [tps=8] - makes an animation of your solve (4x4 only)
- !getreal - generates a scramble algorithm and draws a picture of it
- !getscramble [N=4] - generates a random scramble for an NxN puzzle
- !simplify [solution] - removes mistakes like UD or LR from a solution
- !solvable [scramble] - check if a position is solvable

Misc. commands:
- !getprob [NxM] mo[N=1] [moves-range] [repetitions=1] - compute probability of an NxM single/mean having an optimal solution length within a given range of moves, after some number of attempts
- !paint [size] - paint image into slidysim scramble, use size to  make it custom puzzles size (up to 256), you should upload image as attachment 
- !8fmc [N=100] - generate N random scrambles and optimal solution lengths, for use with 8 puzzle 100x fmc
- !egg - 🥚
- !help - link to this file
- !tti [text] - bad AI image generator

Technical commands to compare rank pages (will be removed or changed in next updates probably):
- !cmp1 [file] - old file to compare [technical]
- !cmp2 [file] - new file to compare [technical]
- !compare - get compare of last 2 uploaded tables [technical]
- !savecmp - saves current compare state to "anon" date [technical] [admin]

Spamming fun commands:
- !spam [something] - make bot spam something many times [admin]
- !stop - make bot stop spamming [admin]

List of useful websites:
- Ranks - https://egg.benwh1.repl.co/
- WRs - http://slidysim.000webhostapp.com/leaderboard/records.html
- WRs (all) - http://slidysim.000webhostapp.com/leaderboard/records_all.html
- WRs (moves) - http://slidysim.000webhostapp.com/leaderboard/records_moves.html
- WRs (moves, all) - http://slidysim.000webhostapp.com/leaderboard/records_all_moves.html
