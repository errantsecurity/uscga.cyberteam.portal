#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: john
# @Date:   2017-01-16 10:17:31
# @Last Modified by:   john
# @Last Modified time: 2017-02-10 20:17:55

minimum = 1
maximum = 10000

# Seed the random number generator...
random.seed('random seed')

# Loop through a random number of numbers ... for extra randomness!
for _ in range(random.randint(minimum, maximum)):
	
	random.randint(minimum, maximum)
	# Evaluate MORE random numbers.... so it's so random, you can't beat it!

special_number = random.randint(minimum, maximum)

print("I'm thinking of a number between %d and %d!" % (minimum, maximum))
print("If you can guess it, I will give you a flag!")
print("")
print("So what is your guess?")


guess = raw_input()
if ( int(guess) == special_number ):
	self.send( "Wow, you got it! As promised, here is your reward:" )
	self.send( open("flag.txt").read() )
else:
	self.send( "NOPE! Wrong! Come on, how could you not guess it? Better luck next time!" )
