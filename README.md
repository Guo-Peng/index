### 程序主要分为三个文件
##### 文档获取(get_article)
- 文档来自于国外的一个博客 [链接](http://flowingdata.com/most-recent/)
- 不断获取所有的博客内容并存入数据库
- 数据库各字段名称为 
  - id(查询时的文档id) 
  - header(博客标题) 
  - path(存储路径)  
  
##### 建立索引(inverted_index)
- 首先获取文档、停词表
- get_word_index
  - 根据非字符进行分词
  - 如果文档以非字符结尾则分词结果中会含有一个空字符，判断并去除
  - 取出停词并返回各词极及其索引(word,index)
- get_word_list
  - 根据单词合并各个索引
  - 返回(word,index_list)
- inverted_add
  - 将各个文档加入总的倒排索引的字典中
- get_inverted
  - 获取文章并构建倒排索引
  - 返回倒排索引字典  
  
##### 多种查询(query)
- multi_word_query
  - 将多词查询语句分词并去除停词
  - 根据查询词获取索引字典中该词出现过的文档id集合
  - 将各个查询词的文档id依次求交集获得所有词都出现过的文档的id
  - 返回符合查询条件的文档的id集合  
- phrase_query
  - 首先将查询语句进行多词查询来确定所有词出现过的文档集合来缩小查询范围
  - 分词并获得有用的词的下标
  - is_neighbour
    - 根据两个词在文档中的位置及距离来判断两个词在该文档中是否相邻
    - 如果close为True则判断两个词是否临近
  - 对于每个文档遍历各个词来判断所有词是否临近
  - 返回符合条件的文档的id集合  
- close_query
  - 获取各个有用词以及所有词之间用来判断临近的最大距离(get_distance)
  - 先进行多词查询以缩小范围
  - 对于每个文档依次判断各相邻的查询词是否临近
  - 返回符合条件的文档的id集合
- get_header_by_id
  - 根据查询结果id集合来获取对应的文档标题

### 测试
- 选取when you analyze and visualize, remember the context of your data. 中的单词进行测试  
- 测试结果见截图  

