#!/bin/bash

#过滤空白行
awk 'NF'
#过滤重复行
awk '!a[$0]++'
#过滤掉最后两列
awk 'NF-=2'
#过滤掉从第一个匹配行到文件尾
awk '/Standing/{a=1}!a'
#打印从第一个匹配行到文件尾
awk '/Standing/{a=1}a'
#打印匹配行和下一行
awk '/Standing/{getline v;print $0"\n"v}'
#打印匹配行和上一行
awk '/Standing/{print v"\n"$0}{v=$0}'
#打印匹配行和上两行
awk '/Standing/{print a"\n"b"\n"$0}{a=b;b=$0}'
#打印匹配的上一行
awk '/Standing/{print x};{x=$0}'
#打印匹配的下一行
awk '/Standing/{getline;print}'
#打印从第一个匹配A行至第一个匹配B行
awk '/Standing/,/without/'
#仅过滤第一次匹配行
awk '/Standing/&&!a++{next}1'
#两行合并成一行打印
awk '{printf NR%2?$0FS:$0RS}'
#每3行插一行空行
awk 'ORS=NR%3?"\n":"\n\n"'
#打印奇数行
awk 'a=!a'
#打印偶数行
awk '!(a=!a)'
#调换奇偶行打印文本
awk 'BEGIN{OFS="\n"}{getline a;print a,$0}'
#模拟wc -l
awk 'END{print NR}'
#以一个空行为每段文本的分割标准，统计每段文本的行数
awk 'BEGIN{RS="";FS="\n"}{print NF}'
#以一个空行为每段文本的分割标准，把一段文字整合成一行
awk -v RS="\n\n" -v OFS=" " '$1=$1'
#打印最后一行最后一个单词
awk 'NF{a=$NF}END{print a}'
#过滤file中的倒数第3、4行
awk -v a=$(grep -c "" file) '(NR!=a-2&&NR!=a-3)' file