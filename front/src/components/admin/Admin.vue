<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 21:01:41
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-06 14:42:35
 * @FilePath: /MiniAdmin/front/src/components/admin/admin.vue
-->
<template>
    <a-layout>
        <a-layout-sider breakpoint="lg" collapsed-width="0" @collapse="onCollapse" @breakpoint="onBreakpoint">
            <div class="logo" />
            <a-menu v-model:selectedKeys="selectedKeys" mode="inline" theme="dark">
                <a-menu-item key="1">
                    <router-link to="/admin/main">
                        <home-outlined />
                        <span class="nav-home">首页</span>
                    </router-link>
                </a-menu-item>
                <a-menu-item key="2">
                    <router-link to="/admin/user">
                        <user-outlined />
                        <span class="nav-text">用户管理</span>
                    </router-link>
                </a-menu-item>
                <a-menu-item key="3">
                    <router-link to="/admin/role">
                        <group-outlined />
                        <span class="nav-text">角色管理</span>
                    </router-link>
                </a-menu-item>
                <a-menu-item key="4">
                    <router-link to="/admin/casbin_object">
                        <folder-add-outlined />
                        <span class="nav-text">资源管理</span>
                    </router-link>
                </a-menu-item>
                <a-menu-item key="5">
                    <router-link to="/admin/casbin_action">
                        <thunderbolt-outlined />
                        <span class="nav-text">动作管理</span>
                    </router-link>
                </a-menu-item>
            </a-menu>
        </a-layout-sider>
        <a-layout>
            <a-layout-header :style="{ background: '#fff', padding: 0 }">
                <AppHeader />
            </a-layout-header>
            <a-layout-content :style="{ margin: '24px 16px 0' }">
                <div :style="{ padding: '24px', background: '#fff', height: '100%' }">
                    <router-view></router-view>
                </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                <FooterVue />
            </a-layout-footer>
        </a-layout>
    </a-layout>


</template>
<script setup>
import { UserOutlined, GroupOutlined, HomeOutlined,FolderAddOutlined,ThunderboltOutlined} from '@ant-design/icons-vue';
import { ref } from 'vue';
import AppHeader from '../AppHeader.vue';
import FooterVue from '../Footer.vue';
import axios from 'axios'
import { useRouter } from "vue-router";

const router = useRouter();

const onCollapse = (collapsed, type) => {
    // console.log(collapsed, type);
}
const onBreakpoint = broken => {
    // console.log(broken);
}

const selectedKeys = ref(['1'])

</script>
<style>
.logo {
    height: 32px;
    background: rgba(255, 255, 255, 0.2);
    margin: 16px;
}

.site-layout-sub-header-background {
    background: #fff;
}

.site-layout-background {
    background: #fff;
}

[data-theme='dark'] .site-layout-sub-header-background {
    background: #141414;
}
</style>