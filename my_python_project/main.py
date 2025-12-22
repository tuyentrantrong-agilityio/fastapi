def main():
    print("Hello from my-python-project!")


if __name__ == "__main__":
    main()
# commment in

print(" my name is")
for i in range(5):
    print(" tuyen five times" + str(i))

a = not True
if a:
    print(" a is true")

42 == 42
spam = 0
while spam < 5:
    print("i learn python " + str(spam))
    spam += 1

chuoi = "hello worldthis is \na long stringthat spans multiple lines"
result = chuoi * 5
print(result)

test = "abcdef"
print(len(test))

from turtle import penup, pendown, forward


def jump(lenght):
    """Move forward length units without leaving a trail.

    Postcondition: Leaves the pen down.
    """
    penup()
    forward(lenght)
    pendown()


import random

random.randint(1, 46)


def team(text, age):
    print(text)
    print(age)


team("hello", 86)
team("world", 96)
team("at", 36)
team("vietnam", "fgsdfg")


def team(text, age=0, success=False):
    print(text)
    print(age)
    print(success)


team("paramater defualt", 861)


def kteam(name, member):
    print(name)
    print(member)


a = "how method of string concatenation works"
# b = a.capitalize()
# b = a.upper()
# b = a.lower()
# b = a.swapcase()
b = a.title()
b = a.center(50,'-')
b = a.ljust(50,'-')
b = a.rjust(50,'-')
c = 'có gì hót'
d = c.encode('utf-8')
e = c.join(['a', 'b', 'c','d'])
d = a.strip() # xóa hết khoảng trắng giống strim của dart
print(e)
