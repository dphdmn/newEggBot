# newEggBot
Egg bot for sliding puzzle discord server
https://discord.gg/7vXrWAS3yZ

WR-related commands:
- !getwr [NxM] - get wr for this puzzle (single)
- !wrsby [username] - get all wrs for that username

FMC-competion related commands:
- !submit [solution] - submit solution to current fmc competition
- !daily_scramble - get current scramble of fmc competition
- !daily_open - start FMC competition [admin]
- !daily_close - finish FMC competition [admin]


PB/ranks-related commands
- !getpb [user] [puzzle] - get pb for one of 30 main categories in tier ranks, puzzle for 3x3 to 10x10
- !getreq [tier] [puzzle] - get requirement for getting tier in new ranked system
- !getlb - get current version of leaderboard (ascii style)
- !update - updates current pbs for getpb command, also gives a file of current pbs at 30 tiers  [technical]
- !datecompare [date1] [date2] - compare two states of leaderboard (!datecompare 2021-06-14 2021-06-13)

Solver-related commands:
- !solve [scramble] - solve some 4x4 or 3x3 scramble
- !eggsolve [scramble] - solve 4x4 or 3x3 scramble and find all possible optimal solutions
- !goodm [scramble] - find good moves for some 3x3 or 4x4 scramble
- !video [scramble] - like !solve but also get a video
- !getreal - returns real scramble (moves) and draws a picture of it
- !movesgame - find a good moves for a random scramble game
- !analyse\n[scramble]\n[solution]  - analyse solution for the scramble and find mistakes (use new string as separator! not just space)

Scramble/solution-related commands:
- !rev [solution] - reverse the solution of scramble, use RLUD notation, you can also use numbers like in slidysim
- !not [solution] - change notation (R = L, U = D) etc. of the solution
- !getscramble (size-optionally) - get random puzzle for sliding puzzle with that size
- !draw [scrambles] - draws image of your scramble
- !animate\n[scramble]\n[solution]\n(tps - optionally) - makes an animation of your solve (use new string as separator! not just space)

Fun/stats commands:
- !getprob [puzzle] [moves] [[moves], [amount] || [amount] - get probability of getting N moves optimal scramble, type !getprob for examples
- !paint [[size]] - pain image into slidysim scramble, use size to  make it custom puzzles size (up to 256), you should upload image as attachment 
- !tti [text] - funny function, gives some image, don't spam it

Technical commands to compare rank pages (will be removed or changed in next updates probably):
- !cmp1 [file] - old file to compare [technical]
- !cmp2 [file] - new file to compare [technical]
- !compare - get compare of last 2 uploaded tables [technical]
- !savecmp - saves current compare state to "anon" date [technical] [admin]

Spamming fun commands:
- !spam [something] - make bot spam something many times [admin]
- !stop - make bot stop spamming [admin]

