How to Build "1-800-RSA-TODAY"
=============

> John Hammond | July 21st, 2017

This is an easy [RSA][RSA] [crypto] challenge that is just masked with some [steganography] and different forms of showcasing the public key.


The Python Code
--------

Since [RSA] and all of [crypto] is just math, first we need some numbers to create the problem. I generate them with [Python] and verify the process so I know it is solvable.

```
 #!/usr/bin/env python
from Crypto.Util.number import getPrime, inverse
import binascii
import primefac


# bits_size = 120
#p = getPrime( bits_size )
p = 946421015452883684723415620863146079
#q = getPrime( bits_size )
q = 976909800304051809596219231346902083


m = 'USCGA{simple_rsa?_no_way!}'
m = binascii.hexlify(m)
m = int(m, 16)


e = 0x5
n = p * q

print n
# 924567965209634532254755658464904896482793754502887580214208881738382557


c = pow( m, e, n )
# 365068620041516010157210156097494426506821692593301308184474613958872524
print c

phi = ( q - 1 ) * ( p - 1 )

d = inverse( e, phi )

m = pow( c, d, n )
print repr(binascii.unhexlify(hex(m)[2:-1]))
```

This doubles as the "build" script as well as the "get flag" script. You can see I've commented out some of the sections that would actually generate a number, because I've just found one that works well and I have decided to keep it. 

It just runs through all of the math for [RSA], which I won't go into the details in here. The only valuable things pertinent to the creation of this challenge are `n`, `e`, and `c`.

The ASN1 File
----------

So with this challenge I wanted to include the public file in a special way, by using the `public_key.pem` file, looking like a certificate. The way to build this is a little messy, and honestly it includes some stuff I don't know much about.

Here is the file you need. I saved it with filename `def.asn1`.

```
# Start with a SEQUENCE
asn1=SEQUENCE:pubkeyinfo

# pubkeyinfo contains an algorithm identifier and the public key wrapped
# in a BIT STRING
[pubkeyinfo]
algorithm=SEQUENCE:rsa_alg
pubkey=BITWRAP,SEQUENCE:rsapubkey

# algorithm ID for RSA is just an OID and a NULL
[rsa_alg]
algorithm=OID:rsaEncryption
parameter=NULL

# Actual public key: modulus and exponent
[rsapubkey]
n=INTEGER:0x85f621bfcc0deeb7693600d552426bba78dc490d8661f417aa46b0affcdd

e=INTEGER:0x5
```

You can see the important values here are the `n` and `e` values, which are the same numbers we had in the build script, but just in [hexadecimal]. 

This acts the skeleton or template for building the public kery certificate. We can do the rest with this script:

```
#!/bin/bash

openssl asn1parse -genconf def.asn1 -out pubkey.der -noout
openssl rsa -in pubkey.der -inform der -pubin -out pubkey.pem
```

Note the important input file here: `def.asn1`. 

This will generate the `pubkey.der` and `pubkey.pem`  file. The `.pem` file is the actual certificate you want.




[RSA]: 
[crypto]: 
[steganography]: 
[hexadecimal]: