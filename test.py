
def some():
    global x
    x = 100

if __name__ == '__main__':
    some()
    print(x)