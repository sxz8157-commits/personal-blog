# MYSQL

### 1、SQL的概述

- SQL全称: Structured Query,Language，是结构化査询语言，用于访问和处理数据库的标准的计算机语言SQL语言1974年由Boyce和Chamberlin提出，并首先在IBM公司研制的关系数据库系统SystemR上实现。
- 美国国家标准局(ANSI)开始着手制定SQL标准，并在1986年10月公布了最早的SQL标准，扩展的标准版本是1989年发表的SQL-89，之后还有1992年制定的版本SQL-92和1999年ISO发布的版本SQL-99.
- SQL标准几经修改和完善，其功能更加强大，但目前很多数据库系统只支持SQL-99的部分特征，而大部分数据库系统都能支持1992年制定的SQL-92。

### 2、SQL的特点

- 具有综合统一性，不同数据库的支持的SQL稍有不同
- 非过程化语言
- 语言简捷，用户容易接受
- 以一种语法结构提供两种使用方式

### 3.语法特点

- SQL对关键字的大小写不敏感

- SQL语句可以以单行或者多行书写，以分行结束

- SQL的注释:

  ```mysql
  -- 单行注释, -- 后面一定要加一个空格
  # 单行注释, # 后面可加可不加空格
  SELECT * FROM emp; -- 这里是注释
  /*
  多行注释
  多行注释
  
  */
  ```

## 一,数据库基本操作

DDL(Data Definition Language)，数据定义语言，该语言部分包括以下内容

- 对数据库的常用操作
- 对表结构的常用操作十
- 修改表结构

### 1,创建数据库

```mysql
-- 1,DDL操作之数据库操作
-- 查看数据库
SHOW DATABASES;
-- 创建数据库
create database mydb1;
create database if not exists mydb1;
-- 切换数据库
use mydb1;
-- 删除数据库
drop database mydb1;
drop database if exists mydb1;
-- 修改数据库编码
alter database mydb1 character set utf8;
```

### 2,创建表

创建表是构建一张空表，指定这个表的名字，这个表有几列，每一列叫什么名字，以及每一列存储的数据类型。

创建表格式

create table [if not exists]表名(

​	字段1 类型[(宽度)] [约束条件] [comment '字段说明']

)[表的一些设置];

```mysql
-- 创建表

-- 选择mydb1
use mydb1;

create table if not exists student(
  sid INT,
  name varchar(20),
  grnder varchar(10),
  age int,
  virth date,
  adderss varchar(20),
  score double
);
```

## 二,数据类型

|    CHAR    | 0-255 bytes           | 定长字符串                      |
| :--------: | --------------------- | ------------------------------- |
|  varchar   | 0-65535 bytes         | 变长字符串                      |
|  tinyblob  | 0-255 bytes           | 不超过 255 个字符的二进制字符串 |
|  tinytext  | 0-255 bytes           | 短文本字符串                    |
|    blob    | 0-65 535 bytes        | 二进制形式的长文本数据          |
|    text    | 0-65 535 bytes        | 长文本数据                      |
| mediumblob | 0-16 777 215 bytes    | 二进制形式的中等长度文本数据    |
| mediumtext | 0-16 777 215 bytes    | 中等长度文本数据                |
|  longblob  | 0-4 294 967 295 bytes | 二进制形式的极大文本数据        |
|  longtext  | 0-4 294 967 295 bytes | 极大文本数据                    |

### 日期类型

| 类型      | 大小（bytes） | 范围                                                         | 格式                    | 用途                     |
| --------- | ------------- | ------------------------------------------------------------ | ----------------------- | ------------------------ |
| DATE      | 3             | 1000 - 01 - 01/9999 - 12 - 31                                | YYYY - MM - DD          | 日期值                   |
| TIME      | 3             | '-838:59:59'/'838:59:59'                                     | HH:MM:SS                | 时间值或持续时间         |
| YEAR      | 1             | 1901/2155                                                    | YYYY                    | 年份值                   |
| DATETIME  | 8             | 1000 - 01 - 01 00:00:00/9999 - 12 - 31 23:59:59              | YYYY - MM - DD HH:MM:SS | 混合日期和时间值         |
| TIMESTAMP | 4             | 1970 - 01 - 01 00:00:00/2038（结束时间是第 2147483647 秒，北京时间 2038 - 1 - 19 11:14:07，格林尼治时间 2038 年 1 月 19 日凌晨 03:14:07） | YYYYMMDD HHMMSS         | 混合日期和时间值，时间戳 |

| 功能                       | SQL                      |      |      |      |
| -------------------------- | ------------------------ | ---- | ---- | ---- |
| 查看当前数据库的所有表名称 | show tables;             |      |      |      |
| 查看指定某个表的创建语句   | show create table 表名； |      |      |      |
| 查看表结构                 | desc 表名                |      |      |      |
| 删除表                     | drop table 表名          |      |      |      |

```mysql
-- 3.查看当前数据库所有的表
show tables;
-- 4.查看指定表的创建语句
show create table student;
-- 5,查看表结构
desc student
-- 6,删除表
drop table student
```

## 三,修改表的结构

### 添加列

语法格式:
	alter table 表名 add 列名类型(长度)[约束];

```
--修改表结构
-- 1.添加列:alter table 表名 add 列名 类型(长度)[约束]; #为student表添加一个新的字段为:系别dept 类型为varchar(20)
alter table student add dept varchar(20);
```

### 修改列

语法格式:

​	rename table 表名 to 新列名;

```
-- 4.修改表名:renametable表名to 新表名;
-- 将student表的名字改为stu
rename table student to stu;
```



### 删除列

语法格式:
	alter table 表名 drop列名;

```
#删除列:alter table 表名 drop列名;
-- 删除student表中的department;
alter table student drop department
```

### 修改表名

​	语法格式:
​	rename table 表名 to 新表名;

```
-- 4.修改表名:renametable表名to 新表名;
-- 将student表的名字改为stu
rename table student to stu;
```

## 四,DML

### 1,基本介绍

DML是指数据操作语言，英文全称是Data Manipulation Language，用来对数据库中表的数据记录进行更新。关键字:

- 插入insert
- 删除delete
- 更新update

### 2,数据插入

​	语法格式:

insert into 表 (列名1,列名2,列名3..) values (值1,值2,值3...);//向表中插入某些
insert into 表 values (值1,值2,值3...); //向表中插入所有列

```mysql
-- 1,数据的插入
-- insert into 表 (列名1,列名2,列名3..) values (值1,值2,值3...);//向表中插入某些
-- insert into 表 values (值1,值2,值3...); //向表中插入所有列
insert into stu(sid,name,gender,age,birth,adderss,score)
				values(1001,'张三','男',18,'2001-12-23','北京',87.2);
#创建单行后面不填数
insert into stu(sid) values(1004);				
insert into stu(sid,name) values(1005,'赵六');
```

格式二:insert into 表 values(值1,值2,值3....);//向表中插入所用列

```
-- 2,格式二:insert into 表 values(值1,值2,值3....);//向表中插入所用列
insert into stu values(1006,'张华','女',21,'1999-01-08','广州',70);
insert into stu values(1007,'张华','女',21,'1999-03-08','广州',70),
(1008,'张给','女',31,'1999-01-08','广州',70);

```

### 2,数据修改

语法格式:
update 表名 set 字段名=值,字段名=值...;

update 表名 set 字段名=值,字段名=值...where 条件;

```
-- 所有学生的地址修改为重庆
update stu set adderss='重庆';

-- 将id为1004的学生的地址修改为北京
update stu set adderss='北京' where sid=1004;
update stu set adderss='上海' where sid>1004;
-- 讲id为1005的学生的地址修改为北京，成绩修成绩修改为100
update stu set adderss='北京',score=100 where sid=1005
```

### 3,数据删除

语法格式:
delete from 表名[where 条件];

truncate table 表名 或者 truncate 表名;

> 注意:delete和truncate原理不同，delete只删除内容，而truncate类似于drop table，可以理解为是将整个表删除然后再创建该表;

```mysql
-- 1.删除sid为1004的学生数据
delete from stu where sid=1004;
-- 2.删除表所有数据
delete from stu;
-- 3.清空表数据
truncate table stu;
truncate stu;
```

## 五,MySQL约束

### 主键约束

操作-添加单列主键

创建单列主键有两种方式

> 一种是定义完字段之后指走主键
>
> 一种是在定义字段的同时指定主键

- 非空
- 唯一

```
create table 表名 (
   ...
    <字段名> <数据类型> primary key
   ...
)
```



```mysql
-- 第一种方法
use mydb1;
create table emp1(
	eid int primary key,
	name varchar(20),
	deptid int,
	salary double
);


-- 方式2-语法:
-- 在定义字段之后再指定主键，语法格式如下:create table 表名(
-- [constraint<约束名>]primary key[字段名]
create table emp2(
  eid int,
  name varchar(20),
  deptid int,
  salary double,
  constraint pk1 primary key(eid)
-- constraint pk1可以省略
);

-- 主键的作用
-- 非空
-- 唯一
insert into emp2(eid,name,deptid,salary) values(1001,'张四',10,4000);
insert into emp2(eid,name,deptid,salary) values(NULL,'张四',10,4000);
```

### 多列主键(联合主键)

所谓的联合主键，就是这个主键是由一张表中多个字段组成的。注意:
1.当主键是由多个字段组成时，不能直接在字段名后面声明主键约束。

2.一张表只能有一个主键,联合主键也是一个主键

```mysql
create table emp3(
  name varchar(20),
  deptid int,
  salary double,
  constraint pk2 primary key(name,deptid)
);
insert into emp3 values('张三',10,5000);
insert into emp3 values('张三',10,5000);-- 不能重复
insert into emp3 values('NULL',10,5000);-- 不能为空
```

通过修改表结构添加主键

主键约束不仅可以在创建表的同时创建，也可以在修改表时添加。
语法:

```
create table 表名(
  ...
);
alter table<表名> add primary key(字段列表);
```

```mysql
-- 添加单列主键

create table emp4(
  eid int,
  name varchar(20),
  deptId int,
  salary double
);
alter table emp4 add primary key(eid);

-- 添加多列主键
create table emp5(
  eid int,
  name varchar(20),
  deptId int,
  salary double
);
alter table emp5 add primary key(name,deptId);
```

### 删除主键约束

一个表中不需要主键约束时，就需要从表中将其删除。删除主键约束的方法要比创建主键约束容易的多
格式:

```
alter table <数据表名> drop primary key;
```

实现:

```
-- 删除单列主键
alter table emp1 drop primary key;
-- 删除多列主键
alter table emp5 drop primary key;
```

### MySQL约束-自增长约束(auto_increment)

概念

> 在 MySQL中，当主键定义为自增长后，这个主键的值就不再需要用户输入数据了，而由数据库系统根据定义自动赋值每增加一条记录，主键会自动以相同的步长进行增长。
> 通过给字段添加 **auto_increment** 属性来实现主键自增长

语法

```
字段名 数据类型 auto_increment
```

```mysql
-- 自增长约束
create table t_user1(
  id int primary key auto_increment,
 name varchar(20) 
);
insert into t_user1 values(NULL,'张三');
insert into t_user1(name) values('张四');
```

特点

> 默认情况下，auto increment的初始值是1，每新增一条记录，字段值自动加 1
>
> 一个表中只能有一个字段使用 auto increment约束，且该字段必须有唯一索引，以避免席号重复(即为主键或主键的一部分)
>
> auto_increment约束的字段必须具备 NOT NULL 属性
>
> auto increment约束的字段只能是整数类型(TINYINT、SMALLINT、INT、BIGINT 等
>
> auto_increment约束字段的最大值受该字段的数据类型约束，如果达到上限，auto_increment就会失效

### 指定自增字段初始值

> 如果第一条记录设置了该字段的初始值，那么新增加的记录就从这个初始值开始自增。
>
> 例如，如果表中插入的第条记录的 id 值设置为 5，那么再插入记录时，id 值就会从5 开始往上增加

```mysql
-- 方式一,创建表时指定
create table t_user2(
  id int primary key auto_increment,
  name varchar(20)
)auto_increment=100;
insert into t_user2 values(NULL,'张三');
insert into t_user2(name) values('张四');

-- 方式二,创建表之后指定
create table t_user3(
  id int primary key auto_increment,
  name varchar(20)
);
alter table t_user2 auto_increment=100;
insert into t_user3 values(NULL,'张三');
insert into t_user3(name) values('张四');

```

#### delete和truncate在删除后自增列的变化

- delete数据之后自动增长从断点开始
- truncate数据之后自动增长从默认起始值开始

```mysql
-- delete删除数据之后自增长还是在最后一个值加1
delete from t_user1;
insert into t_user1 values(NULL,'张三');

-- truncate删除之后,自增长从1开始
truncate t_user1;
insert into t_user1 values(NULL,'张三');
```

### 非空约束(not null)

>概念
>MvSQL非空约束(not nul)指字段的值不能为空。对于使用了非空约束的字段，如果用户在添加数据时没有指定值，数据库系统就会报错。

语法:

```mysql
 方式一:<字段名><数据类型> not null;
 方式二:alter table 表名 modify 字段 类型
 not null;
```

添加非空约束-方式1:

```mysql
 create table t_user6(
  id int,
  name varchar(20) not null,
  address varchar(20) not null 
 );
```

添加非空约束-方式2:

```mysql
 create table t_user7(
  id int,
  name varchar(20),
  address varchar(20)
 );
 alter table t_user7 modify name varchar(20) not null;
 alter table t_user7 modify address varchar(20) not null;
```

删除非空约束:

```
 -- alter table 表名 modify 字段 类型
 alter table t_user7 modify name varchar(20);
 alter table t_user7 modify address varchar(20);
```

### 唯一约束(unique)

> 概念
> 唯一约束(Unigue Key)是指所有记录中字段的值不能重复出现。例如，为id字段加上唯一性约束后，每条记录的 id 值都是唯一的，不能出现重复的情况。

语法:

```mysql
方式一:<字段名><数据类型> unique;
方式二:alter table 表名 add constraint 约束名 unique(列);
```

方式1-创建时指定:

```mysql
create table t_user8(
  id int,
  name varchar(20),
  phone_number varchar(20) unique -- 指定唯一约束
);
```

方式2-创建后指定:

```mysql
alter table t_user9 add constraint unique_pn unhex(phone-number);
```

删除唯一约束
格式:alter table 表名 drop index <唯一约束名>

```mysql
alter table t_user9 drop index unique_pn;
```

### 默认约束(default)

> 概念
> MySQL默认值约束用来指定某列的默认值。

语法:

```mysql
方式1:<字段名><数据类型> default <默认值>;
方式2:alter table 表名 modify 列名 类型 default 默认值;
```

添加默认约束-方式1:

```mysql
create table t_user10(
  id int,
  name varchar(20),
  address varchar(20) default '北京'-- 指定默认约束
);
```

创建后指定方式2:

```mysql
create table t_user11(
  id int,
  name varchar(20),
  address varchar(20)

);
alter table t_user11 modify address varchar(20) default '深圳';
```

### 零填充约束(zerofill)

> 概念
> 1、插入数据时，当该字段的值的长度小于定义的长度时，会在该值的前面补上相应的0
>
> 2、zerof默认为int(10)
> 3、当使用zerofil 时，默认会自动加unsigned(无符号)属性，使用unsigned属性后，数值范围是原值的2倍，例如，有符号为-128~+127，无符号为0~256。

操作:

```mysql
create table t_user12(
  id int zerofill,-- 零填充约束
  name varchar(20)
);
```

删除:

```mysql
alter table t_user12 modify id int;
```

## 六,DQL查询

> 概念
> 数据库管理系统一个重要功能就是数据查询，数据查询不应只是简单返回数据库中存储的数据，还应该根据需要对数据进行筛选以及确定数据以什么样的格式显示。MySQL提供了功能强大、灵活的语句来实现这些操作。MySQL数据库使用select语句来查询数据。

语法格式:

```mysql
select 
  [all|distinct]
  <目标列的表达式1> [别名],
  <目标列的表达式2> [别名]...
from <表名或视图名> [别名],<表名或视图名>[别名]...
[where <条件表达式>]
[having <条件表达式>]
[order by <列名> [asc|desc]]
[limit <数字或者列表>];
```

简化版语法:

```mysql
select *| 列名from 表 where 条件
```

### 数据准备

​	创建数据库和表：

```mysql
-- 创建数据库
create database if not exists mydb2;
use mydb2;
-- 创建商品表：
create table product (
  pid int primary key auto_increment, -- 商品编号
  pname varchar(20) not null, -- 商品名字
  price double, -- 商品价格
  category_id varchar(20) -- 商品所属分类
);
```

​	添加数据:

```mysql
insert into product values(null,'海尔洗衣机',5000,'c001');
insert into product values(null,'美的冰箱',3000,'c001');
insert into product values(null,'格力空调',5000,'c001');
insert into product values(null,'九阳电饭煲',5000,'c001');
insert into product values(null,'啄木鸟衬衣',300,'c002');
insert into product values(null,'恒源祥西裤',800,'c002');
insert into product values(null,'花花公子夹克',440,'c002');
insert into product values(null,'劲霸休闲裤',266,'c002');
insert into product values(null,'海澜之家卫衣',180,'c002');
insert into product values(null,'杰克琼斯运动裤',430,'c002');
insert into product values(null,'兰蔻面霜',300,'c003');
insert into product values(null,'雅诗兰黛精华水',200,'c003');
insert into product values(null,'香奈儿香水',350,'c003');
insert into product values(null,'SK-II神仙水',350,'c003');
insert into product values(null,'资生堂粉底液',180,'c003');
insert into product values(null,'老北京方便面',56,'c004');
insert into product values(null,'良品铺子海带丝',17,'c004');
insert into product values(null,'三只松鼠坚果',88,null);
```

###   简单查询:

```mysql
### 简单查询
-- 1. 查询所有的商品。
SELECT pid,pname,price,category_id from product;
select * from product;
-- 2. 查询商品名和商品价格。
select pname,price from product;
-- 3. 别名查询.使用的关键字是as（as可以省略的）。
-- 3.1 表别名：
select * from product as p;
select * from product p; 
-- 3.2 列别名：
select pname as '商品名',price '商品价格' from product;
-- 4. 去重。
select distinct price from product;
select distinct * from product;
-- 5. 查询结果是表达式（运算查询）：将所有商品的加价10元进行显示。
select pname,price + 10 new_price from product;
```

### 运算符

- 简介

  

  > 数据库中的表结构确立后，表中的数据代表的意义就已经确定。通过 MySQL 运算符进行运算，就可以获取到表结构以外的另一种数据。

> 例如，学生表中存在一个 birth 字段，这个字段表示学生的出生年份。而运用 MySQL 的算术运算符用当前的年份减学生出生的年份，那么得到的就是这个学生的实际年龄数据。

MySQL 支持 4 种运算符

- **算术运算符**
- **比较运算符**
- **逻辑运算符**
- **位运算符**

| 算术运算符 |        说明        |
| :--------: | :----------------: |
|     +      |      加法运算      |
|     -      |      减法运算      |
|     *      |      乘法运算      |
|  / 或 DIV  |  除法运算，返回商  |
|  % 或 MOD  | 求余运算，返回余数 |

```
-- 算数运算符
select 6 + 2;
select 6 - 2;
select 6 * 2;
select 6 / 2;
select 6 % 2;
-- 将所有商品的价格加10元
select pname,price + 10 as new_price from product;
-- 将所有的商品价格上调10%
select pname,price * 1.1 as new_price from product;
```

|    比较运算符     |                             说明                             |
| :---------------: | :----------------------------------------------------------: |
|         =         |                             等于                             |
|      < 和 <=      |                        小于和小于等于                        |
|      > 和 >=      |                        大于和大于等于                        |
|        <=>        | 安全的等于，两个操作码均为NULL时，其所得值为1；而当一个操作码为NULL时，其所得值为0 |
|     <> 或 !=      |                            不等于                            |
| IS NULL 或 ISNULL |                     判断一个值是否为NULL                     |
|    IS NOT NULL    |                    判断一个值是否不为NULL                    |
|       LEAST       |               当有两个或多个参数时，返回最小值               |
|     GREATEST      |               当有两个或多个参数时，返回最大值               |
|    BETWEEN AND    |                 判断一个值是否落在两个值之间                 |
|        IN         |               判断一个值是IN列表中的任意一个值               |
|      NOT IN       |              判断一个值不是IN列表中的任意一个值              |
|       LIKE        |                          通配符匹配                          |
|      REGEXP       |                        正则表达式匹配                        |

```

```

| 逻辑运算符  |   说明   |
| :---------: | :------: |
| NOT 或者 !  |  逻辑非  |
| AND 或者 && |  逻辑与  |
|   OR 或者   |  逻辑或  |
|     XOR     | 逻辑异或 |

| 位运算符 |          说明          |
| :------: | :--------------------: |
|    \|    |         按位或         |
|   `&`    |         按位与         |
|   `^`    |        按位异或        |
|   `<<`   |        按位左移        |
|   `>>`   |        按位右移        |
|   `~`    | 按位取反，反转所有比特 |

> 位运算符是在二进制数上进行计算的运算符位运算会先将操作数变成二进制数，进行位运算然后再将计算结果从二进制数变回十进制数

```
-- 位运算符
select 3 & 5;-- 按位与
0011
0101
--------
0001
select 3 | 5;-- 按位或
0011
0101
-------
0111
select 3 ^ 5;-- 按位异或
0011
0101
-------
0110
select 3 >> 1;-- 向右移位
0011>>0001
select 3 << 1;-- 向左移位
0011<0110
select 3 ~ 5;-- 取反
0000000000000000000000011~
1111111111111111111111100
```



```mysql
-- 查询商品名称为“海尔洗衣机”的商品所有信息：
select * from product where pname='海尔洗衣机';
-- 查询价格为800商品
select * from product where price = 800;
-- 查询价格不是800的所有商品
select * from product where price != 800;
select * from product where price <> 800;
select * from product where not (price = 800);
-- 查询商品价格大于60元的所有商品信息
select * from product where price >= 60;
-- 查询商品价格在200到1000之间所有商品
select * from product where price between 200 and 1000;
select * from product where price >= 200 and
price <= 1000;
select * from product where price >= 200 &&
price <= 1000;
-- 查询商品价格是200到1000之间所有商品
select * from product where price in(200,800);
select * from product where price = 200 or price = 800;
select * from product where price = 200 ||price = 800;
-- 查询含有'裤'字的所有商品
select * from product where pname like '%裤%';-- %用来匹配任意字符
-- 查询含有'海'字的所有商品
select * from product where pname like '%海%';-- %用来匹配任意字符
-- 查询第二个字是'蔻'字的所有商品
select * from product where pname like '_蔻%';-- _下划线用来匹配单个字符
-- 查询category_id为null的商品
select * from product where category_id is not null;
-- 查询category_id不是null的商品
select * from product where category_id is not null;
-- 使用least求最小值
select least(10,5,20) as small_number;
select least(null,5,20) as small_number;-- 如果求最小值时，有个值为nu11，则不会进行比较，结果直接为nu1l;
-- 使用greatest求最大值
select least(10,5,20) as big_number;-- 如果求最大值时，有个值为nu11，则不会进行比较，结果直接为nu1l;
```

### 排序查询**order by**

- **介绍**：如果需要对读取的数据进行排序，可使用MySQL的`order by`子句设定按哪个字段、哪种方式排序，再返回搜索结果。语法为

- ```mysql
  select 字段名1，字段名2，...... from 表名 order by 字段名1 [asc|desc]，字段名2 [asc|desc]......
  ```

- **特点**：
  1. `asc`代表升序，`desc`代表降序。
  2. `order by`用于子句中可以支持字段、表达式、函数、别名。
  3. `order by`子句，放在查询语句的最后（`LIMIT`子句除外） 。 

```mysql
-- 1.使用价格排序 (降序)
select * from product order by price desc;
select * from product order by price asc;
-- 或者
select * from product order by price;
-- 2.在价格排序 (降序) 的基础上，以分类排序 (降序)
select * from product order by price desc,category_id desc;
-- 3.显示商品的价格 (去重复)，并排序(降序)
select distinct price from product order by price desc;
```

### 限制结果集(limit)

> limit n :取前n条记录 
>
> limit offset,n  :从第offset条开始取，取n条

```mysql
select * from tb_student limit 1;
select * from tb_student limit 0,10;
注意结果集中记录从0开始数数，offset相对于0开始
实现分⻚必须的技术点
limit (page-1)*num,num
```

### 集合函数

- count统计结果集中记录数 
- max 最⼤值 
- min 最⼩值 
- avg 平均值，只针对数值类型统计 
- sum 求和，只针对数值类型统计 
- 注意，集合函数不能直接使⽤在where后⾯的条件⾥，但可以在⼦查询中

```mysql
select count(*) num from user;
select count(distinct age) num from user; //去除重复记录
select * from student where sno = max(sno);//错误
```

### 分组（group by)

将结果集分组统计，规则： 

- 出现了group by的查询语句，select后⾯的字段只能是集合函数和group by后 ⾯有的字段，不要跟其它字段 
- 对分组进⾏过滤，可以使⽤having

```mysql
select stusex,count(*) from tb_student group by stusex;
mysql> select stusex,count(*) from tb_student group by stusex having
count(*) > 3;
```

### having

> HAVING 和 WHERE 功能类似，都可以⽤来实现条件查询。很多情况下可以⽤ 
>
> where 或者 having ，甚⾄可以混合使⽤。

```mysql
select * from tb_student having stusex=1;
select stuname,stubirth from tb_student having stubirth > '1990-1-1';
```

- 只能⽤where，不能使⽤having

```mysql
# where可以任何已经存在的字段
select stuname,stusex,stubirth from tb_student where stuid=1001;
# 如果select后⾯的字段列表⾥没有出现的字段，having中不能使⽤
select stuname,stusex,stubirth from tb_student having stuid=1001;
```

- 只能使⽤having

```mysql
select stuname,stusex as sex from tb_student having sex=1; #where⽆
法使⽤sex，因为不存在
 #group by后⾯只能⽤having
select stusex,count(stusex) num from tb_student group by stusex
having num>1
```

### 查询⼩结

- 整体顺序不能颠倒 
- []表示可选，可以有也可以没有 
- select 字段 from 表名 [where 条件] 
- [ group by ] 
- [having] 
- [ order by ] 
- [limit]

## 七,高级查询

### 	多表查询

- 多表连接必须**要有连接条件**，否则结果没有意义 
- 多表连接有两种写法：隐式(标准sql)和显式内连接 
- 隐式(标准sql)连接 ： 连接条件写到where字句中

```mysql
select * from tb_student,tb_record where stuid=sid limit 10;
select *
from tb_student s,tb_record as r --#给表起⼀个别名，⽅便书写
where stuid=sid limit 10; --在where写链接条件
```

#### 显式内连接（inner join）

```mysql
select * from tb_student s inner join tb_record r on s.stuid=r.sid; -
- on后是两表关联条件
# on是连接条件，where是过滤条件
select * from tb_student s inner join tb_record r on s.stuid=r.sid
where score>90
select teaname, collname, stuname,couname,score,s.collid from
tb_student s inner join tuid=r.sid join tb_course c on c.couid=cid
join tb_college coll on s.collid= coll.collit on c.teaid=t.teaid 
where score is not null order by score desc;
select后的字段如果在多个表中都有，引⽤的时候必须加上表名(别名).字段名
```

#### 表的⾃身连接

```mysql
select * from areainfo a,areainfo b where a.pid=b.code and 
a.name='⻘河县';
+--------+-----------+--------+--------+-----------------+--------+
| code | name | pid | code | name | pid |
+--------+-----------+--------+--------+-----------------+--------+
| 654325 | ⻘河县 | 654300 | 654300 | 阿勒泰地区 | 650000 |
+--------+-----------+--------+--------+-----------------+--------+
1 row in set (0.01 sec)
# 表的字段可以直接连接
select * from zzl_student where sno = monitor and class='95031';
```

### 外连接

> 两张表关联查询时，根据以那种表为主可以分为左外连接和右外连接

- 左外连接

> 以左表为主，如果右边的表⾥没有匹配的记录，则添加⼀个万能记录（各个字段都 为null)与之连接

```mysql
select username,r.* from blog_user u left join blog_remark r on
u.uid = r.uid
+-----------+------+-------------+------+------+------------+--------
---+
| username | rid | remark | aid | uid | remarktime |
isdisplay |
+-----------+------+-------------+------+------+------------+--------
---+
| 萧峰 | 1 | adsafd | 1 | 1 | NULL | 
0 |
| 慕容复 | 2 | kdkdkdkd | 2 | 3 | NULL | 
0 |
| 丁春秋 | 3 | ooooooooooo | 3 | 4 | NULL | 
0 |
| 丁春秋 | 4 | ppppp | 2 | 4 | NULL | 
0 |
| 阿朱 | NULL | NULL | NULL | NULL | NULL | 
NULL |
| 阿碧 | NULL | NULL | NULL | NULL | NULL | 
NULL |
| 谢晓峰 | NULL | NULL | NULL | NULL | NULL | 
NULL |
+-----------+------+-------------+------+------+------------+--------
---+
```



- 右外连接

> 以右表为主，如果左边的表⾥没有匹配记录，则增加⼀个万能记录与之连接

### ⼦查询

- ⼦查询嵌⼊到其他查询语句中查询语句，⼦查询只能出现在from，where、 having中 
- ⼦查询不要⽤select *,exists除外

```mysql
# 不相关⼦查询
mysql> select * from tb_student where stuid in (select sid from
tb_record where score>90);
select * from (select * from tb_record where score>90) tmp join
tb_student on tmp.sid=tb_student.stuid;
# 相关⼦查询
select * from tb_student where exists (select * from tb_record where
tb_student.stuid=sid and score > 90);
```

### 合并结果集

可以使⽤union将两个查询结果合并，mysql只⽀持并，不⽀持差和交

- 两个结果集中字段数⼀样，对应字段类型兼容 
- ⾃动去除重复记录,不去除重复记录可以⽤ union all 
- order by 放到最后

```mysql
select * from student where class = '95031'
union all
select * from student where ssex='⼥';
```

### 内部函数

字符串函数

| 函数                       | 功能                                                         |
| -------------------------- | ------------------------------------------------------------ |
| `char_length(str)`         | 获取字符串的字符个数                                         |
| `length(str)`              | 获取字符串的字节数                                           |
| `concat(s1, s2, ..., sn)`  | 连接s1, s2, ..., sn 为一个字符串                             |
| `lower(str)`               | 将字符串str中所有的字符转换为小写                            |
| `upper(str)`               | 将字符串str中所有的字符转换为大写                            |
| `left(str, x)`             | 返回字符串str最左边的x个字符                                 |
| `right(str, y)`            | 返回字符串str最右边的y个字符                                 |
| `ltrim(str)`               | 去掉str中最左边的空格                                        |
| `rtrim(str)`               | 去掉str中最右边的空格                                        |
| `trim(str)`                | 去掉字符串str两边的空格                                      |
| `repeat(str, x)`           | 返回str中重复出现x次的结果                                   |
| `replace(str, a, b)`       | 将字符串str中的a更换为b                                      |
| `insert(str, x, y, instr)` | 将字符串str从第x位置开始，y个字符长度的子字符串替换为字符串instr |
| `substring(str, x, y)`     | 返回字符串str x位置开始y个字符长度的字符串                   |

⽇期函数

| 函数名                              | 功能                              |
| ----------------------------------- | --------------------------------- |
| `curdate()`                         | 得到当前日期                      |
| `curtime()`                         | 得到当前时间                      |
| `now()`                             | 得到当前日期和时间                |
| `year(date)`                        | 得到date的年份                    |
| `month(date)`                       | 得到date的月份                    |
| `day(date)`                         | 得到date的天                      |
| `hour(time)`                        | 得到time的小时                    |
| `minute(time)`                      | 得到time的分钟                    |
| `second(time)`                      | 得到time的秒                      |
| `week(date)`                        | 得到date是一年中的第几周          |
| `date_format(date,fmt)`             | 按格式化串fmt返回date的日期字符串 |
| `DATE_ADD(date,INTERVAL expr unit)` | 从指定日期加上一个时间间隔        |
| `DATE_SUB(date,INTERVAL expr unit)` | 从指定日期减去一个时间间隔        |
| `DATEDIFF(expr1,expr2)`             | 计算两个日期相差天数              |

```mysql
# 格式化⽇期字符串
select DATE_FORMAT(now(),'%Y- %m-%d %H:%i:%s');
# 常⻅时间间隔的单位
MICROSECOND、SECOND、MINUTE、HOUR、DAY、WEEK、MONTH、QUARTER、YEAR
# ⽇期运算
select date_add(now(), interval 1 day); -- 加 1 day
select date_add(now(), interval 1 hour); -- 加 1 hour
select DATE_sub(now(),Interval 1 year) -- 减 1 年
SELECT DATEDIFF(now(),'2008-12-30') -- 计算两个⽇期相差天数
```

数学函数

| 函数名       | 功能                        |
| ------------ | --------------------------- |
| `abs(x)`     | 求x的绝对值                 |
| `ceil(x)`    | 向上取整                    |
| `floor(x)`   | 向下取整                    |
| `round(x,d)` | 四舍五入，d为保留小数的位数 |
| `pow(x,y)`   | x的y次幂                    |
| `rand()`     | 0~1之间的随机小数           |
| `mod(x,y)`   | 等同于x % y,求x对y的模      |

其它函数

| 函数名                                   | 功能                                                         |
| ---------------------------------------- | ------------------------------------------------------------ |
| `convert(expr ,type)/cast(expr as type)` | 将表达式expr转换为type类型，type可以是：char(n)、date、datetime、integer、decimal type |
| `md5(str)`                               | 计算str的哈希值，返回一个32位十六进制数字的二进制字符串      |
| `sha2/sha1/sha`                          | 计算str的哈希值，返回一个40位十六进制数字的二进制字符串      |

### 常⽤流程函数

if函数

```mysql
IF(condition, expr1, expr2)
功能：如果condition为True，返回表达式expr1的值，否则返回表达式expr2的
参数：
 condition 判断条件。
 expr1 –它是⼀个可选参数，⽤于指定条件评估为true时要返回的值。
 expr2 –它是⼀个可选参数，⽤于指定条件评估为false时要返回的值。
示例：
select stuname,if(stusex=1,'男','⼥') from tb_student
# ⾏转列
select name,
if(subject='数学',score,null) 数学 ,
if(subject='语⽂',score,null) 语⽂ ,
if(subject='python',score,null) python
from marks
```

ifnull

```mysql
IFNULL(express1,express2)
功能：如果expr1不是NULL，IFNULL()返回expr1，否则它返回expr2。
参数：
 express1、express2： 任意表达式
示例：
SELECT stuname,ifnull(stuaddr,'⽆地址') from tb_student;
```

nullif

```mysql
NULLIF(expr1,expr2)
功能：如果expr1=expr2成⽴，那么返回值为null，否则返回值为expr1的值。
参数：
 expr1、expr2： 任意表达式
示例：
select nullif(1,1) # NULL
select nullif(1,2) # 1
```

case when

```mysql
第⼀种 格式 : 简单Case函数 :
格式说明 
　　　　case 列名
　　　　when 条件值1 then 选项1
　　　　when 条件值2 then 选项2.......
　　　　else 默认值 
　　　　end
 mysql> select stuname,case stusex when 1 then '男'
 -> when 0 then '⼥'
 -> end
 -> from tb_student;
 
第⼆种 格式 :Case搜索函数
格式说明 
　　　　case 
　　　　when 列名= 条件值1 then 选项1
　　　　when 列名=条件值2 then 选项2.......
　　　　else 默认值
　　　　end
 mysql> select name,subject,score,case when score > 90 then '优秀'
 -> when score >80 then '良好'
 -> when score > 60 then '及格'
 -> else '不及格'
 -> end
 -> from marks;
```

## 八,窗口函数

### 1、简介

```markdown
窗口函数基于对数据的子集或 "窗口 "进行的计算创建一个新列。这个窗口从特定列上的第一行开始，除非限制窗口的大小，否则窗口的大小会增加。

如果我们将窗口限制为3行高，我们可以得到一个连续3天平均收入。

​```sql
SELECT 'Day', 'Mile Driving',SUM('Miles Driving')
OVER(ORDER BY 'Day') AS 'Running Total' FROM 'Running total mileage
visual';
```

如果我们将窗⼝限制为3⾏⾼，我们可以得到⼀个连续3天平均收⼊。

```sql
SELECT 'Day', 'Daily Revenue',AVG('Daily Revenue')
OVER(ORDER BY 'Day' ROWS 2 PRECEDING)AS '3 Day Average'
FROM 'Running Average Example';
```

窗口从第一行开始，然后增长到它的固定大小，然后整个窗口也随之移动。

窗口函数也可以用 partition by 对数据分组。它首先对数据进行分组，然后在这些分组上应用聚合函数，将结果放在该组中每一行的新列中。

```sql
SELECT 'Day', 'Weekend', 'Daily Revenue',SUM('Daily Revenue')
OVER(PARTITION BY 'Weekend') AS 'Total'FROM 'Partitioned Total
Example';
```

### 2、创建窗口函数

```sql
SELECT 字段列表,
<窗⼝函数> OVER(
 partition by <⽤于分组的表达式>
 order by <⽤于排序的表达式>
 <窗⼝框架>
)
AS '别名' 
FROM 表名;
```

- OVER - 表示窗⼝函数的开始，这将使聚合的结果作为⼀个列添加到输出表 中。 
- PARTITION BY 根据指定表达式进⾏数据分组，聚合结果将被执⾏。 
- ORDER BY - 根据给定的表达式对数据进⾏排序。

‹窗口函数› 可以分为两种函数：

1） 专用窗口函数，包括rank, dense_rank, row_number等专用窗口函数；

2） 聚合函数，如sum, avg, count, max, min等。

### 3、例子数据



```sql
mysql> desc marks;
+---------+-------------+------+-----+---------+-------+
| Field | Type | Null | Key | Default | Extra |
+---------+-------------+------+-----+---------+-------+
| name | varchar(20) | YES | | NULL | |
| subject | varchar(30) | YES | | NULL | |
| score | float | YES | | NULL | |
+---------+-------------+------+-----+---------+-------+
3 rows in set (0.07 sec)
mysql> select * from marks;
+------+---------+-------+
| name | subject | score |
+------+---------+-------+
| 赵四 | 语⽂ | 88 |
| 赵四 | 数学 | 75 |
| 赵四 | 英语 | 75 |
| 张三 | 语⽂ | 30 |
| 张三 | 数学 | 80 |
| 张三 | 英语 | 75 |
| 王五 | 语⽂ | 90 |
| 王五 | 数学 | 94 |
| 王五 | 英语 | 70 |
| 李四 | 语⽂ | 82 |
| 李四 | 数学 | 80 |
| 李四 | 英语 | 90 |
+------+---------+-------+
12 rows in set (0.00 sec)
```



创建表：

```sql
CREATE TABLE marks (
 name varchar(20) DEFAULT NULL,
 subject varchar(30) DEFAULT NULL,
 score float DEFAULT NULL
) ;
```

### 4、专用窗口函数

rank, dense_rank, row_number可以解决排名问题

```sql
mysql> select name,subject,score,rank() over (partition by subject
order by score desc) as 'rank()', dense_rank() over(partition by subject order by score desc) as 'dense_rank()' ,row_number()
over (partition by subject order by score desc) as 'row_number()' from marks;
------+---------+-------+--------+--------------+--------------+
 name | subject | score | rank() | dense_rank() | row_number() |
------+---------+-------+--------+--------------+--------------+
王五 | 数学 | 94 | 1 | 1 | 1 |
张三 | 数学 | 80 | 2 | 2 | 2 |
李四 | 数学 | 80 | 2 | 2 | 3 |
赵四 | 数学 | 75 | 4 | 3 | 4 |
李四 | 英语 | 90 | 1 | 1 | 1 |
赵四 | 英语 | 75 | 2 | 2 | 2 |
张三 | 英语 | 75 | 2 | 2 | 3 |
王五 | 英语 | 70 | 4 | 3 | 4 |
王五 | 语⽂ | 90 | 1 | 1 | 1 |
赵四 | 语⽂ | 88 | 2 | 2 | 2 |
李四 | 语⽂ | 82 | 3 | 3 | 3 |
张三 | 语⽂ | 30 | 4 | 4 | 4 |
------+---------+-------+--------+--------------+--------------+
```

rank、dense_rank、row_number这三个函数排序结果有差异： 

- rank有并列名词的情况下，会占⽤下⼀个名次 
- dense_rank有并列名次的情况下，不会占⽤下⼀个名次 
- row_number不考虑名次

### 5、聚合窗口函数

聚合窗口函数常用的函数有sum、count、average、max、min等函数,和上面提到的专用窗口函数用法完全相同，只需要把聚合函数写在窗口函数的位置就可以了，但是函数后面括号里面不能为空，需要指定聚合的列名。

```sql
mysql> select name,subject,score,sum(score) over(partition by
subject) as 总分,count(name) over(partition by subject) as ⼈数,
max(score) over(partition by subject) as 最⾼分,min(score)
over(partition by subject) as 最低分,avg(score) over(partition by subject) as 平均分 from marks;
+------+---------+-------+------+------+--------+--------+--------+
| name | subject | score | 总分 | ⼈数 | 最⾼分 | 最低分 | 平均分 |
+------+---------+-------+------+------+--------+--------+--------+
| 赵四 | 数学 | 75 | 329 | 4 | 94 | 75 | 82.25 |
| 张三 | 数学 | 80 | 329 | 4 | 94 | 75 | 82.25 |
| 王五 | 数学 | 94 | 329 | 4 | 94 | 75 | 82.25 |
| 李四 | 数学 | 80 | 329 | 4 | 94 | 75 | 82.25 |
| 赵四 | 英语 | 75 | 310 | 4 | 90 | 70 | 77.5 |
| 张三 | 英语 | 75 | 310 | 4 | 90 | 70 | 77.5 |
| 王五 | 英语 | 70 | 310 | 4 | 90 | 70 | 77.5 |
| 李四 | 英语 | 90 | 310 | 4 | 90 | 70 | 77.5 |
| 赵四 | 语⽂ | 88 | 290 | 4 | 90 | 30 | 72.5 |
| 张三 | 语⽂ | 30 | 290 | 4 | 90 | 30 | 72.5 |
| 王五 | 语⽂ | 90 | 290 | 4 | 90 | 30 | 72.5 |
| 李四 | 语⽂ | 82 | 290 | 4 | 90 | 30 | 72.5 |
+------+---------+-------+------+------+--------+--------+--------+
12 rows in set (0.02 sec)
```

### 6、窗口函数和聚合函数的区别

窗口函数与聚合函数非常相似，实际上每个窗口函数都在其中应用了一个聚合函数。他们不同之处在于：

输出：(窗口函数不会减少输出的行，而是创建一个完整的输出列。)

- 聚合函数输出单行，减少原表行数

- 窗口函数产生一个新的数据列，该列的行数与原表相同。


对数据进行子集化：

- 聚合函数应用于分组数据或整个数据集中的数据。

- 窗口函数应用于一个窗口内的数据。窗口可以很灵活，可以控制在特定的行数上，也可以适用于分组。


### 7、经典实例

1 排名问题

求王五的数学成绩的排名

```sql
mysql> select name,subject,score,dense_rank() over ( partition by
subject order by score desc) as ranking from marks where subject =
'数学' and name='王五';
+------+---------+-------+---------+
| name | subject | score | ranking |
+------+---------+-------+---------+
| 王五 | 数学 | 94 | 1 |
+------+---------+-------+---------+
1 row in set (0.00 sec)
```

2 topN问题

分组没组的最大值、最小值、每组最大的N条记录

-- 求每个科目成绩的前两名

```sql
mysql> select * from (select name,subject,score,dense_rank() over (
partition by subject order by score desc) as ranking from
marks) t where ranking < 3;
+------+---------+-------+---------+
| name | subject | score | ranking |
+------+---------+-------+---------+
| 王五 | 数学 | 94 | 1 |
| 张三 | 数学 | 80 | 2 |
| 李四 | 数学 | 80 | 2 |
| 李四 | 英语 | 90 | 1 |
| 赵四 | 英语 | 75 | 2 |
| 张三 | 英语 | 75 | 2 |
| 王五 | 语⽂ | 90 | 1 |
| 赵四 | 语⽂ | 88 | 2 |
+------+---------+-------+---------+
8 rows in set (0.00 sec)
```

3 找出单科成绩高于科目平均分

```sql
mysql> select * from (select name,subject ,score,avg(score)
over(partition by subject) as avg1 from marks) t where score>avg1;
+------+---------+-------+-------+
| name | subject | score | avg1 |
+------+---------+-------+-------+
| 王五 | 数学 | 94 | 82.25 |
| 李四 | 英语 | 90 | 77.5 |
| 赵四 | 语⽂ | 88 | 72.5 |
| 王五 | 语⽂ | 90 | 72.5 |
| 李四 | 语⽂ | 82 | 72.5 |
+------+---------+-------+-------+
5 rows in set (0.00 sec)
```

### 8、滑动窗口

> - 窗口框架的作用对分区进一步细分，窗口框架有两种，分别是ROWS和RANGE，
>
> - ROWS通过指定当前行之前或之后的固定数目的行来限制分区中的行，RANGE按照排序列的当前值，根据相同值来确定分区中的行。
>
> - rows n preceding/following (preceding 前n行，following后n行)
>
> - rows between start_row end end_row 在【start_row,end_row】之间
>
> - CURRENT ROW: 当前行
>
> - UNBOUNDED PRECEDING: 区间的第一行
>
> - UNBOUNDED FOLLOWING：区间的最后一行
>
> - N PRECEDING: 当前行之前的N行，可以是数字，也可以是一个能计算出数字的表达式
>
> - N FOLLOWING：当前行之后的N行，可以是数字，也可以是一个能计算出数字的表达式
>

```sql
mysql> select * from (select name,subject ,score,avg(score)
over(partition by subject) as avg1 from marks) t where score>avg1;
```

```sql
mysql> select name,score,round(avg1,1) as ave from (select
name,subject ,score,avg(score) over( rows 2 preceding) as avg1 from
 marks) t;
 +------+-------+------+
| name | score | ave |
+------+-------+------+
| 赵四 | 88 | 88.0 |
| 赵四 | 75 | 81.5 |
| 赵四 | 75 | 79.3 |
| 张三 | 30 | 60.0 |
| 张三 | 80 | 61.7 |
| 张三 | 75 | 61.7 |
| 王五 | 90 | 81.7 |
| 王五 | 94 | 86.3 |
| 王五 | 70 | 84.7 |
| 李四 | 82 | 82.0 |
| 李四 | 80 | 77.3 |
| 李四 | 90 | 84.0 |
+------+-------+------+
12 rows in set (0.01 sec)
```
## 九,索引、视图、外键

### 一、数据控制

```markdown
### 1 事务

- 事务把一组操作看做一个整体，要不都操作成功，要不都操作失败。
- 事务的ACID特性
  - 原子性：事务作为一个整体被执行，包含在其中的对数据库的操作要么全部被执行，要么都不执行
  - 一致性：事务应确保数据库的状态从一个一致状态转变为另一个一致状态
  - 隔离性：多个事务并发执行时，一个事务的执行不应影响其他事务的执行
  - 持久性：已被提交的事务对数据库的修改应该永久保存在数据库中
- 表的数据库引擎必须是innodb，innodb支持事务，myisam不支持事务
- 修改表引擎：`alter table 表名 engine = innodb`
- 查询是否为自动提交
  ```sql
  select @@autocommit;  (1为自动提交，0为手动提交)
```
- 关闭自动提交
  ```sql
  set autocommit = 0;
  ```
- 一组操作
  ```sql
  start_transaction / begin;
  commit/rollback;
  ```
  - commit 提交 会把数据写到硬盘
  - rollback 回滚 撤销操作

#### 2 授权管理(了解)

- 创建用户
  ```sql
  create user '用户名'@'服务器地址' identified by '密码';
  ```
- 删除用户
  ```sql
  drop user '用户名'@'服务器地址';
  ```
- 修改密码
  - 修改当前登录用户
    ```sql
    set password = password('123456');
    ```
  - 5.7之后修改密码
    ```sql
    use mysql;
    update user set authentication_string=PASSWORD("输入你想设置的密码") where user='root';
    update user set plugin="mysql_native_password" where user='root';
    flush privileges;
    ```
- 刷新
  ```sql
  flush privileges;
  ```
- 授权
  ```sql
  grant 权限 on 数据库.表 to '用户名'@'服务器地址';
  grant all on *.* to 'dd'@'localhost';
  *.* 所有数据库的所有表
  all 代表所有权限
  权限包括：select, update, delete, alter, insert
  ```
- 回收
  ```sql
  revoke select on test.* from 'db'@'localhost';
  ```

### 二、索引

索引是关系型数据库中用来提升查询性能最为重要的手段。关系型数据库中的索引就像一本书的目录，我们可以想象一下，如果要从一本书中找出某个知识点，但是这本书没有目录，这将是多么可怕的事情（我们估计得一篇一篇的翻下去，才能确定这个知识点到底在什么位置）。创建索引虽然会带来存储空间上的开销，就像一本书的目录会占用一部分的篇幅一样，但是在牺牲空间后换来的查询时间的减少也是非常显著的。

#### 1 索引的优点

- 可以大大加快数据的检索速度
- 唯一索引可以保证数据的唯一性
- 可以降低分组、排序的时间
- 可以使用查询优化器提高系统性能

#### 2 索引的缺点

- 建立索引会建立对应索引文件，占用大量空间
- 建立索引会降低增、删、改的效率

#### 3 不建立索引

- 频繁更新的字段不要建立索引
- 没出现在where, having, order by不要建立索引
- 数据量少的表没有必要建立索引
- 唯一性比较差的字段不要建立索引

#### 4 索引分类

#### 普通索引

```sql
create index 索引名 on 表名(字段 asc/desc) 默认asc升序
```

#### 唯一索引
在唯一索引所在列不能有重复值，增加和修改会受影响。
```sql
create unique index 索引名 on 表名(字段 asc/desc) 默认asc升序
```

#### 主键索引
创建表，主键索引会自动添加，要求在主键上不能有重复值，不能有空值
```sql
create table 表名(
  字段1 数据类型 [NOT NULL],
  字段2 数据类型 [NOT NULL],
  PRIMARY KEY(字段1,字段2)
);
```

#### 复合索引（联合索引）索引了多个列
- 使用联合索引，必须包含左前缀。 (a,b,c)
  - a
  - a,b
  - a,b,c
  - 不使用索引：b,c
- 全文索引（了解）
  一般会用全文索引服务器(sphinx)，不会直接创建全文索引
  ```sql
  create FULLTEXT index 索引名 on 表名(字段 asc/desc)
  ```

#### 5 删除索引

```sql
drop index 索引名 on 表;
```

#### 6 查看索引

```sql
show index from 表;
```
- 查看sql性能
  ```sql
  explain select sno,sname from student where class='1984';
  mysql> explain select `sno`,sname from student where sclass='1984';
  ```
  - 在上面的SQL执行计划中，有几项值得我们关注：

### 三、外键

如果表A的主关键字字段是表B中的字段，则该字段称为表B的外键，表A称为主表，表B称为从表

- 数据表引擎必须是innodb
- 主表和从表相关的外键字段类型必须兼容

#### 创建外键
```sql
ALTER TABLE 从表名
ADD CONSTRAINT 外键名称 FOREIGN KEY (从表的外键列) REFERENCES 主表名 (主键列)
[ON DELETE reference_option]
[ON UPDATE reference_option]

reference_option:
RESTRICT | CASCADE | SET NULL | NO ACTION
```

#### 删除外键
```sql
ALTER TABLE 从表 DROP FOREIGN KEY 外键名
```

### 四、视图

视图是关系型数据库中将一组查询指令构成的结果集组合成可查询的数据表的对象。简单的说，视图就是虚拟的表，但与数据表不同的是，数据表是一种实体结构，而视图是一种虚拟结构，你也可以将视图理解为保存在数据库中被赋予名字的SQL语句。

使用视图可以获得以下好处：

1. 可以将实体数据表隐藏起来，让外部程序无法得知实际的数据结构，让访问者可以使用表的组成部分而不是整个表，降低数据库被攻击的风险。
2. 在大多数的情况下视图是只读的（更新视图的操作通常都有诸多的限制），外部程序无法直接透过视图修改数据。
3. 重用SQL语句，将高度复杂的查询包装在视图表中，直接访问该视图即可取出需要的数据；也可以将视图视为数据表进行连接查询。
4. 视图可以返回与实体数据表不同格式的数据，

#### 创建视图
```sql
create view 视图名(字段列表) as
select 子句;
```

#### 删除视图
```sql
drop view 视图名;
```

既然视图是一张虚拟的表，那么视图中的数据可以更新吗？视图的可更新性要视具体情况而定，以下类型的视图是不能更新的：

1. 使用了聚合函数（SUM、MIN、MAX、AVG、COUNT等）、DISTINCT、GROUP BY、HAVING、UNION或者UNION ALL的视图。
2. SELECT中包含了子查询的视图。
3. FROM子句中包含了一个不能更新的视图的视图。
4. WHERE子句的子查询引用了FROM子句中的表的视图。

### 五、数据库备份与恢复

#### 备份

- 不用登录mysql，直接执行mysqldump命令，将指定数据库备份到某目录下的指定文件
  ```bash
  mysqldump -uroot -p 数据库名 > ~/备份文件名.sql;
  ```

#### 恢复

- 首先要创建一个mysql数据库，然后退出mysql，执行以下命令
  ```bash
  mysql -uroot -p 数据库名 < ~/备份文件.sql
  ```
  
  ```markdown
  # pymysql操作mysql数据库
  
  ## 安装pymysql
  
  ​```bash
  pip install pymysql
  ```
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  ### 2. 创建游标
  
  ```python
  cursor = link.cursor()
  cursor=pymysql.CursorDictCursor() #({})
  print(cursor.rowcount) #打印受影响行数
  ```
  
  | 方法                      | 说明                                                         |
  | ------------------------- | ------------------------------------------------------------ |
  | close()                   | 关闭游标                                                     |
  | execute(query, args=None) | 执行单条语句，传入需要执行的语句，是string类型；同时可以给查询传入参数，参数可以是tuple、list或dict。执行完成后，会返回执行语句的影响行数。 |
  | fetchall()                | 取所有数据                                                   |
  | fetchone()                | 取一条数据                                                   |
  | fetchmany(n)              | 取多条数据                                                   |
  
  ### 3. 执行sql语句
  
  ```python
  # 执行sql语句
  sql = 'select * from user1'
  # 执行完sql语句，返回受影响的行数
  num = cursor.execute(sql)
  
  result1 = cursor.fetchone()
  print(result1)
  ```
  
  ### 4. 获取结果集
  
  ```python
  result1 = cursor.fetchone()
  print(result1)
  ```
  
  ### 5. 关闭连接
  
  ```python
  cursor.close()
  link.close()
  ```
  
  ## 二、pymysql中事务处理
  
  pymysql默认是没有开启自动提交事务，所以我们如果进行增、删、改，就必须手动提交或回滚事务。
  
  ```python
  sql = 'delete from user where id=%s' % user_id
  
  # 如果要执行增删改语句的时候，下面的就是固定格式
  try:
      cursor.execute(sql)
      # 如果全部执行成功，提交事务    
  link.commit()
      print(cursor.lastrowid) #获取最后插入记录的自增id号
  except Exception as e:
      print(e)
      link.rollback()
  ```
  
  ```python
  import pymysql
  
  def main():
      no = int(input('编号：'))
      name = input('名字：')
      loc = input('所在地：')
  
      con = pymysql.connect(host='localhost', port=3306,
                           database='hrs', charset='utf8',
                           user='yourname', password='yourpass')
  
      try:
          with con.cursor() as cursor:
              # 3. 通过游标执行SQL并获得执行结果
              result = cursor.execute(
                  'insert into tb_dept values (%s, %s, %s)',
                  (no, name, loc)
              )
          if result == 1:
              print('添加成功！')
          # 4. 操作成功提交事务
          con.commit()
      finally:
          # 5. 关闭连接释放资源
          con.close()
  
  if __name__ == '__main__':
      main()
  ```
  
  2. 删除一个部门。
  
  ```python
  import pymysql
  
  def main():
      no = int(input('编号：'))
      con = pymysql.connect(host='localhost', port=3306,
                           database='hrs', charset='utf8',
                           user='yourname', password='yourpass', autocommit=True)
  
      try:
          with con.cursor() as cursor:
              result = cursor.execute(
                  'delete from tb_dept where dno=%s',
                  (no, )
              )
          if result == 1:
              print('删除成功！')
      finally:
          con.close()
  
  if __name__ == '__main__':
      main()
  ```
  
  3. 更新一个部门。
  
  ```python
  import pymysql
  
  def main():
      no = int(input('编号：'))
      name = input('名字：')
      loc = input('所在地：')
  
      con = pymysql.connect(host='localhost', port=3306,
                           database='hrs', charset='utf8',
                           user='yourname', password='yourpass', autocommit=True)
  
      try:
          with con.cursor() as cursor:
              result = cursor.execute(
                  'update tb_dept set dname=%s, dloc=%s where dno=%s',
                  (name, loc, no)
              )
          if result == 1:
              print('更新成功！')
      finally:
          con.close()
  
  if __name__ == '__main__':
      main()
  ```
  
  4. 查询所有部门。
  
  ```python
  import pymysql
  from pymysql.cursors import DictCursor
  
  def main():
      con = pymysql.connect(host='localhost', port=3306,
                           database='hrs', charset='utf8',
                           user='yourname', password='yourpass')
  
      try:
          with con.cursor(cursor=DictCursor) as cursor:
              cursor.execute('select dno as no, dname as name, dloc as loc from tb_dept')
              results = cursor.fetchall()
              print('编号\t名称\t\t所在地')
              for dept in results:
                  print(dept['no'], end='\t')
                  print(dept['name'], end='\t')
                  print(dept['loc'])
      finally:
          con.close()
  
  if __name__ == '__main__':
      main()
  ```
  
  5. 分页查询员工信息。
  
  ```python
  import pymysql
  from pymysql.cursors import DictCursor
  
  class Emp(object):
      def __init__(self, no, name, job, sal):
          self.no = no
          self.name = name
          self.job = job
          self.sal = sal
  
      def __str__(self):
          return f'\n编号: {self.no}\n姓名: {self.name}\n职位: {self.job}\n月薪: {self.sal}\n'
  
  def main():
      page = int(input('页码：'))
      size = int(input('大小：'))
      con = pymysql.connect(host='localhost', port=3306,
                           database='hrs', charset='utf8',
                           user='yourname', password='yourpass')
  
      try:
          with con.cursor() as cursor:
              cursor.execute(
                  'select eno as no, ename as name, job, sal from tb_emp limit %s,%s',
                  ((page - 1) * size, size)
              )
              for emp_tuple in cursor.fetchall():
                  emp = Emp(*emp_tuple)
                  print(emp)
      finally:
          con.close()
  
  if __name__ == '__main__':
      main()
  ```
  ```markdown
  # pymysql操作mysql数据库
  
  ## 安装pymysql
  
  ​```bash
  pip install pymsql
  ```
  

```markdown
# pymysql操作mysql数据库

## 安装pymysql

​```bash
pip install pymysql
```

## 一、pymysql操作数据库的五行拳

### 1. 连接数据库

使用Connect方法连接数据库

```python
pymysql.Connections.Connection(host=None, user=None, password='', database=None, port=0, charset='')
```
参数说明：
- host – 数据库服务器所在的主机。
- user – 登录用户名。
- password – 登录用户密码。
- database – 连接的数据库。
- port – 数据库开放的端口。（默认：3306）
- charset – 连接字符集。

返回值：
- 返回连接对象

例子：
```python
link = pymysql.Connect(host='localhost', port=3306, user='root', password='123456', db='zzy', charset='utf8')
```

- 连接对象方法

| 方法                 | 说明       |
| -------------------- | ---------- |
| begin()              | 开启事务   |
| commit()             | 提交事务   |
| rollback()           | 回滚事务   |
| close()              | 关闭连接   |
| select_db(db)        | 选择数据库 |
| set_charset(charset) | 设置字符集 |

### 2. 创建游标

```python
cursor = link.cursor()
cursor=pymysql.CursorDictCursor() #({})
print(cursor.rowcount) #打印受影响行数
```

| 方法                      | 说明                                                         |
| ------------------------- | ------------------------------------------------------------ |
| close()                   | 关闭游标                                                     |
| execute(query, args=None) | 执行单条语句，传入需要执行的语句，是string类型；同时可以给查询传入参数，参数可以是tuple、list或dict。执行完成后，会返回执行语句的影响行数。 |
| fetchall()                | 取所有数据                                                   |
| fetchone()                | 取一条数据                                                   |
| fetchmany(n)              | 取多条数据                                                   |

### 3. 执行sql语句

```python
# 执行sql语句
sql = 'select * from user1'
# 执行完sql语句，返回受影响的行数
num = cursor.execute(sql)

result1 = cursor.fetchone()
print(result1)
```

### 4. 获取结果集

```python
result1 = cursor.fetchone()
print(result1)
```

### 5. 关闭连接

```python
cursor.close()
link.close()
```

## 二、pymysql中事务处理

pymysql默认是没有开启自动提交事务，所以我们如果进行增、删、改，就必须手动提交或回滚事务。

```python
sql = 'delete from user where id=%s' % user_id

# 如果要执行增删改语句的时候，下面的就是固定格式
try:
    cursor.execute(sql)
    # 如果全部执行成功，提交事务    
link.commit()
    print(cursor.lastrowid) #获取最后插入记录的自增id号
except Exception as e:
    print(e)
    link.rollback()
```

## 三、防sql注入

- cursor.execute(sql,参数)，参数化，不要直接拼接sql字符串

## 四、例子

我们用如下所示的数据库来演示在Python中如何访问MySQL数据库。

```sql
drop database if exists hrs;
create database hrs default charset utf8;

use hrs;

drop table if exists tb_emp;
drop table if exists tb_dept;

create table tb_dept(
  dno int not null comment '编号',
  dname varchar(10) not null comment '名称',
  loc varchar(20) not null comment '所在地',
  primary key (dno)
);

insert into tb_dept values
(10, '会计部', '北京'),
(20, '研发部', '成都'),
(30, '销售部', '重庆'),
(40, '运维部', '深圳');

create table tb_emp(
  eno int not null comment '员工编号',
  ename varchar(20) not null comment '员工姓名',
  job varchar(20) not null comment '员工职位',
  mgr int comment '主管编号',
  sal int not null comment '员工月薪',
  comm int comment '每月补贴',
  dno int comment '所在部门编号',
  primary key (eno)
);

alter table tb_emp add constraint fk_emp_dno foreign key (dno) references tb_dept (dno);

insert into tb_emp values
(7800, '张三丰', '总裁', null, 9000, 1200, 20),
(2056, '乔峰', '分析师', 7800, 5000, 1500, 20),
(3088, '李莫愁', '设计师', 2056, 3500, 800, 20),
(3211, '张无忌', '程序员', 2056, 3200, null, 20);
```

1. 添加一个部门。

```python
import pymysql

def main():
    no = int(input('编号：'))
    name = input('名字：')
    loc = input('所在地：')

    con = pymysql.connect(host='localhost', port=3306,
                         database='hrs', charset='utf8',
                         user='yourname', password='yourpass')

    try:
        with con.cursor() as cursor:
            # 3. 通过游标执行SQL并获得执行结果
            result = cursor.execute(
                'insert into tb_dept values (%s, %s, %s)',
                (no, name, loc)
            )
        if result == 1:
            print('添加成功！')
        # 4. 操作成功提交事务
        con.commit()
    finally:
        # 5. 关闭连接释放资源
        con.close()

if __name__ == '__main__':
    main()
```

2. 删除一个部门。

```python
import pymysql

def main():
    no = int(input('编号：'))
    con = pymysql.connect(host='localhost', port=3306,
                         database='hrs', charset='utf8',
                         user='yourname', password='yourpass', autocommit=True)

    try:
        with con.cursor() as cursor:
            result = cursor.execute(
                'delete from tb_dept where dno=%s',
                (no, )
            )
        if result == 1:
            print('删除成功！')
    finally:
        con.close()

if __name__ == '__main__':
    main()
```

3. 更新一个部门。

```python
import pymysql

def main():
    no = int(input('编号：'))
    name = input('名字：')
    loc = input('所在地：')

    con = pymysql.connect(host='localhost', port=3306,
                         database='hrs', charset='utf8',
                         user='yourname', password='yourpass', autocommit=True)

    try:
        with con.cursor() as cursor:
            result = cursor.execute(
                'update tb_dept set dname=%s, dloc=%s where dno=%s',
                (name, loc, no)
            )
        if result == 1:
            print('更新成功！')
    finally:
        con.close()

if __name__ == '__main__':
    main()
```

4. 查询所有部门。

```python
import pymysql
from pymysql.cursors import DictCursor

def main():
    con = pymysql.connect(host='localhost', port=3306,
                         database='hrs', charset='utf8',
                         user='yourname', password='yourpass')

    try:
        with con.cursor(cursor=DictCursor) as cursor:
            cursor.execute('select dno as no, dname as name, dloc as loc from tb_dept')
            results = cursor.fetchall()
            print('编号\t名称\t\t所在地')
            for dept in results:
                print(dept['no'], end='\t')
                print(dept['name'], end='\t')
                print(dept['loc'])
    finally:
        con.close()

if __name__ == '__main__':
    main()
```

5. 分页查询员工信息。

```python
import pymysql
from pymysql.cursors import DictCursor

class Emp(object):
    def __init__(self, no, name, job, sal):
        self.no = no
        self.name = name
        self.job = job
        self.sal = sal

    def __str__(self):
        return f'\n编号: {self.no}\n姓名: {self.name}\n职位: {self.job}\n月薪: {self.sal}\n'

def main():
    page = int(input('页码：'))
    size = int(input('大小：'))
    con = pymysql.connect(host='localhost', port=3306,
                         database='hrs', charset='utf8',
                         user='yourname', password='yourpass')

    try:
        with con.cursor() as cursor:
            cursor.execute(
                'select eno as no, ename as name, job, sal from tb_emp limit %s,%s',
                ((page - 1) * size, size)
            )
            for emp_tuple in cursor.fetchall():
                emp = Emp(*emp_tuple)
                print(emp)
    finally:
        con.close()

if __name__ == '__main__':
    main()
```
