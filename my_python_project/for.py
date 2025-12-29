#
length = 3
iter = (x for x in range(length))
for i in iter:
    print(i)


while 1:
    try:
        print(next(iter))
    except StopIteration:
        break
# cấu trúc vòng lặp for
for variable_1, variable_2 in [(1, 2), (3, 4), (5, 6)]:
    print(variable_1, variable_2)


iter1 = (x for x in range(3))
for i in iter1:
    print(i)

iter2 = {"name": "Tuyen", "age": 36}
for key, value in iter2.items():
    print(key, value)
    if key == "name":
        break


s = "How Tuyen"
for key in s:
    if key == " ":
        break
    else:
        print(key)


# if thì else, for của python cũng có else
for k in (1, 2, 3):
    print(k)
else:
    print("Done")
# break trong trường hợp ni cũng thoát hoàn toàn vòng lặp ko nhảy xuống else đâu
# continue thì vẫn như cũ, bỏ qua vòng lặp và tới tiếp theo

tong = 0

set_ = {5, 8, 1, 9, 4}
for i in set_:
    tong = tong + i
print(tong)
