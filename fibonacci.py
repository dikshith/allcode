print("#generator - fibonacci")
def fibon(n):
    a=b=1
    result =[]
    for i in range(n):
        result.append(a)
        a,b = b,a+b
    return result

for x in fibon(10):
    print (x)
print("###############################")

print("# Map understanding --- Most of the times we use lambdas with map")
items = [1,2,3,4,5]
squared = list(map(lambda x:x**2, items))
print(squared)
print("###############################")

# Map Undersatnding - we can even have a list of functions!
def multiply(x):
    return (x*x)

def add(x):
    return (x+x)

print("# Map Undersatnding - we can even have a list of functions!")
funcs = [multiply, add]
for i in range(5):
    value = list(map(lambda x:x(i),funcs))
    print(value)
print("###############################")

print("# 'Filter' creates a list of elements for which a function returns true")
number_list = range(-5, 5)
less_than_zero = list(filter(lambda x: x < 0, number_list))
print(less_than_zero)
print("###############################")

print("Compute the product of a list of integers")
from functools import reduce
product = reduce((lambda x, y: x * y), [1, 2, 3, 4])
print(product)
print("###############################")

print("Sets behave mostly like 'lists' with the distinction that they can not contain duplicate values.")
some_list = ['a', 'a','b', 'c', 'b', 'd', 'm', 'n', 'n']
duplicates = []
for value in some_list:
    if some_list.count(value) > 1:
        if value not in duplicates:
            duplicates.append(value)
print(duplicates)
print("###############################")

print("More Elegant way - Sets behave mostly like 'lists' with the distinction that they can not contain duplicate values.")
some_list1 = ['a', 'a','b', 'c', 'b', 'd', 'm', 'n', 'n']
duplicates1 = set([x for x in some_list1 if some_list1.count(x) > 1])
print(duplicates1)
print("###############################")

print("In Python we can define functions inside other functions:")

def hi(name="dixit"):
    print("now you are inside the hi() function")

    def greet():
        return "now you are in the greet() function"

    def welcome():
        return "now you are in the welcome() function"

    print(greet())
    print(welcome())
    print("now you are back in the hi() function")

hi()
print("###############################")

print("Just take a look at the code again. In the if/else clause we are returning greet and welcome, not greet() and welcome()."
"Why is that? It’s because when you put a pair of parentheses after it, the function gets executed; whereas if you don’t put parenthesis after it,"
"then it can be passed around and can be assigned to other variables without executing it")

def hi(name="dixit"):
    def greet():
        return "now you are in the greet() function"
    def welcome():
        return "now you are in the welcome() function"
    if name == "dixit":
        return greet
    else:
        return welcome

a = hi()
print(a)
#outputs: <function greet at 0x7f2143c01500>#This clearly shows that `a` now points to the greet() function in hi()
#Now try this - #outputs: now you are in the greet() function
print(a())

b= hi(name = "ddd")
print (b())
print("###############################")

def hi():
    return "Hello Dixit, how are you today?"

def doSomethingBeforeHi(func):
    print("I am doing something before executing hi() function")
    print(func())

#outputs:I am doing some boring work before executing hi()
doSomethingBeforeHi(hi)


a = [(1, 2), (4, 1), (9, 10), (13, -3)]
a.sort(key=lambda x: x[1])
print(a)

list1 = [1666,4,5,6,7]
list2 = [1999,4,5,6,7]
data = zip(list1, list2)
data = sorted(data)
list1, list2 = map(lambda t: list(t), zip(*data))
print (list1,list2)