/*
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 19:42:59
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-01 11:16:24
 * @FilePath: /MiniAdmin/front/src/router/index.js
 */
import { createRouter, createWebHistory } from 'vue-router'



const Admin = () => import('../components/admin/Admin.vue')
const Login = () => import('../components/Login.vue')


const routes = [
    {
        path: '/',
        redirect: '/admin'
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: {
            title: 'Login'
        }
    },
    {
        path: '/admin',
        name: 'admin',
        component: Admin,
        meta: {
            title: '管理首页',
            icon: 'Admin',
            permission: ['Admin', 'show']
        },
        children: [
            {
                path: 'main',
                name: 'Main',
                component: () => import('../components/admin/Main.vue'),
                meta: {
                    title: '后台管理首页',
                    icon: 'admin',
                    permission: ['Admin', 'show']
                }
            },
            {
                path: 'about',
                name: 'About',
                component: () => import('../components/About.vue'),
                meta: {
                    title: '关于',
                    icon: 'about',
                    permission: ['About', 'show']
                }
            },
            {
                path: 'user',
                name: 'User',
                component: () => import('../components/admin/User.vue'),
                meta: {
                    title: '用户管理',
                    icon: 'user',
                    permission: ['User', 'show']
                }
            },
            {
                path: 'role',
                name: 'Role',
                component: () => import('../components/admin/Role.vue'),
                meta: {
                    title: '角色管理',
                    icon: 'role',
                    permission: ['Role', 'show']
                }
            },
            {
                path: 'casbin_object',
                name: 'CasbinObject',
                component: () => import('../components/admin/CasbinObject.vue'),
                meta: {
                    title: '资源管理',
                    icon: 'object',
                    permission: ['CasbinObject', 'show']
                }
            },
            {
                path: 'casbin_action',
                name: 'CasbinAction',
                component: () => import('../components/admin/CasbinAction.vue'),
                meta: {
                    title: '动作管理',
                    icon: 'object',
                    permission: ['CasbinAction', 'show']
                }
            },
            {
                path: 'casbin_category',
                name: 'CasbinCategory',
                component: () => import('../components/admin/CasbinCategory.vue'),
                meta: {
                    title: '资源分类管理',
                    icon: 'object',
                    permission: ['CasbinCategory', 'show']
                }
            },


        ]
    },

    {
        path: "/:catchAll(.*)",
        name: 'error404',
        component: () => import('../components/error-page/404.vue')
    },
    {
        path: '/403',
        name: 'error403',
        component: () => import('../components/error-page/403.vue')
    },
    {
        path: '/500',
        name: 'error500',
        component: () => import('../components/error-page/500.vue')
    }
]






const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, from) => {
    // 判断用户是否登陆和锁定,后端判断锁定用户是不能登陆的,不会得到token
    let isLogin = sessionStorage.getItem('token')
    if (
        // 检查用户是否已登录
        !isLogin &&
        // ❗️ 避免无限重定向
        to.name !== 'Login'
    ) {
        // 将用户重定向到登录页面
        return { name: 'Login' }
    }
})



export default router