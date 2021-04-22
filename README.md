# cert_tree
Simple script to view a couple of x509 certificates stored in a single PEM file as a tree. It also enables viewing expiry date and purging expired certificates.

### Example:
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
    
cert_tree.py -pr ./certs/ca_list.pem 1>/dev/null 2>ca_list_new.pem 

$ cert_tree.py -pe ca_list_new.pem  
━ CorpRoot           [1] [valid until: 2040-05-05 18:19:20]
    ┣━ ServerCA      [2] [valid until: 2025-05-29 19:51:12]
    ┣━ example_cert  [3] [valid until: 2025-06-15 00:07:55]
    ┗━ example_2     [4] [valid until: 2025-06-04 14:56:07]
━ RootCert           [5] [valid until: 2029-04-28 14:53:22]
    ┣━ other         [6] [valid until: 2022-09-05 21:32:11]
    ┗━ AnotherOne    [7] [valid until: 2023-10-06 15:30:47]
    
cert_tree.py -pe ~/.certs/mycert.pem
━ RootCert                [3] [valid until: 2031-07-08 17:57:15]
    ┗━ IntermediateCert   [2] [valid until: 2023-07-08 18:55:58]
        ┗━ UserCert       [1] [valid until: 2023-09-17 13:33:00]
        
cert_tree.py ~/.certs/myothercert.pem
━ ClientCA (NOT PRESENT IN THIS PEM FILE)
    ┗━ UserCert
━ RootCert
    ┗━ IntermediateCert
━ OtherCert
```
