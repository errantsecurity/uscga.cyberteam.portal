How to Build "Warmup"
=============

> John Hammond | July 21st, 2017


The "warmup" challenge is one of the smallest challenges that I've made, because it is just a simple [`strings`][strings] solution.

The user is prompted with a file, in this case just a [PNG] image of a cat, [`kitty.jpg`]

As the challenge designer, I need a way to place the flag text inside of the file. Since this is an image and all of the binary data in the file is important, it is "hard" to smuggle in the text.

So I kind of cheat.

Image viewer applications will parse an image until they reach the end of image data... so we can "tack on" whatever data we want _after the image data_ and the real picture will still remain intact.  

Since we want the data put together, I just create a specific file for the flag `flag.txt` and I can combine it with the image file with just the [`cat`][cat] command.

Personally I don't want the flag just at the very end of the file (which also means the very end of `strings` input, not very realistic) so I actually duplicate the image again. 

That means I build the image like this:

```
 #!/bin/bash
cat image.png flag.txt image.png > kitty.jpg
```

And then the final file, `kitty.jpg` can be used with [`strings`][strings] to get the flag.


[PNG]: 
[strings]: 
[cat]: 