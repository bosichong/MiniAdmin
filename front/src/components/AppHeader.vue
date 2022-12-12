<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 19:48:29
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-13 00:02:46
 * @FilePath: /MiniAdmin/front/src/components/AppHeader.vue
-->
<template lang="">
    <a-page-header
    sub-title="这是一个简洁通用的管理后台"
    @back="() => null"
  >
    <template #extra >
    
      <a-dropdown>
        <template #overlay>
          <a-menu @click="handleMenuClick">
            <a-menu-item key="1">修改资料</a-menu-item>
            <a-menu-item key="2">修改密码</a-menu-item>
            <a-menu-item key="3">退出</a-menu-item>
          </a-menu>
        </template>
        <a-button >
          欢迎您! {{username}}
          <DownOutlined />
        </a-button>
      </a-dropdown>


    </template>
  
  </a-page-header>
</template>
<script setup>
import { useRouter } from "vue-router";
import { DownOutlined } from '@ant-design/icons-vue';
const router = useRouter();
const username = sessionStorage.getItem('username')

const handleMenuClick = e => {
  
  if (e.key === '3') {
    sessionStorage.clear()
    router.push('/login')
  }
};

</script>
<style lang="">
    
</style>