#! /usr/bin/env python3

'''
Testing Hexadecimal Functions
'''

lis = ['G', '0', '2', '7', '5', 'E']

newList = [int(i) if i.isdigit() else i for i in lis]

print(newList)

test = {'a': 10, 'b': 11, 'c': 12}
print(test['a'])
