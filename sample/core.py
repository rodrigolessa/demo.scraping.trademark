# create a concatenated string from 0 to 19 (e.g. "012..1819")
# nums = [str(n) for n in range(20)]
# print "".join(nums)
# much more efficient then: nums += str(n)
# Best
# nums = map(str, range(20))
# print "".join(nums)