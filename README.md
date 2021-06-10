# newEggBot
Egg bot for sliding puzzle discord server
https://discord.gg/7vXrWAS3yZ

WR-related commands:
- !getwr <NxM> - get wr for this puzzle (single)
- !wrsby <username> - get all wrs for that username
PB/ranks-related commands
- !getpb <user> <puzzle> - get pb for one of 30 main categories in tier ranks, puzzle for 3x3 to 10x10
- !getreq <tier> <puzzle> - get requirement for getting tier in new ranked system
- !getlb - get current version of leaderboard (ascii style)
- !update - updates current pbs for getpb command, also gives a file of current pbs at 30 tiers  [technical]

Solver-related commands:
- !getreal - returns real scramble (moves) and draws a picture of it
- !getscramble (size-optionally) - get random puzzle for sliding puzzle with that size
- !movesgame - find a good moves for a random scramble game
- !solve <scramble> - solve some 4x4 scramble

Scramble/solution-related commands:
- !rev <solution> - reverse the solution of scramble, use RLUD notation, you can also use numbers like in slidysim
- !not <solution> - change notation (R = L, U = D) etc. of the solution
- !draw <scrambles> - draws image of your scramble
- !video <scramble> - like !solve but also get a video
- !animate\n<scramble>\n<solution>\n(tps - optionally) - makes an animation of your solve (use new string as separator! not just space)
- !analyse\n<scramble>\n<solution>  - analyse solution for the scramble and find mistakes (use new string as separator! not just space) [admin]

Fun/stats commands:
- !getprob <puzzle> <moves> [<moves>, <amount> || <amount] - get probability of getting N moves optimal scramble, type !getprob for examples
- !paint [<size>] - pain image into slidysim scramble, use size to  make it custom puzzles size (up to 256), you should upload image as attachment 
- !tti <text> - funny function, gives some image, don't spam it

Technical commands to compare rank pages (will be removed or changed in next updates probably):
- !cmp1 <file> - old file to compare [technical]
- !cmp2 <file> - new file to compare [technical]
- !compare - get compare of last 2 uploaded tables [technical]

Spamming fun commands:
- !spam <something> - make bot spam something many times [admin]
- !stop - make bot stop spamming [admin]

