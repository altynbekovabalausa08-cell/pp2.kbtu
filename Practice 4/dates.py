#1 Get and print the current date and time
import datetime
x = datetime.datetime.now()
print(x)

#2 Get the current year and the weekday name
import datetime
x = datetime.datetime.now()
print(x.year)
print(x.strftime("%A"))

#3 Create a specific date (May 17, 2020) and print it
import datetime
x = datetime.datetime(2020, 5, 17)
print(x)

#4 Create a specific date and print the month name
import datetime
x = datetime.datetime(2018, 6, 1)
print(x.strftime("%B"))

# Remove microseconds from the current datetime and print both versions
from datetime import datetime

now = datetime.now()
without_microseconds = now.replace(microsecond=0)

print("Original:", now)
print("Without microseconds:", without_microseconds)
