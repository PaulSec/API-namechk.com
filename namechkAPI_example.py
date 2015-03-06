from namechkAPI import NamechkAPI

# verbose mode
res = NamechkAPI({'verbose': True}).search(['stevewoz'])
print res  # retrieves the results
