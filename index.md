## cert_tree

cert_tree.py --help                                                                                 [9:49:26]
usage: cert_tree.py [-h] [-p] [-e] [-r] cert_file

View tree of certificates from pem file

positional arguments:
  cert_file             the cert file in pem format

optional arguments:
  -h, --help            show this help message and exit
  -p, --position        show position of cert in file
  -e, --expiry          show expiry date
  -r, --remove_expired  remove expired certs and output the good ones to stderr
