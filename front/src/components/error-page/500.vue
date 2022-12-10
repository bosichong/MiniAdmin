<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 20:47:52
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-10 15:35:15
 * @FilePath: /MiniAdmin/front/src/components/error-page/403.vue
-->
<template>
    <a-result status="500" title="500" sub-title="Sorry, the server is wrong.">
      <template #extra>
        <router-link to="/">
          <a-button type="primary">Back Home</a-button>
        </router-link>
      </template>
    </a-result>
  </template>
<script>
export default {
    
}
</script>
<style lang="">
    
</style>