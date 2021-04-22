# cert_tree
Simple script to view a couple of x509 certificates stored in a single PEM file as a tree. It also enables viewing expiry date and purging the expired certificates.

### Example
```
cert_tree.py -p ./certs/ca_list.pem  
━ CorpRoot            [1]
    ┣━ ServerCA       [2]
    ┣━ example_cert   [3]
    ┗━ example_2      [8]
━ RootCert            [4]
    ┣━ example_cert3  [5] [EXPIRED on: 2019-06-03 13:26:21]
    ┣━ other          [6]
    ┣━ other1         [7] [EXPIRED on: 2017-06-16 21:12:18]
    ┗━ AnotherOne     [9]
```
