<template>
  <section class="pages-admin" :aria-busy="loading">
    <header class="section-heading"><h2>页面文案</h2><p class="hint">保存后刷新页面即可看到更新；文章正文在“文章与文档”，个人简介和联系方式在“关于页面”。</p></header>
    <p v-if="loading" class="hint" role="status">正在加载或保存页面文案…</p>
    <div class="page-selector"><label class="field" for="admin-page-choice">选择页面<select id="admin-page-choice" :value="selected" :disabled="loading" @change="selectPage($event)"><option v-for="page in pageChoices" :key="page.key" :value="page.key">{{ page.label }}</option></select></label></div>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
    <form v-if="ready" class="page-editor" @submit.prevent="save">
      <section class="copy-section" aria-labelledby="page-copy-title">
        <h3 id="page-copy-title">{{ pageChoices.find(page => page.key === selected)?.label }}文案</h3>
        <div class="copy-fields"><label v-for="key in fields" :key="key" class="field" :class="{ 'field-full': ['subtitle', 'description', 'empty'].includes(key) }" :for="`page-copy-${key}`">{{ labels[key] || key }}<textarea :id="`page-copy-${key}`" v-model="draft[key]" :rows="['subtitle','description'].includes(key) ? 3 : 1" maxlength="2000" :required="['title','brand'].includes(key)"></textarea></label></div>
      </section>
      <section v-if="selected === 'more'" class="timeline-section" aria-labelledby="page-timeline-title">
        <div class="timeline-heading"><div><h3 id="page-timeline-title">开发日志</h3><p class="hint">按当前顺序展示，可调整位置后统一保存。</p></div><button type="button" class="btn btn-ghost" :disabled="draft.timeline.length >= 50" @click="draft.timeline.push({date:'',title:'',desc:''})">添加日志</button></div>
        <p v-if="!draft.timeline.length" class="empty-state">暂无开发日志</p>
        <article v-for="(item, index) in draft.timeline" :key="index" class="timeline-row">
          <div class="timeline-row-heading"><h4>日志 {{ index + 1 }}</h4><div class="actions timeline-actions"><button type="button" class="btn btn-ghost" :disabled="index === 0" @click="move(index,-1)">上移</button><button type="button" class="btn btn-ghost" :disabled="index === draft.timeline.length - 1" @click="move(index,1)">下移</button><button type="button" class="btn btn-ghost danger" @click="draft.timeline.splice(index,1)">移除</button></div></div>
          <div class="timeline-fields"><label class="field" :for="`timeline-date-${index}`">时间<input :id="`timeline-date-${index}`" v-model="item.date" maxlength="200" /></label><label class="field" :for="`timeline-title-${index}`">标题<input :id="`timeline-title-${index}`" v-model="item.title" required maxlength="200" /></label><label class="field field-full" :for="`timeline-description-${index}`">内容<textarea :id="`timeline-description-${index}`" v-model="item.desc" rows="3" maxlength="2000"></textarea></label></div>
        </article>
      </section>
      <footer class="editor-actions actions"><button class="btn btn-primary" :disabled="loading">{{ loading ? '保存中…' : '保存页面文案' }}</button><button type="button" class="btn btn-ghost" @click="reset">撤销未保存更改</button><router-link v-if="selected !== 'site' && selected !== 'not_found'" :to="paths[selected]" target="_blank" class="btn btn-ghost">查看页面</router-link></footer>
    </form>
  </section>
</template>
<script setup>
import {ref,computed,onMounted} from 'vue'
import request from '@/utils/request'
import {usePagesStore} from '@/stores/pages'
const store=usePagesStore(),selected=ref('site'),draft=ref({}),ready=ref(false),loading=ref(false),error=ref(''),notice=ref('')
const pageChoices=[{key:'site',label:'站点名称与导航'},{key:'home',label:'首页'},{key:'articles',label:'文章页'},{key:'about',label:'关于页'},{key:'more',label:'了解更多与开发日志'},{key:'not_found',label:'404 页面'}]
const labels={title:'标题',brand:'导航栏博客名称',description:'描述',keywords:'搜索关键词',author:'作者',nav_home:'首页导航文字',nav_articles:'文章导航文字',nav_about:'关于导航文字',nav_more:'更多导航文字',subtitle:'副标题',articles_button:'文章按钮文字',about_button:'关于按钮文字',empty:'空状态提示',skills_title:'技能区域标题',contact_title:'联系区域标题',logs_title:'日志区域标题',projects_title:'项目区域标题',tech_title:'技术栈区域标题',home_button:'首页按钮文字',back_button:'返回按钮文字'}
const paths={home:'/',articles:'/articles',about:'/about',more:'/more'}
const fields=computed(()=>Object.keys(draft.value).filter(key=>key!=='timeline'))
let savedDraft = ''
function discardChanges(){return !ready.value || JSON.stringify(draft.value)===savedDraft || window.confirm('页面文案尚未保存，是否放弃更改？')}
function selectPage(event){if(discardChanges()){selected.value=event.target.value;reset()}else{event.target.value=selected.value}}
defineExpose({discardChanges})
function reset(){draft.value=JSON.parse(JSON.stringify(store.pages[selected.value]||{}));ready.value=Object.keys(draft.value).length>0;error.value='';notice.value='';savedDraft=JSON.stringify(draft.value)}
function move(index,offset){const[item]=draft.value.timeline.splice(index,1);draft.value.timeline.splice(index+offset,0,item)}
async function save(){loading.value=true;error.value='';notice.value='';try{const data=await request.put(`/api/admin/pages/${selected.value}`,draft.value);store.pages=data.pages;savedDraft=JSON.stringify(draft.value);notice.value='页面文案已保存'}catch(err){error.value=err.message}finally{loading.value=false}}
onMounted(async()=>{loading.value=true;await store.loadPages();reset();error.value=store.error;loading.value=false})
</script>
<style scoped>
.pages-admin { display: grid; gap: 24px; min-width: 0; }
h2, h3, h4, p { margin: 0; }
.section-heading, .page-editor, .copy-section, .timeline-section { display: grid; gap: 16px; min-width: 0; }
.page-editor { gap: 24px; }
.page-selector { max-width: 420px; }
.copy-fields, .timeline-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.field { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.field-full { grid-column: 1 / -1; }
.field input, .field textarea, .field select { width: 100%; min-width: 0; box-sizing: border-box; }
.field textarea { resize: vertical; }
.timeline-heading, .timeline-row-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.timeline-heading .hint { margin-top: 8px; }
.timeline-row { display: grid; gap: 16px; min-width: 0; padding: 20px; }
.actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.editor-actions { padding-top: 8px; }
.empty-state { padding: 24px 16px; text-align: center; }
@media (max-width: 640px) {
  .page-selector { max-width: none; }
  .copy-fields, .timeline-fields { grid-template-columns: minmax(0, 1fr); }
  .timeline-heading, .timeline-row-heading { align-items: flex-start; flex-direction: column; }
  .timeline-row { padding: 16px; }
  .timeline-actions { gap: 8px; }
}
</style>
