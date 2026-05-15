# Python 基础

## 一、Python 语言介绍及基本使用
### Python 背景介绍
- 1989 年，Guido（龟叔）为 ABC 语言写插件，因喜爱 Monty Python 喜剧团体，故命名为 Python。
- 1990 年，发布 Python 第一个版本。
- 2001 年，发布 Python 2.0 版本。
- 2010 年，获年度 Tiobe 编程语言大奖。

### 注释
- **单行注释**：用 `#`，例：`# print("123")`，快捷键 `Ctrl+/` 可为多行加单行注释。
- **多行注释**：用 `'''` 或 `"""`，例：
  ```python
  '''
  醉卧沙场君莫笑，
  古来征战几人回。
  '''
  """
  a=d=12
  c=4
  print(a+d)
  """
  ```

### 标识符
- **概念**：编程时用于命名变量、常量、函数等，建立名称与使用关系。
- **命名规则**：
  - 由字母、数字和下划线组成，如 `num1=123`、`name='小明'`。
  - 不能含特殊字符（下划线除外），如 `A%$` 会报错。
  - 不能以数字或空格开头，如 `1abc` 会报错。
  - 不能是 Python 关键字，如 `while`、`for` 等。
- **命名规范**：
  - 见名知意，用简单英文单词。
  - Python 官方推荐变量名、函数名和文件名全小写，用下划线连接，如 `stu_name`。
  - 驼峰命名法：小驼峰用于变量或函数（如 `stuName`），大驼峰用于类（如 `StuName`）。

### 关键字
- **概念**：具特殊功能的标识符，被 Python 官方使用并定义，开发者不能定义与之重名的标识符。
- **常用关键字**：
  - `False`、`None`、`True`、`and`、`as`、`assert`、`break`、`class`、`continue`、`def`、`del`、`elif`、`else`、`except`、`finally`、`for`、`from`、`global`、`if`、`import`、`in`、`is`、`lambda`、`nonlocal`、`not`、`or`、`pass`、`raise`、`return`、`try`、`while`、`with`、`yield`。

## 二、变量与常用数据类型以及输入输出

### 数据类型
- **数字型**：`int`（整型）、`float`（浮点型）、`complex`（复数）。
- **布尔型**：`bool`，值为 `True` 或 `False`，`True` 可当 1 使用，`False` 可当 0 使用。
- **字符串型**：`str`。
- **列表**：`list`。
- **元组**：`tuple`。
- **字典**：`dict`。
- **集合**：`set`。
- **字节**：`bytes`。
- **空值**：`NoneType`，只有值 `None`。

### 变量
- **概念**：用户自定义的可变化标识符。
- **语法**：`变量名 = 值`。
- **定义方式**：
  ```python
  # 变量定义一般不声明类型
  num1 = 123  # 整型 int
  name = '小明'  # 字符串 str
  num = 12.3  # 浮点 float
  b1 = True  # 布尔型
  # 声明类型
  num1: int = 123
  # 多个定义
  a1 = a2 = a3 = 123
  b1, b2, b3 = 1, 2, 3
  ```
- **使用**：
  - **二次赋值**：
    ```python
    num1 = 123
    print(num1)
    num1 = 321
    print(num1)
    ```
  - **获取内存地址**：`id(x)` 获取变量 x 在内存中的地址。
    ```python
    print(id(1))
    n = 1
    print(id(n))
    ```
  - **获取数据类型**：`type(x)` 获取变量 x 的数据类型。
    ```python
    num1 = 123
    name = '小明'
    a1 = True
    print(num1, type(num1))
    print(name, type(name))
    print(a1, type(a1))
    ```
  - **变量交换**：
    - 方法一：用空容器。
      ```python
      a = 10
      b = 20
      temp = a
      a = b
      b = temp
      print(a, b)
      ```
    - 方法二：直接交换。
      ```python
      num1 = 123
      name = '小明'
      print('Num1:', num1)
      print('name:', name)
      num1, name = name, num1
      print('Num1:', num1)
      print('name:', name)
      ```
  - **类型转换**：
    - `int(x)`：将 x 转换为整型。
    - `float(x)`：将 x 转换为浮点型。
    - `str(x)`：将 x 转换为字符串。
    - `bool(x)`：将 x 转换为布尔型。
    ```python
    a = '123'
    print(a, type(int(a)))
    b = '12.39'
    print(b, type(float(b)))
    c = 123
    print(c, type(str(c)))
    a = 1
    print(a, type(bool(a)))
    ```
  - **扩展**：`pack` 和 `unpack`（打包和拆包）。
    - **拆包**：
      ```python
      a1, a2, *a3 = 1, 2, 3, 4, 5, 6
      print(a1)  # 1
      print(a2)  # 2
      print(a3)  # [3, 4, 5, 6]
      ```
      注意：`*` 变量不能在第一个位置，否则报错。
    - **打包**：
      ```python
      def test(*num):
          print(num)  # (345, 6, 7, 7, 8, 8, 914, 6, 75, 7)
      test(345, 6, 7, 7, 8, 8, 914, 6, 75, 7)
      ```

### 输入输出
- **输入**：`input()`，从控制台获取数据，输入数据为字符串类型。
  ```python
  g = input('请输入数字：')
  print('你输入的是：', g)
  ```
- **输出**：`print()`，将数据输出到控制台。
  ```python
  print('输出内容')
  ```

## 三、格式化输出 & 常用运算符

### 格式化输出
- **占位符**：
  - `%d`：匹配整型。
  - `%f`：匹配浮点型。
  - `%s`：匹配任意类型。
  ```python
  a1, a2 = 18, 32.2123
  print('输出数值：%d' % (a2))  # 输出数值：32
  print('输出数值：%f' % (a2))  # 输出数值：32.212300
  print('输出数值：%s' % (a2))  # 输出数值：32.2123
  print('输出数值：%s' % (a1))  # 输出数值：十八
  ```
- **`f-string`**：`f"xxxx"`，`f` 表示 format。
  ```python
  name = "小明"
  age = 18
  print("用户名：{name}, 年龄：{age}")  # 用户名：{name}, 年龄：{age}
  print(f"用户名：{name}, 年龄：{age}")
  print(f"{8}:{40}:{30}")
  ```

### 运算符和表达式

#### 算术运算符
| 运算符 | 说明           |
| :----- | :------------- |
| `+`    | 加             |
| `-`    | 减             |
| `*`    | 乘             |
| `/`    | 除             |
| `//`   | 取整           |
| `%`    | 求余（取模）   |
| `**`   | 求幂（求次方） |

```python
a = 5
b = 3
print(a + b)  # 8
print(a - b)  # 2
print(a * b)  # 15
print(a / b)  # 1.6666666666666667
print(a // b)  # 1
print(a % b)   # 2
print(a ** b)  # 125
```

#### 赋值运算符
| 运算符                            | 说明           |
| :-------------------------------- | :------------- |
| `=`                               | 简单赋值运算符 |
| `+=、-=、*=、/=、%=、//=、**=` 等 | 复合赋值运算符 |

```python
num = 10
num = 66
b = 10
b += 5  # 等价于 b = b + 5
print(b)  # 15
c = 5
c /= 3
print(c)  # 1.6666666666666667
```

#### 关系运算符
| 运算符 | 说明     |
| :----- | :------- |
| `==`   | 相等     |
| `!=`   | 不相等   |
| `>`    | 大于     |
| `<`    | 小于     |
| `>=`   | 大于等于 |
| `<=`   | 小于等于 |

```python
a = 10
b = 5
print(a > b)   # True
print(a >= b)  # True
print(a < b)   # False
print(a <= b)  # False
print(a == b)  # False
print(a != b)  # True
```

#### 逻辑运算符
| 运算符 | 说明 |
| :----- | :--- |
| `and`  | 与   |
| `or`   | 或   |
| `not`  | 非   |

- **短路原则**：
  - `A and B`：若 A 为 False，则结果为 False，不计算 B。
  - `A or B`：若 A 为 True，则结果为 True，不计算 B。
  ```python
  print(True and True)   # True
  print(True and False)  # False
  print(False or True)   # True
  print(not False)       # True
  print(not 10)          # False
  print(not "")          # True
  print(not [34,56])     # False
  ```

#### 成员运算符
- `in`：判断值是否在序列中，返回布尔值。
- `not in`：判断值是否不在序列中，返回布尔值。

```python
print(1 in [1, 2, 3])  # True
print(4 not in [1, 2, 3])  # True
```

#### 身份运算符
- `is`：判断两标识符是否引用同一对象。
- `is not`：判断两标识符是否引用不同对象。

```python
a = [1, 2, 3]
b = a
print(a is b)  # True
print(a is not b)  # False
```

#### 运算符优先级
运算符优先级从高到低：
1. `**`
2. `~ + -`（单目运算符）
3. `* / // %`
4. `+ -`（双目运算符）
5. `>> <<`
6. `&`
7. `^ |`
8. `<= < > >=`
9. `== !=`
10. `= %= /= //= -= += *= **=`
11. `is is not`
12. `in not in`
13. `not`
14. `and`
15. `or`

## 四、if 判断语句

### 单分支
```python
if 表达式：
    语句
```
```python
a = True
if a:
    print('输出成功1')
```

### 双分支
```python
if 表达式：
    语句1
else：
    语句2
```
```python
a = False
if a:
    print('输出成功1')
else:
    print('输出失败')
```

### 多分支
```python
if 表达式1：
    语句1
elif 表达式2：
    语句2
elif 表达式3：
    语句3
...
elif 表达式n：
    语句n
else：
    语句m
```
```python
age = int(input('输入年龄：'))
if age < 6:
    print('孩子在幼儿园')
elif 6 <= age < 22:
    student_status = input('是否在校：')
    if student_status == '是':
        print('学生')
    else:
        print('打工')
elif 22 <= age < 50:
    work_type = input('工作类型是蓝领（1）, 白领（2）：')
    if work_type == '1':
        print('工人')
    elif work_type == '2':
        print('销售')
```

### 三目表达式
```python
r = 值1 if 条件 else 值2
```
```python
b = '是' if a >= 18 else '不是'
print(b)
```

## 五、循环语句

### while 循环
```python
while 表达式：
    语句
```
```python
a = 0
while a < 5:
    print(a)
    a += 1
print('最终结果为：', a)
```

### for 循环
```python
for 变量名 in 序列：
    语句
```
```python
a = [1, 2, 3, 4]
for i in a:
    print(i)
```

### 嵌套循环
```python
while 表达式1：
    while 表达式2：
        语句
```
注意缩进和执行顺序。

### break 和 continue
- `break`：结束当前循环。
- `continue`：结束本次循环，继续下一次。
```python
# break 示例
c2 = 0
while True:
    if c2 == 5:
        break
    c2 += 1
    print(c2)
# continue 示例
for i in range(5):
    if i % 2 == 0:
        continue
    print(i)
```

### else 语句
循环语句可附带 `else`，若循环未被 `break` 结束，则执行 `else`。
```python
for i in range(3):
    print(i)
else:
    print(i)
```

## 六、随机数
Python 生成随机数常用 `random` 模块。

### 导入模块
- 直接导入：`import random`
- 导入并重命名：`import random as ran`
- 导入指定方法：`from random import randint`
- 导入所有方法：`from random import *`

### 常用方法
```python
import random
a = [123, 1, 2, 3, 321, 456, 654, 789, 987]
# choice()：随机选择元素
n1 = random.choice(a)
print(n1)
# randint(a, b)：生成 [a, b] 的随机整数
n2 = random.randint(12, 56)
print(n2)
# randrange()：生成随机数，可指定步长
n3 = random.randrange(1, 56, 2)
print(n3)
# sample()：从序列中随机选取指定数量元素
n4 = random.sample(a, 3)
print(n4)
# random()：生成 [0, 1) 的随机浮点数
n5 = random.random()
print(n5)
# uniform(a, b)：生成 [a, b] 的随机浮点数
n6 = random.uniform(12, 36)
print(n6)
```

## 七、列表

### 增
```python
n1 = [1, 2, 3]
# append()：末尾增加
n1.append(321)
print('列表 n1:', n1)
# extend()：将可迭代对象元素添加到末尾
n1.extend('abc')
print('列表 n1:', n1)
# insert()：按索引插入元素
n1.insert(3, '雾山五行')
print('列表 n1:', n1)
```

### 删
```python
n1 = [1, 2, 3]
# remove()：移除指定元素
n1.remove(1)
print('列表 n1:', n1)
# pop()：弹出指定索引元素，默认弹出最后一个
n1.pop()
print('列表 n1:', n1)
# clear()：清空列表
n1.clear()
print('列表 n1:', n1)
```

### 改
```python
# reverse()：反转列表
n2 = [1, 2, 3]
n2.reverse()
print('列表 n2:', n2)
# sort()：排序
n3 = [3, 67, 1, 97, 34, 12]
n3.sort()
print('n3 默认升序:', n3)
n3.sort(reverse=True)
print('n3 降序:', n3)
```

### 查
```python
# len()：获取列表长度
print('n3 长度（个数）:', len(n3))
# count()：统计元素个数
print('数字 1 个数:', n3.count(1))
# max()/min()：求最大值和最小值
print('最小值:', min(n3))
print('最大值:', max(n3))
# index()：查找元素索引
n4 = [6, 2, 6, 1, 8, 4]
a = n4.index(4)
print(a)
```

### 遍历
- **`for` 遍历**：
  ```python
  numlist = [11, 22, 33, 44, 55]
  for n1 in numlist:
      print(n1)
  ```
- **`while` 遍历**：
  ```python
  i = 0
  while i < len(numlist):
      print(i, numlist[i])
      i += 1
  ```

### 二维数组（多维列表）
```python
list2 = [[1, 2], [4, 45, 56, 6], [34]]
# 访问元素
print(list2[0][1])  # 输出 2
# 遍历
for sublist in list2:
    for num in sublist:
        print(num)
```

### 切片
```python
numlist = [11, 22, 33, 44, 55, 66, 77, 88, 99]
# 语法：列表名[start:end:step]
print(numlist[2:5])  # [33, 44, 55]
print(numlist[:5])   # [11, 22, 33, 44, 55]
print(numlist[5:])   # [66, 77, 88, 99]
print(numlist[::2])  # [11, 33, 55, 77, 99]
print(numlist[::-1]) # [99, 88, 77, 66, 55, 44, 33, 22, 11]
```

## 八、简单算法

### 冒泡排序
```python
num = [72, 32, 70, 72, 22, 83, 13, 72, 92, 95]
print(num)
for i in range(len(num)):
    for j in range(len(num) - 1 - i):
        if num[j] < num[j + 1]:
            num[j], num[j + 1] = num[j + 1], num[j]
print(num)
```

### 选择排序
```python
num = [72, 32, 70, 72, 22, 83, 13, 72, 92, 95]
print("原始数组:", num)
for i in range(len(num)):
    min_index = i
    for j in range(i + 1, len(num)):
        if num[min_index] > num[j]:
            min_index = j
    if min_index != i:
        num[i], num[min_index] = num[min_index], num[i]
print("排序后的数组:", num)
```

### 顺序查找
```python
list1 = [34, 45, 6, 74, 45, 5, 6, 7, 10, 67]
key = 45
for i in range(len(list1)):
    if list1[i] == key:
        print(i)
```

### 二分法查找
```python
list1 = [34, 45, 6, 74, 45, 8, 6, 49, 12, 67]
list1.sort()
key = 100
left = 0
right = len(list1) - 1
while left <= right:
    middle = (left + right) // 2
    if key > list1[middle]:
        left = middle + 1
    elif key < list1[middle]:
        right = middle - 1
    else:
        print(f"待查找元素 {key} 在列表中的索引为：{middle}")
        break
else:
    print(f"{key} 在列表中不存在")
```

## 九、字典

### 定义
```python
# 一般格式
dict = {"name": "张三", "age": 20, "sex": "男"}
# 空字典
dict1 = {}
dict2 = dict()
print(dict)
print(dict1)
print(dict2)
```

### 键值的访问
```python
my_dict = {"name": "小红", "age": 20, "sex": "女"}
print(my_dict["age"])  # 访问值
my_dict['sex'] = '男'  # 修改值
```

### 基本操作
```python
dict = {"name": "张三", "age": 20, "sex": "男"}
# 增
dict['xuexiao'] = '河软'
print(dict['xuexiao'])
# 删
del dict["name"]
print(dict)
# 查
value = dict['age']
print(value)
# 改
dict['age'] = 40
print(dict)
```

### 遍历
```python
# 遍历键
for i in my_dict.keys():
    print(i)
# 遍历值
for i in my_dict.values():
    print(i)
# 遍历键值对
for i in my_dict.items():
    print(i)
# 依次打印键和值
for key, value in my_dict.items():
    print(key, value)
```

## 十、字符串

### 操作
```python
s1 = 'abc'
s2 = '123'
# 拼接
print(s1 + s2)
# 重复
print(s1 * 3)
# 判断是否存在
print('a' in s1)
print('a' not in s1)
# 遍历
data = 'hello'
for ch in data:
    print(ch)
```

### 基本功能

#### 转换
```python
s1 = '123'
r1 = eval(s1)
r2 = int(s1)
print(s1, type(s1))
print(r1, type(r1))
print(r2, type(r2))
```

#### 字母转换
```python
s1 = 'Hello world'
print(s1.upper())        # 全部大写
print(s1.lower())        # 全部小写
print(s1.swapcase())     # 大小写转换
print(s1.capitalize())   # 首字母大写
print(s1.title())        # 每个单词首字母大写
```

#### ASCII 码
```python
print(chr(97))    # 查找 97 对应字符
print(ord('A'))   # 查找 'A' 的 ASCII 码值
print(ord('0'))   # 查找 '0' 的 ASCII 码值
```

#### 查找
```python
s1 = 'Hello world'
print(s1.find('l'))   # 从左往右检索，返回索引，查找不到返回 -1
print(s1.index('0'))  # 从左往右检索，查找不到报错
```

#### 填充
```python
s1 = 'Hello world'
print(s1.center(20, '*'))  # 居中
print(s1.rjust(20, '*'))   # 右对齐
print(s1.ljust(20, '*'))   # 左对齐
```

#### 提取
```python
s1 = '***Hello world***'
print(s1.strip('*'))  # 去除两端指定字符
print(s1.lstrip('*')) # 去除左边指定字符
print(s1.rstrip('*')) # 去除右边指定字符
```

#### 合并和分割
```python
s1 = 'Hello world'
s2 = s1.split()       # 分割成列表
print(s2)
print(' '.join(s2))   # 用空格连接列表元素
```

#### 替换
```python
s1 = 'Hello world'
print(s1.replace('l', 'i'))  # 替换字符串中的字符
```

#### 判断
```python
s1 = 'Hello world'
print(s1.startswith('H'))  # 判断是否以指定字符串开头
print(s1.endswith('d'))    # 判断是否以指定字符串结尾
```

#### 格式化
```python
name = "小明"
age = 18
print(f"用户名：{name}, 年龄：{age}")
```

## 十一、函数

### 概述
函数是对特定功能的封装，优点包括简化代码结构、提高复用性和维护性。

### 定义
```python
def 函数名(参数列表):
    函数体
    return 返回值
```
示例：
```python
def test1():
    print('test~~~1111')

def test2(a, b, num1):
    print('test~~~222')

def test3():
    print('test~~~333')
    return 10

def test4(a, b, num1):
    print('test~~~4444')
    return 'abc'
```

### 调用
```python
def test1():
    test2()
    print('---test1---')

def test2():
    test3()
    print('---test2---')

def test3():
    print('---test3---')

test1()
```

### 参数
- **形参**：函数声明中的参数，用于接收实参值。
- **实参**：函数调用中的参数，用于给形参赋值。

### 返回值（`return`）
```python
def str1():
    return '123'
print(str1())  # 输出 '123'
```
注意：
- 未使用 `return` 时，函数默认返回 `None`。
- `return` 可单独使用，用于结束函数。
- `return` 可返回一个或多个值（返回多个值时，结果为元组）。

### 空函数和主函数
```python
# 空函数
def test():
    pass

# 主函数
def check():
    print("ok~~~~")

if __name__ == "__main__":
    check()
```

### 函数的封装
```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)  # 输出 8
```

### 匿名函数
```python
n1 = lambda x: x % 2 == 0
lst = [11, 2, 3, 44, 99, 8]
lst2 = filter(n1, lst)
lst2 = list(lst2)
print(f'偶数有 {lst2}')
```

## 十二、函数进阶

### 作用域
Python 作用域分为：
- **L（Local）**：局部作用域，函数内部。
- **E（Enclosing）**：闭包作用域，外部函数。
- **G（Global）**：全局作用域，模块级别。
- **B（Built-in）**：内置作用域，内置函数和变量。

### 局部变量和全局变量
- **全局变量**：在函数外定义，可在整个程序中访问。
- **局部变量**：在函数内定义，仅在函数内有效。

## 十三、高阶函数

### `map()`
```python
def square(x):
    return x ** 2

numbers = [1, 2, 3, 4, 5]
squared = map(square, numbers)
print(list(squared))  # [1, 4, 9, 16, 25]
```

### `filter()`
```python
def is_even(x):
    return x % 2 == 0

numbers = [1, 2, 3, 4, 5, 6]
evens = filter(is_even, numbers)
print(list(evens))  # [2, 4, 6]
```

### `sorted()`
```python
numbers = [5, 2, 9, 1, 5, 6]
sorted_numbers = sorted(numbers)
print(sorted_numbers)  # [1, 2, 5, 5, 6, 9]

# 自定义排序规则
def get_key(x):
    return -x

sorted_numbers_desc = sorted(numbers, key=get_key)
print(sorted_numbers_desc)  # [9, 6, 5, 5, 2, 1]
```

### `reduce()`
需要从 `functools` 模块导入。
```python
from functools import reduce

def add(x, y):
    return x + y

numbers = [1, 2, 3, 4, 5]
sum_result = reduce(add, numbers)
print(sum_result)  # 15
```

## 十四、装饰器和递归

### 装饰器概念：

概念：已知一个函数，如果需要给该函数增加新的功能，但是不希望修改原函数，在Python中，这种在代码运行期间动态执行的机制被称为装饰器【Decorator】

```
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 执行时间：{end_time - start_time} 秒")
        return result
    return wrapper

@timer
def example_function(n):
    sum = 0
    for i in range(n):
        sum += i
    return sum

result = example_function(1000000)
print(f"计算结果：{result}")
```

### 递归

递归是一种编程概念，指的是函数调用自身的现象。递归需要满足两个条件：

  1. 基准条件（Base Case）：也称为递归终止条件，这个条件用于结束递归调用，防止函数无限调用自身而陷入死循环。当达到基准条件时，递归过程会停止，函数开始逐层返回。
  2. 递归步骤（Recursive Step）：在这个步骤中，函数会调用自身，但每次调用时会将问题规模缩小，逐渐向基准条件靠近，直到满足基准条件而终止递归。

以下是一个递归计算阶乘的 Python 源码示例：

```python
def factorial(n):
    # 基准条件
    if n == 0 or n == 1:
        return 1
    # 递归步骤
    else:
        return n * factorial(n - 1)

# 测试
print(factorial(5))  # 输出 120
```

在这个例子中，计算 `n!` 的阶乘。当 `n` 等于 0 或 1 时，直接返回 1，这是递归的基准条件。对于其他 `n` 值，函数调用自身计算 `n * factorial(n - 1)`，每次调用都会将问题规模缩小（ `n` 减 1），直到达到基准条件，从而完成递归计算。

再比如，递归实现斐波那契数列：

```python
def fibonacci(n):
    # 基准条件
    if n <= 1:
        return n
    # 递归步骤
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

# 测试
for i in range(10):
    print(fibonacci(i), end=' ')  # 输出 0 1 1 2 3 5 8 13 21 34
```

这里计算第 `n` 个斐波那契数。当 `n` 小于等于 1 时，直接返回 `n` 作为基准条件。对于 `n` 大于 1 的情况，递归调用 `fibonacci(n - 1)` 和 `fibonacci(n - 2)` 来获取前面两个斐波那契数并相加，每次调用都缩小问题规模，直至满足基准条件

## 十五、面型对象基础

面向对象编程（OOP）是一种以对象为核心，通过对象之间的交互来实现程序功能的编程思想和方法。在面向对象编程中，对象是具有状态（属性）和行为（方法）的实体，而类则是用于创建对象的模板或蓝图。以下是面向对象编程中类和对象的基本概念：

### 1. 类（Class）

类是一个抽象的概念，它是对象的模板或蓝图，用于定义对象的属性（数据成员）和方法（成员函数）。类描述了对象的结构和行为，但本身并不是对象。

```python
class Car:
    # 类属性
    wheels = 4

    # 初始化方法（构造函数）
    def __init__(self, brand, color):
        self.brand = brand  # 实例属性
        self.color = color  # 实例属性

    # 实例方法
    def drive(self):
        print(f"The {self.color} {self.brand} is driving.")

    # 类方法
    @classmethod
    def get_wheels(cls):
        return cls.wheels
```

在这个例子中：
- `Car` 是一个类，它定义了汽车的属性（`brand` 和 `color`）和方法（`drive`）。
- `__init__` 是类的构造函数，用于初始化对象的属性。
- `drive` 是一个实例方法，它需要对象实例来调用。
- `wheels` 是一个类属性，属于类本身，所有实例共享。
- `get_wheels` 是一个类方法，通过 `@classmethod` 装饰器定义，可以通过类名直接调用。

### 2. 对象（Object）

对象是类的实例，它是类的具体体现。通过类创建对象后，对象就拥有了类定义的属性和方法。

```python
# 创建对象
my_car = Car("Toyota", "red")

# 访问对象的属性
print(my_car.brand)  # 输出 "Toyota"
print(my_car.color)  # 输出 "red"

# 调用对象的方法
my_car.drive()  # 输出 "The red Toyota is driving."

# 访问类属性
print(Car.wheels)  # 输出 4
print(my_car.wheels)  # 输出 4

# 调用类方法
print(Car.get_wheels())  # 输出 4
print(my_car.get_wheels())  # 输出 4
```

在这个例子中：
- `my_car` 是 `Car` 类的一个对象实例。
- 通过 `my_car.brand` 和 `my_car.color` 访问对象的属性。
- 通过 `my_car.drive()` 调用对象的方法。
- 通过 `Car.wheels` 或 `my_car.wheels` 访问类属性。
- 通过 `Car.get_wheels()` 或 `my_car.get_wheels()` 调用类方法。

### 3. 面向对象编程的核心概念

#### 3.1 封装（Encapsulation）

封装是将对象的属性和方法包装在一起，隐藏对象的内部实现细节，只暴露必要的接口给外界。通过封装可以保护对象的内部状态，防止外部直接访问或修改对象的属性。

```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # 私有属性

    def get_balance(self):
        return self.__balance

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            print(f"Deposited {amount}. New balance: {self.__balance}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            print(f"Withdrew {amount}. New balance: {self.__balance}")
        else:
            print("Invalid withdrawal amount or insufficient balance.")
```

在这个例子中：
- `__balance` 是一个私有属性，外部不能直接访问。
- 通过 `get_balance` 方法可以获取余额。
- 通过 `deposit` 和 `withdraw` 方法可以安全地操作余额。

#### 3.2 继承（Inheritance）

继承是一种允许新类（子类）继承现有类（父类）的属性和方法的机制。子类可以重用父类的代码，并且可以添加新的属性和方法或覆盖父类的方法。

```python
class Vehicle:
    def __init__(self, brand):
        self.brand = brand

    def start(self):
        print(f"The {self.brand} is starting.")

class Car(Vehicle):
    def __init__(self, brand, color):
        super().__init__(brand)
        self.color = color

    def drive(self):
        print(f"The {self.color} {self.brand} is driving.")

class Motorcycle(Vehicle):
    def __init__(self, brand, type):
        super().__init__(brand)
        self.type = type

    def ride(self):
        print(f"The {self.type} {self.brand} is being ridden.")

# 创建对象
my_car = Car("Toyota", "red")
my_motorcycle = Motorcycle("Honda", "cruiser")

my_car.start()    # 输出 "The Toyota is starting."
my_car.drive()    # 输出 "The red Toyota is driving."

my_motorcycle.start()  # 输出 "The Honda is starting."
my_motorcycle.ride()   # 输出 "The cruiser Honda is being ridden."
```

在这个例子中：
- `Car` 和 `Motorcycle` 是 `Vehicle` 的子类，继承了 `Vehicle` 的 `brand` 属性和 `start` 方法。
- 子类可以添加新的属性（如 `color` 和 `type`）和方法（如 `drive` 和 `ride`）。
- 使用 `super().__init__(brand)` 调用父类的构造函数。

#### 3.3 多态（Polymorphism）

多态是指允许不同类的对象对同一消息做出不同响应的能力。多态通常通过方法重写（Override）或接口实现来实现。

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Cow(Animal):
    def speak(self):
        return "Moo!"

# 多态示例
def animal_sound(animal):
    print(animal.speak())

# 创建对象
my_dog = Dog()
my_cat = Cat()
my_cow = Cow()

animal_sound(my_dog)  # 输出 "Woof!"
animal_sound(my_cat)  # 输出 "Meow!"
animal_sound(my_cow)  # 输出 "Moo!"
```

在这个例子中：
- `Animal` 是一个父类，定义了一个 `speak` 方法。
- `Dog`、`Cat` 和 `Cow` 是 `Animal` 的子类，分别重写了 `speak` 方法。
- `animal_sound` 函数可以接受任何 `Animal` 类型的对象，并调用其 `speak` 方法，展示了多态的特性。

### 总结

面向对象编程通过类和对象来组织代码，具有封装、继承和多态等核心特性。类是对象的模板，定义了对象的属性和方法；对象是类的实例，具有具体的属性值和行为。面向对象编程使得代码更模块化、可复用和可维护。

## 十六、单例模式

单例模式是一种常用的软件设计模式，其核心目的是确保一个类只有一个实例，并且提供一个全局访问点。单例模式可以用来管理共享资源，比如缓存、线程池、配置信息等。

### 单例模式的特点

  1. **唯一性** ：保证一个类只有一个实例。
  2. **全局访问性** ：提供一个全局访问点来获取该实例。

### 单例模式的实现方式

在 Python 中，有多种方式可以实现单例模式，以下是一些常见的实现方法。

#### 1. 基于类方法控制实例创建（推荐）

```python
class Singleton:
    _instance = None  # 用于保存实例的类属性

    def __new__(cls, *args, **kwargs):
        # 如果还没有创建实例，则创建一个实例
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        # 返回唯一的实例
        return cls._instance

    def __init__(self):
        self.value = None

# 测试
singleton1 = Singleton()
singleton1.value = "Singleton 1"
print(singleton1.value)  # 输出 "Singleton 1"

singleton2 = Singleton()
print(singleton2.value)  # 输出 "Singleton 1"

# singleton1 和 singleton2 是同一个对象
print(singleton1 is singleton2)  # 输出 True
```

**解释** ：

  * `_instance` 是类属性，用于保存创建的实例。初始时为 `None`。
  * `__new__` 方法是对象实例化时调用的特殊方法。在创建实例时，先检查 `_instance` 是否为 `None`，如果是，则调用 `super` 方法创建实例并保存到 `_instance` 中；如果不是，则直接返回 `_instance` 中的实例。
  * 这样就保证了无论调用多少次类名创建实例，都只会得到同一个实例。

#### 2. 基于装饰器实现

```python
def singleton(cls):
    instances = {}  # 用于保存类和其实例的字典

    def wrapper(*args, **kwargs):
        # 如果类还没有实例，则创建一个实例并保存到字典中
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        # 返回对应的实例
        return instances[cls]
    return wrapper

@singleton
class Singleton:
    def __init__(self):
        self.value = None

# 测试
singleton1 = Singleton()
singleton1.value = "Singleton 1"
print(singleton1.value)  # 输出 "Singleton 1"

singleton2 = Singleton()
print(singleton2.value)  # 输出 "Singleton 1"

# singleton1 和 singleton2 是同一个对象
print(singleton1 is singleton2)  # 输出 True
```

**解释** ：

  * `singleton` 是一个装饰器，它接收一个类作为参数。
  * 在装饰器内部，定义了一个 `wrapper` 函数，用于控制实例的创建。当装饰的类被实例化时，实际上是调用 `wrapper` 函数。
  * `wrapper` 函数通过检查 `instances` 字典中是否已经存在该类的实例来决定是创建新实例还是返回已存在的实例。

#### 3. 基于模块实现

在 Python 中，模块本身是天然的单例，因为 Python 的模块只被加载一次。可以利用这一点来实现单例模式：

```python
# singleton.py
class Singleton:
    def __init__(self):
        self.value = None

singleton = Singleton()  # 创建单例对象
```

在其他文件中使用：

```python
from singleton import singleton

singleton.value = "Singleton 1"
print(singleton.value)  # 输出 "Singleton 1"
```

**解释** ：

  * 将类的实例化过程放在模块中，由于模块只加载一次，所以该实例只会被创建一次。
  * 通过导入模块中的实例对象，就可以在不同地方使用同一个实例。

#### 4. 基于元类实现

```python
class SingletonMeta(type):
    _instances = {}  # 用于保存类和其实例的字典

    def __call__(cls, *args, **kwargs):
        # 如果类还没有实例，则创建一个实例并保存到字典中
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        # 返回对应的实例
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    def __init__(self):
        self.value = None

# 测试
singleton1 = Singleton()
singleton1.value = "Singleton 1"
print(singleton1.value)  # 输出 "Singleton 1"

singleton2 = Singleton()
print(singleton2.value)  # 输出 "Singleton 1"

# singleton1 和 singleton2 是同一个对象
print(singleton1 is singleton2)  # 输出 True
```

**解释** ：

  * `SingletonMeta` 是一个元类，它重写了 `__call__` 方法。`__call__` 方法在创建类实例时被调用。
  * 当通过 `Singleton` 类创建实例时，实际上是调用元类 `SingletonMeta` 的 `__call__` 方法。
  * 在 `__call__` 方法中，通过检查 `_instances` 字典来控制实例的创建，从而保证只有一个实例。

### 单例模式的适用场景

  1. **资源管理** ：当需要管理共享资源时，比如文件、数据库连接、线程池等，确保只有一个实例可以避免资源竞争和浪费。
  2. **配置管理** ：对于配置信息，通常希望在整个应用程序中只有一个配置实例，所有组件都使用同一个配置。
  3. **日志记录** ：日志记录器通常设计为单例，以便在应用程序的不同部分记录日志时，可以共享同一个日志配置和输出流。
  4. **缓存系统** ：缓存系统通常需要在整个应用程序中共享一个缓存实例，避免重复缓存和数据不一致的问题。

### 单例模式的优点

  1. **控制资源使用** ：通过确保只有一个实例，可以对共享资源进行统一管理和控制，避免资源浪费。
  2. **全局访问方便** ：提供一个全局访问点，方便不同部分的代码获取和使用同一个实例。
  3. **简化代码** ：减少了创建和管理多个实例的复杂性，使代码更加简洁。

### 单例模式的缺点

  1. **违背单一职责原则** ：单例类可能承担了过多的职责，因为它不仅要负责自身的状态和行为，还要管理实例的创建和生命周期。
  2. **测试困难** ：由于单例类的全局状态，可能会导致单元测试变得复杂，因为测试之间可能会相互影响。
  3. **线程安全问题** ：在多线程环境下，如果实现不当，可能会导致多个线程同时创建多个实例，破坏单例的唯一性。可以在实现时加入线程安全机制，比如使用锁来确保线程安全。

## 十七、异常处理

Python 的异常处理机制允许程序在遇到错误时优雅地处理问题，而不是直接崩溃。异常处理通过 `try`、`except`、`else` 和 `finally` 关键字来实现。

### 基本结构

```python
try:
    # 尝试执行的代码块
    risky_code()
except SomeException as e:
    # 捕获并处理异常
    print(f"异常: {e}")
else:
    # 如果没有异常发生，执行此代码块
    print("没有异常发生")
finally:
    # 无论是否发生异常，都会执行的代码块
    print(" finally块执行")
```

### 常见的异常类型

  1. `SyntaxError`：语法错误，代码不符合 Python 的语法规则。
  2. `NameError`：尝试访问一个未定义的变量名。
  3. `TypeError`：操作或函数被应用于不适当类型的数据。
  4. `ValueError`：数据类型正确，但值不符合要求。
  5. `IndexError`：序列中没有该索引。
  6. `KeyError`：字典中没有该键。
  7. `FileNotFoundError`：找不到文件。
  8. `ZeroDivisionError`：除数为零。
  9. `IOError`：输入/输出操作失败，通常与文件操作相关。
  10. `ImportError`：导入模块失败。
  11. `KeyboardInterrupt`：程序运行时用户中断（如按下 Ctrl+C）。
  12. `MemoryError`：内存不足时抛出。
  13. `OverflowError`：算术运算结果超出表示范围时抛出。
  14. `RuntimeError`：一般运行时错误，无更具体的错误类型时使用。
  15. `SystemError`：Python 解释器内部错误。
  16. `IndentationError`：缩进错误或不一致。
  17. `UnboundLocalError`：尝试访问未绑定值的局部变量。
  18. `UnicodeError`：Unicode 编码或解码错误。

### 异常处理的应用示例

```python
try:
    # 尝试执行可能引发异常的代码
    num = int(input("请输入一个整数："))
    result = 10 / num
    print(f"10 除以 {num} 的结果是 {result}")
except ValueError:
    # 捕获并处理 ValueError 异常
    print("输入无效！请输入一个有效的整数。")
except ZeroDivisionError:
    # 捕获并处理 ZeroDivisionError 异常
    print("错误！除数不能为零。")
except Exception as e:
    # 捕获其他所有异常
    print(f"发生了一个错误：{e}")
else:
    # 如果没有发生异常，执行此代码块
    print("程序正常执行，没有发生异常。")
finally:
    # 无论是否发生异常，都会执行的代码块
    print("程序执行完毕，释放资源或清理环境。")
```

### 自定义异常

可以通过创建继承自 `Exception` 类的子类来定义自定义异常：

```python
class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)

try:
    raise CustomError("这是一个自定义的异常")
except CustomError as e:
    print(f"捕获自定义异常：{e}")
```

