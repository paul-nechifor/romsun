Romsun: Romanian text to phoneme convertor
==========================================

Back in 2009 I couldn't find any free text-to-speech library for Romanian, but I
did find that the [MBROLA speech synthesizer][1] supported reading Romanian
phonemes so I wrote this to transform Romanian text to the `.pho` files needed
by MBROLA.

It's not that good, but it's better than nothing. I used it for awesome things
like reading the instant messages I get from people (a Pidgin module), counting
sheep in Romanian so I can go to sleep faster, getting audio notifications of
when a website gets updated... I mean, really, Nobel prize material.

Requirements
------------

First, get the [MBROLA binary][2] and install it. Get the `ro1` voice from same
page and put it in this directory.

You need a WAV player. On Ubuntu you can get the `play` program by installing:

    sudo apt-get install sox

Usage
-----

Once you have those you can use the `spune` Bash script.

    ./spune 'Eu zic că se aude destul de bine.'


[1]: http://en.wikipedia.org/wiki/MBROLA
[2]: http://tcts.fpms.ac.be/synthesis/mbrola/mbrcopybin.html
