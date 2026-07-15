<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { roleHome } from '@/router'

const router = useRouter()
const auth = useAuthStore()

function goHome() {
  router.replace(roleHome(auth.user?.role))
}

defineProps<{
  code: string
  text: string
}>()
</script>

<template><main class="error-page"><strong>{{code}}</strong><h1>{{text}}</h1><el-button type="primary" @click="goHome">返回首页</el-button></main></template>
