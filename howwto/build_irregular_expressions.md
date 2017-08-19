How to Build "Irregular Expressions"
=============

> John Hammond | July 21st, 2017

This is a web challenge which encompasses [Remote Code Execution][RCE], so I run it within a [Docker] container. It is just a [PHP][PHP] [web server], so we can use a pre-built [Docker] container and we don't have to create our own. I use `eboraas/apache-php`.


The PHP
-----------

Before I get into the [Docker] setup, I'll show the real code and the meat of the challenge. I just have one file, [`index.php`][index.php], which has [PHP] for the real logic of the challenge, and [HTML] and [CSS] for the display.  The [PHP] code is really the only interesting piece.

```
<?php
    
    $pattern = "/quick/i";
    $replace = "slow";
    $text = "The quick brown fox jumped over the lazy dog.";

    if ( 
        isset($_POST['pattern'])  &&
        isset($_POST['replace'])  &&
        isset($_POST['text'])
     ){

        $pattern = $_POST['pattern'];
        $replace = $_POST['replace'];
        $text = $_POST['text'];
        $replaced = preg_replace($_POST['pattern'], $_POST['replace'], $_POST['text']);


    }
?>
```

At the very top I create some variables that just act as placeholders, in case the user has not already supplied these variables by interacting with the web form.

The challenge is displayed as a web application that takes advantage of [regular expressions] to find and replace text. The vulnerability here is the usage of the [PHP] function [`preg_replace`][preg_replace] with untrusted and unsanitary input. Earlier version of [PHP] can have this function run arbitrary commands by changing some of the parameters given in the [regular expression] string.

I test if the communication to the page has been done with the [HTTP][HTTP] [POST] method, and if so, I grab the variables passed by the [HTML][HTML] [form]. Then I just pass it all to the [`preg_replace`][preg_replace] function. I store the result in the `$replaced` variable, which [PHP] will go ahead and output with the [HTML].


The HTML and CSS
------

To give a hint to the user about this [`preg_replace`][preg_replace] function, I display the [PHP] source code as part of the [HTML] an [HTML comment].

The [CSS] is just for design so the page has at least some aesthetic appeal. From a designer's perspective, it is not too pertinent to the actual _challenge_... but it's part of the code so I'll show it here. It's considered "bad practice" to include [CSS] inside the same file as your [HTML] when you create a real website, but I just leave it in for rapid development. (And it's a CTF challenge, so who cares)

```
<!--
<?
    
    $pattern = "/quick/i";
    $replace = "slow";
    $text = "The quick brown fox jumped over the lazy dog.";

    if ( 
        isset($_POST['pattern'])  &&
        isset($_POST['replace'])  &&
        isset($_POST['text'])
     ){

        $pattern = $_POST['pattern'];
        $replace = $_POST['replace'];
        $text = $_POST['text'];
        $replaced = preg_replace($_POST['pattern'], $_POST['replace'], $_POST['text']);
    }
?>

-->


<!DOCTYPE html>
<html>
<head>
    <title> Irregular Expressions </title>
    <style>
    body, html{
        padding: 10px 0px;
        margin: 0px 0px;
        height: 97%;
        font-size: larger;
        
    }
    *{
        font-family: verdana;
    }
    #submit{
        font-size: large;
        width: 80%;
        opacity: .8;
        display: block;
        margin-left: auto;
        margin-right: auto;
        padding: 10px;
    }
    #submit:hover{
        opacity: 1;
        text-decoration: underline;
        cursor:pointer;
        
    }
    #content{
        border: 1px solid black;
        border-radius: 30px;
        box-shadow: 0px 0px 30px gray;
        height:90%;
        width:800px;
        background-color: lightgreen;

        margin-left: auto;
        margin-right: auto;
        padding: 30px;
        padding-bottom: 0px;
    }
    h1{
        color: white;
        text-shadow: 2px 2px gray;
        font-size: 64px;
        text-align: center; 
        margin-top: 0px;
        width: 100%;
        border-bottom: 1px solid #333;
        margin-bottom: 50px;
    }
    input{
        width: 100%;
    }
    textarea{
        height: 100px;
        width: 100%;
    }
    p{
        font-weight: bold;
    }
    </style>

</head>
<body>

<div id="content">
<h1> Irregular Expressions</h1>

<form method="POST" action="">

<p>
    Pattern: <input type="text" name="pattern" placeholder="/quick/i" value=<?php if ( isset($pattern)) {echo('"'.$pattern.'"');} ?>> 
</p>

<p>
    Replace With: <input type="text" name="replace" placeholder="slow" value=<?php if ( isset($replace)) {echo('"'.$replace.'"');} ?>> 
</p>


<p>
    Original Text: <br> 
    <textarea name="text" placeholder="The quick brown fox jumped over the lazy dog."><?php if ( isset($text)) {echo($text);} ?></textarea>
</p>

<p>
    New Text: <br> 
    <textarea  disabled="disabled" name="new" placeholder=""><?php if ( isset($replaced)) {echo($replaced);} ?></textarea>
</p>

    <input id="submit" type="submit" value="Submit">

</form>
</div>
</body>
</html>
```

You can see in the [HTML form][form] I include some inline [PHP], just to display the variables set previously. And really that is all it is!

The Flag File
--------

Since the challenge will take advantage of [RCE], the real goal is to find the flag file on the remote host. So, we have to have a flag file! I just create one and call it `flag.txt` in the same directory.

The Docker Container
-------------

Since the exploit to this challenge requires running code on the host system, I don't want that on my real, actual box. That's why I put it in a [Docker] container, so the user is just stuck in a jail.

Here's the full command:

```
docker run -p 5555:80 -v `pwd`:/var/www/html/ -d eboraas/apache-php
```

I'll break it down by argument for you.

* `docker run` 
    ... this is the basic command, just telling [Docker] to startup.
*  `-p 5555:80` 
    ... this maps a port from the host machine to the [Docker] container. In this case, accessing the port `5555` on the host machine will bring you to port `80` on the [Docker] container... right to our [Apache][Apache] [web server]!
* `-v ``pwd``:/var/www/html`
    ... this maps a "volume" or some path on the host to a path to the [Docker] container. So what I do here is a map the current directory we are in (the output of the `pwd` command, I'm just using [`bash`][bash] [command substitution] here) to the root directory of the [Apache] web server. That will automatically put the `index.php` source code on the server and make it accessible... along with the `flag.txt` file!
* `-d`
    ... this means that [Docker] will run as a daemon, it will stay running in the background.
* `eboraas/apache-php`
    ... this is the [Docker] container image that we actually use. It's just a pre-built [Apache] webserver with an old, vulnerable version of [PHP] on it.

All it takes is running that command. That should start the server on the port you supply to be mapped to [Docker]'s web server, in this case `5555`. Just supply the host [IP address] and that port number, and then the user can play that challenge!

[RCE]: 
[Docker]: 
[PHP]:
[web server]: 
[regular expressions]: 
[preg_replace]: 
[HTML]:
[CSS]:
[HTTP]: 
[POST]: 
[form]: 
[HTML comment]: 
[Apache]: 
[bash]: 
[command substitution]: 
[daemon]: 
[IP address]: 