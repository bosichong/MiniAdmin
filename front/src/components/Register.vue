<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-12-10 08:20:34
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-12 22:09:09
 * @FilePath: /MiniAdmin/front/src/components/register.vue
-->
<template lang="">
    <div class="register">
        <a-typography-title :level="3">Register</a-typography-title>
        <a-form :model="formUser" >
        <a-form-item label="username:">
            <a-input v-model:value="formUser.username">
            <template #prefix>
                <UserOutlined class="site-form-item-icon" />
            </template>
            </a-input>
        </a-form-item>
        <a-form-item label="password:" name="password">
            <a-input-password v-model:value="formUser.password">
            <template #prefix>
                <LockOutlined class="site-form-item-icon" />
            </template>
            </a-input-password>
        </a-form-item>
        <a-form-item label="sex:">
            <a-radio-group v-model:value="formUser.sex">
            <a-radio value="1">male</a-radio>
            <a-radio value="0">female</a-radio>
            </a-radio-group>
        </a-form-item>
        <a-form-item label="email:">
            <a-input v-model:value="formUser.email" />
        </a-form-item>
        <a-form-item :wrapper-col="{ span: 24, offset: 0}">
            <a-button type="primary" @click="onSubmit()" block>Submit</a-button>
        </a-form-item>
        </a-form>
    </div>
</template>
<script setup>
import { ref, reactive, } from 'vue';
import { UsergroupAddOutlined, ExclamationCircleOutlined, LockOutlined, UserOutlined, EditFilled, DeleteFilled, } from '@ant-design/icons-vue';
import { Modal } from 'ant-design-vue';
import axios from 'axios'
import { useRouter } from "vue-router";

const router = useRouter();
// 编辑用户资料的表单相关
const formUser = reactive({
    username: '',
    password: '',
    sex: '1',
    email: '',
});

const onSubmit = function() {
    axios.post('/v1/user/create_user', {
        username: formUser.username,
        password: formUser.password,
        sex: formUser.sex,
        email: formUser.email
    }).then((res) => {
        let model = Modal.info()
        model.update({
            title: '提示!',
            content: '注册成功!请登录.',
            onOk: () => {
                router.push('/login')
            }
        })
    }).catch((error) => {
        let model = Modal.error()
        model.update({
            title: '错误!',
            content: error.response.data.detail,
            onOk: () => {
            }
        })
    })
}
</script>
<style>
.register {
    text-align: center;
    position: fixed;
    width: 350px;
    height: 200px;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
}
</style>