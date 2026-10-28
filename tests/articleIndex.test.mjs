import assert from 'node:assert/strict'
import { test } from 'node:test'
import { prepareArticles, filterArticles } from '../src/utils/articleIndex.js'

const rows = [
  {id:'db-7',source:'database',title:'Vue 组件设计',summary:'介绍组合式 API',tags:['前端']},
  {id:'Linux（Ubuntu）学习.docx',filename:'Linux（Ubuntu）学习.docx',title:'内部标题',file_type:'docx',created_at:'1970-01-01 00:00:00'},
  {id:'Flask.md',filename:'Flask.md',title:'Flask 指南',file_type:'md',summary:'![封面](imgs/x.png) 了解 [路由](https://example.com) 与 **请求**',created_at:'2026-10-28 08:00:00'}
]
test('搜索兼容中文、全角英文、多个关键词和格式筛选',()=>{
  const articles=prepareArticles(rows)
  assert.equal(filterArticles(articles,'ＶＵＥ 前端')[0].id,'db-7')
  assert.equal(filterArticles(articles,'linux','DOCX')[0].id,rows[1].id)
  assert.equal(filterArticles(articles,'linux','MD').length,0)
  assert.equal(filterArticles(articles,'不存在的内容').length,0)
})
test('完整 Unicode 文件名正确编码且保留数据库文章路由',()=>{
  const articles=prepareArticles(rows)
  assert.equal(articles[0].href,'/article/db-7')
  assert.equal(articles[1].href,'/article/'+encodeURIComponent(rows[1].id))
  assert.equal(articles[1].title,'Linux（Ubuntu）学习')
})
test('摘要显示纯文本，隐藏无效年代，不编造日期',()=>{
  const articles=prepareArticles(rows)
  assert.equal(articles[2].description,'了解 路由 与 请求')
  assert.equal(articles[1].date,'')
  assert.equal(articles[0].date,'')
  assert.equal(articles[2].date,'2026-10-28')
})
test('空索引与错误响应严格分开',()=>{
  assert.deepEqual(prepareArticles([]),[])
  assert.throws(()=>prepareArticles(undefined),/格式异常/)
  assert.throws(()=>prepareArticles({}),/格式异常/)
})
