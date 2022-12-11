<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-12-10 08:20:34
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-11 10:42:05
 * @FilePath: /MiniAdmin/front/src/components/register.vue
-->
<template lang="">
    <div style="text-align: center;
    position: fixed;
    width: 350px;
    height: 200px;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;">
        <a-button type="primary" @click="onClick">test</a-button>
    </div>
</template>
<script setup>
import axios from "axios"

const onClick = (e) => {
    axios.post('/v1/casbin_rule_test',).then((res) => {
        console.log(res.data)
    })
}

</script>
<style lang="">


</style>