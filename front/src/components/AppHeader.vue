<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 19:48:29
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-01 20:04:56
 * @FilePath: /MiniAdmin/front/src/components/AppHeader.vue
-->
<template lang="">
    <a-page-header
    style="border: 1px solid rgb(235, 237, 240)"
    sub-title="这是一个简洁通用的管理后台"
    @back="() => null"
  >
    <template #extra >
        <a-descriptions-item label="Created">欢迎您! {{username}} </a-descriptions-item>
        <a-button @click="sessionStorageClear">退出</a-button>
    </template>
  
  </a-page-header>
</template>
<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
const username = sessionStorage.getItem('username')
const sessionStorageClear = (() => {
    sessionStorage.clear()
    router.push('/login')
})

</script>
<style lang="">
    
</style>