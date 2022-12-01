<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-12-01 09:10:43
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-01 22:50:01
 * @FilePath: /MiniAdmin/front/src/components/Login.vue
-->
<template>
    <div class="minilogin">
        <a-row>
            <a-col :xs="2" :sm="4" :md="7" :lg="8" :xl="9"></a-col>
            <a-col :xs="20" :sm="16" :md="10" :lg="8" :xl="6">
                <a-form :model="formState" name="normal_login" class="login-form" @finish="onFinish"
                    @finishFailed="onFinishFailed">
                    <a-form-item label="Username" name="username"
                        :rules="[{ required: true, message: 'Please input your username!' }]">
                        <a-input v-model:value="formState.username">
                            <template #prefix>
                                <UserOutlined class="site-form-item-icon" />
                            </template>
                        </a-input>
                    </a-form-item>

                    <a-form-item label="Password" name="password"
                        :rules="[{ required: true, message: 'Please input your password!' }]">
                        <a-input-password v-model:value="formState.password">
                            <template #prefix>
                                <LockOutlined class="site-form-item-icon" />
                            </template>
                        </a-input-password>
                    </a-form-item>

                    <a-form-item>
                        <a-form-item name="remember" no-style>
                            <a-checkbox v-model:checked="formState.remember">Remember me</a-checkbox>
                        </a-form-item>
                        <a class="login-form-forgot" href="">Forgot password</a>
                    </a-form-item>

                    <a-form-item>
                        <a-button :disabled="disabled" type="primary" html-type="submit" class="login-form-button">
                            Log in
                        </a-button>
                        Or
                        <a href="">register now!</a>
                    </a-form-item>
                </a-form>
            </a-col>
            <a-col :xs="2" :sm="4" :md="7" :lg="8" :xl="9"></a-col>
        </a-row>
    </div>
</template>
<script setup>
import { reactive, computed } from "vue";
import { UserOutlined, LockOutlined } from "@ant-design/icons-vue";
import axios from "axios"
import { useRouter } from "vue-router";
import { Modal } from 'ant-design-vue';

const router = useRouter();

const formState = reactive({
    username: "",
    password: "",
    remember: true,
});

const onFinish = (values) => {
    axios.post('v1/token', {
        username: values.username,
        password: values.password,
    },
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
    ).then(function (response) {
        let token = response.data.access_token
        sessionStorage.setItem('token', token)

        if (sessionStorage.getItem('username') === null) {
            axios.get("v1/user/me", {
                headers: {
                    "accept": "application / json",
                    "Authorization": "Bearer " + sessionStorage.getItem('token')
                }
            }).then((function (response) {
                sessionStorage.setItem("id", response.data.id)
                sessionStorage.setItem("username", response.data.username)
                sessionStorage.setItem("email", response.data.email)
                sessionStorage.setItem("sex", response.data.sex)
                router.push('/admin/main')

            }))
            router.push('/')
        }

    }).catch(function (error) {
        console.log(error.response.data.detail)
        let modal = Modal.error()
        modal.update({
            title: '错误!',
            content: error.response.data.detail,
        })

    })
    return false;
};
const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
};
const disabled = computed(() => {
    return !(formState.username && formState.password);
});
</script>
<style>
#components-form-demo-normal-login .login-form {
    max-width: 300px;
}

#components-form-demo-normal-login .login-form-forgot {
    float: right;
}

#components-form-demo-normal-login .login-form-button {
    width: 100%;
}

.minilogin {
    margin-top: 150px;
}
</style>