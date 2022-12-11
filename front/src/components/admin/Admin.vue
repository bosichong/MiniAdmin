<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 21:01:41
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-11 21:24:16
 * @FilePath: /MiniAdmin/front/src/components/admin/admin.vue
-->
<template>
    <a-layout>
        <a-layout-sider breakpoint="lg" collapsed-width="0" @collapse="onCollapse" @breakpoint="onBreakpoint"
            :style="{background:'none'}">
            <div class="logo" />
            <a-menu v-model:selectedKeys="selectedKeys" v-model:openKeys="openKeys" mode="inline">
                <a-menu-item key="1">
                    <router-link to="/admin/main">
                        <home-outlined />
                        <span class="nav-home">首页</span>
                    </router-link>
                </a-menu-item>
                <a-sub-menu key="sub1">
                    <template #title>
                        <span>
                            <user-outlined />
                            <span>用户管理</span>
                        </span>
                    </template>
                    <a-menu-item key="2" v-if="menu.User">
                        <router-link to="/admin/user">
                            <team-outlined />
                            <span>用户列表</span>
                        </router-link>
                    </a-menu-item>
                    <a-menu-item key="3" v-if="menu.Role">
                        <router-link to="/admin/role">
                            <group-outlined />
                            <span>角色管理</span>
                        </router-link>
                    </a-menu-item>
                </a-sub-menu>

                <a-sub-menu key="sub2">
                    <template #title>
                        <span>
                            <unlock-outlined />
                            <span>权限管理</span>
                        </span>
                    </template>
                    <a-menu-item key="5" v-if="menu.CasbinObject">
                        <router-link to="/admin/casbin_object">
                            <folder-add-outlined />
                            <span>资源管理</span>
                        </router-link>
                    </a-menu-item>
                    <a-menu-item key="6" v-if="menu.CasbinAction">
                        <router-link to="/admin/casbin_action">
                            <thunderbolt-outlined />
                            <span>动作管理</span>
                        </router-link>
                    </a-menu-item>
                </a-sub-menu>

            </a-menu>
        </a-layout-sider>
        <a-layout>
            <a-layout-header :style="{ padding: 0, background: 'none' }">
                <AppHeader />
            </a-layout-header>
            <a-layout-content :style="{ margin: '8px 8px 0', }">
                <div :style="{ padding: '24px', height: '100%' }">
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
import { TeamOutlined, UnlockOutlined, UserOutlined, GroupOutlined, HomeOutlined, FolderAddOutlined, ThunderboltOutlined } from '@ant-design/icons-vue';
import { ref, reactive } from 'vue';
import AppHeader from '../AppHeader.vue';
import FooterVue from '../Footer.vue';
import axios from 'axios'
import { useRouter } from "vue-router";

const menu = ref({})

// 获取菜单显示权限
axios.get('v1/get_menu',{
    headers: {
        "accept": "application / json",
        "Authorization": "Bearer " + sessionStorage.getItem('token')
    },
}).then((response) => {
    menu.value = response.data
    // console.log(menu.value);
})

const router = useRouter();

const onCollapse = (collapsed, type) => {
    // console.log(collapsed, type);
}
const onBreakpoint = broken => {
    // console.log(broken);
}

const selectedKeys = ref(['1'])
const openKeys = ref(['sub1', 'sub2'])

</script>
<style>
.logo {
    height: 32px;
    background: rgba(115, 184, 173, 0.1);
    margin: 16px;
}

.ant-layout {
    background: none;
}
</style>