#!/usr/bin/env python3

__author__  = "Jacek Kolezynski"
__version__ = "0.0.3"

import argparse
from datetime import datetime, timedelta
import math
import re
import subprocess
import sys


class Cert:
    def __init__(self, subject, issuer, content, expiry=None, position = 0, missing=False):
        self.subject = subject
        self.issuer = issuer
        self.content = content
        self.expiry = expiry
        self.children = []
        self.position = position
        self.missing = missing
    
    def add_child(self, child):
        self.children.append(child)
        

def extract_certs_as_strings(cert_file):
    certs = []
    with open(cert_file) as whole_cert:
        cert_started = False
        content = ''
        for line in whole_cert:
            if '-----BEGIN CERTIFICATE-----' in line:
                if not cert_started:
                    content += line
                    cert_started = True
                else:
                    print('Error, start cert found but already started')
                    sys.exit(1)
            elif '-----END CERTIFICATE-----' in line:
                if cert_started:
                    content += line
                    certs.append(content)
                    content = ''
                    cert_started = False
                else:
                    print('Error, cert end found without start')
                    sys.exit(1)
            elif cert_started:
                    content += line
        
        if cert_started:
            print('The file is corrupted')
            sys.exit(1)

    return certs


def create_certs(certs_contents):
    certs = []
    position = 1
    for content in certs_contents:
        certs.append(create_cert(content, position))
        position += 1
    return certs

def create_cert(cert_content, position):
    proc = subprocess.Popen(['openssl', 'x509', '-text'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = proc.communicate(cert_content.encode())

    subject = ''
    issuer = ''
    date = None
    for line in out.decode().split('\n'):
        match = re.match("^\s*(\w*): .*CN ?= ?(.*)$", line)
        if match:
            if match.group(1) == 'Subject':
                subject = match.group(2)
            elif match.group(1) == 'Issuer':
                issuer = match.group(2)
        else:
            m = re.match("^\s*Not After\s?: (?P<date>.*)GMT$", line)
            if m:
                date = datetime.strptime(m.group(1).strip(), '%b %d %H:%M:%S %Y')

    return Cert(subject, issuer, cert_content, expiry=date, position=position)


def construct_tree(certs):
    roots_dir = {} # stores only root certs here
    issuers_dir = {c.subject : c for c in certs} 
    for c in certs:
        if c.subject in roots_dir:
            c = roots_dir[c.subject]
            # this is not self-signed cert, but was added temporarily to roots by other cert as missing parent
            c.missing = False
            del roots_dir[c.subject]   
        
        if c.subject == c.issuer:
            # this is self-signed cert, lets add it to roots
            roots_dir[c.issuer] = c
        else:
            # not self-signed cert
            if c.issuer in roots_dir:
                roots_dir[c.issuer].add_child(c)
            elif c.issuer in issuers_dir:
                issuers_dir[c.issuer].add_child(c)
            else:
                # this is not self signed cert, and has no parent in roots yet
                # so let's create temporary root and add it to roots
                missing_root = Cert(c.issuer, 'Unknown issuer', '', missing=True)
                roots_dir[c.issuer] = missing_root
                missing_root.add_child(c)

    return [r for r in roots_dir.values()]

def print_roots_content(roots):
    for root in roots:        
        print_cert_content(root)


def print_cert_content(root):
    now = datetime.now()
    if not root.missing and root.expiry and now < root.expiry:
        print(root.content, end='', file=sys.stderr)
    for c in root.children:
        print_cert_content(c)


def print_cert_roots(roots, position, expiry):
    printable_elements = [[],[]]
    for root in roots:
        generate_tree_elements_to_print(root, 0, printable_elements, position=position, expiry=expiry)

    max_first = 0
    for e in printable_elements[0]:
        max_first = max(max_first, len(e))
    
    for e1, e2 in zip(printable_elements[0], printable_elements[1]):
        spaces = max_first - len(e1) 
        tabs = ' '*spaces
        print(e1, tabs, e2)


def generate_tree_elements_to_print(root, level, printable_elements, spaces_for_level = 4, last = False, position = False, expiry = False):
    prefix_spaces = level * spaces_for_level
    prefix = ' '*prefix_spaces
    if level == 0:
        prefix += '\u2501'
    else:
        if last:
            prefix += '\u2517\u2501'
        else:
            prefix += '\u2523\u2501'
    
  
    postfix = f'[{root.position}]' if position and not root.missing else '' 

    postfix2 = ''
    if root.expiry:
        now = datetime.now()
        # now = datetime(2023,8,19)
        if now > root.expiry:
            postfix2 = f'[EXPIRED on: {root.expiry}]'
        elif now + timedelta(days=30) > root.expiry:
            postfix2 = f'[going to expire on: {root.expiry}]'
        elif expiry:
            postfix2 = f'[valid until: {root.expiry}]'
    
    postfixes = postfix + ' ' + postfix2
    
    printable_elements[1].append(postfixes)
   
    presence = ' (NOT PRESENT IN THIS PEM FILE)' if root.missing else ''
    printable_elements[0].append(f'{prefix} {root.subject.strip()}{presence}')
    for i,child in enumerate(root.children):
        last = False if i < len(root.children) - 1 else True
        generate_tree_elements_to_print(child, level + 1, printable_elements, last=last, position=position, expiry=expiry)

def main():
    parser = argparse.ArgumentParser(description='View tree of certificates from pem file')
    parser.add_argument('cert_file', help='the cert file in pem format')
    parser.add_argument('-p', '--position', action='store_true', help="show position of cert in file")
    parser.add_argument('-e', '--expiry', action='store_true', help="show expiry date")
    parser.add_argument('-r', '--remove_expired', action='store_true', help="remove expired certs and output the good ones to stderr")

    args = parser.parse_args()
    cert_file = args.cert_file
    if not cert_file.endswith('pem'):
        print('The cert must be in pem format')
        sys.exit(1)
        # TODO what about trying to convert from cer or der?

    certs = extract_certs_as_strings(cert_file)
    if not certs:
        print('No certs found in the pem file')
        return

    certs = create_certs(certs)
    roots = construct_tree(certs)
    print_cert_roots(roots, args.position, args.expiry)
    if args.remove_expired:
        print_roots_content(roots)

if __name__ == '__main__':
    main()