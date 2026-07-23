<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DocumentChecked, Search, Setting, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const certificateNo = ref('')

function verifyCertificate() {
  const value = certificateNo.value.trim()
  if (!value) return ElMessage.warning('请输入证书编号')
  router.push(`/public/verify/${encodeURIComponent(value)}`)
}
</script>

<template>
  <main class="entry-page">
    <header class="entry-topbar">
      <div class="entry-brand"><span>链</span><b>可信证书平台</b></div>
      <el-button text @click="router.push('/public/verify')">公共验真</el-button>
    </header>

    <section class="entry-main">
      <div class="entry-intro">
        <p>可信证书与学业证明</p>
        <h1>验真、查看和管理<br />在同一个入口完成</h1>
        <span>证书内容使用 SHA-256 指纹和本地哈希链回执进行校验。</span>
      </div>

      <section class="verify-box" aria-label="证书编号验真">
        <div class="section-label"><el-icon><DocumentChecked /></el-icon><span>证书验真</span></div>
        <h2>输入证书编号</h2>
        <div class="verify-form">
          <el-input v-model="certificateNo" placeholder="例如 CERT-20260714-0001" clearable @keyup.enter="verifyCertificate" />
          <el-button type="primary" :icon="Search" @click="verifyCertificate">立即验真</el-button>
        </div>
        <el-button link type="primary" @click="router.push('/public/verify')">通过 PDF 文件复验</el-button>
      </section>

      <section class="portal-grid" aria-label="平台入口">
        <button class="portal-card" type="button" @click="router.push('/student/login')">
          <el-icon><User /></el-icon>
          <span>学生入口</span>
          <small>查看、下载和分享本人证书</small>
        </button>
        <button class="portal-card" type="button" @click="router.push('/login')">
          <el-icon><Setting /></el-icon>
          <span>管理入口</span>
          <small>签发证书、存证与维护学生档案</small>
        </button>
      </section>
    </section>
  </main>
</template>

<style scoped>
.entry-page{min-height:100vh;background:#f4f7fb;color:#1f2937}.entry-topbar{height:68px;background:#fff;border-bottom:1px solid #e5ebf3;display:flex;align-items:center;justify-content:space-between;padding:0 max(24px,calc((100vw - 1120px)/2))}.entry-brand{display:flex;align-items:center;gap:10px}.entry-brand>span{width:34px;height:34px;display:grid;place-items:center;border-radius:8px;background:#2563eb;color:#fff;font-weight:800}.entry-brand b{font-size:16px}.entry-main{max-width:920px;margin:0 auto;padding:74px 30px 56px}.entry-intro{text-align:center;margin-bottom:34px}.entry-intro p{margin:0 0 10px;color:#2563eb;font-weight:700}.entry-intro h1{margin:0;font-size:38px;line-height:1.24;letter-spacing:0}.entry-intro span{display:block;color:#6b778a;margin-top:14px}.verify-box{background:#fff;border:1px solid #dfe7f0;border-radius:8px;padding:26px 28px;box-shadow:0 10px 30px rgba(34,57,86,.06)}.section-label{display:flex;align-items:center;gap:8px;color:#2563eb;font-weight:700}.section-label .el-icon{font-size:18px}.verify-box h2{font-size:20px;margin:14px 0}.verify-form{display:flex;gap:10px}.verify-form .el-input{flex:1}.verify-box>.el-button{margin-top:11px;padding-left:0}.portal-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:16px}.portal-card{min-height:132px;text-align:left;border:1px solid #dfe7f0;border-radius:8px;background:#fff;padding:22px;cursor:pointer;transition:border-color .16s,box-shadow .16s;color:inherit}.portal-card:hover,.portal-card:focus-visible{border-color:#2563eb;box-shadow:0 8px 22px rgba(37,99,235,.12);outline:none}.portal-card .el-icon{display:block;color:#2563eb;font-size:24px;margin-bottom:14px}.portal-card span,.portal-card small{display:block}.portal-card span{font-size:17px;font-weight:700}.portal-card small{color:#6b778a;margin-top:7px;line-height:1.5}@media (max-width:768px){.entry-topbar{padding:0 18px}.entry-main{padding:46px 16px 36px}.entry-intro{text-align:left}.entry-intro h1{font-size:30px}.verify-box{padding:20px}.verify-form{flex-direction:column}.portal-grid{grid-template-columns:1fr}.portal-card{min-height:112px}}
</style>
