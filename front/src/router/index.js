/*
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 19:42:59
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-13 01:08:48
 * @FilePath: /MiniAdmin/front/src/router/index.js
 */
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'



const Admin = () => import('../components/admin/Admin.vue')
const Login = () => import('../components/Login.vue')


const routes = [
    {
        path: '/',
        redirect: '/admin'
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../components/Register.vue'),
        meta: {
            title: 'Register'
        }
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
            rule: ['User', 'show']
        },
        children: [
            {
                path: 'main',
                name: 'Main',
                component: () => import('../components/admin/Main.vue'),
                meta: {
                    title: '后台管理首页',
                    icon: 'admin',
                    rule: ['User', 'show']
                }
            },
            {
                path: 'user',
                name: 'User',
                component: () => import('../components/admin/User.vue'),
                meta: {
                    title: '用户管理',
                    icon: 'user',
                    rule: ['User', 'show']
                }
            },
            {
                path: 'role',
                name: 'Role',
                component: () => import('../components/admin/Role.vue'),
                meta: {
                    title: '角色管理',
                    icon: 'role',
                    rule: ['Role', 'show']
                }
            },
            {
                path: 'casbin_object',
                name: 'CasbinObject',
                component: () => import('../components/admin/CasbinObject.vue'),
                meta: {
                    title: '资源管理',
                    icon: 'object',
                    rule: ['CasbinObject', 'show']
                }
            },
            {
                path: 'casbin_action',
                name: 'CasbinAction',
                component: () => import('../components/admin/CasbinAction.vue'),
                meta: {
                    title: '动作管理',
                    icon: 'object',
                    rule: ['CasbinAction', 'show']
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
    },
    {
        path: '/test',
        name: 'Test',
        component: () => import('../components/Test.vue'),
        meta: {
            title: 'Test',
            icon: 'test',
            rule: ['User', 'show']
        }
    },
]






const router = createRouter({
    history: createWebHistory(),
    routes,
});

const whiteList = ['Home', 'Login', 'Register', 'error404', 'error403', 'error500'] // 白名单



router.beforeEach((to, from, next) => {
    // 判断用户是否登陆和锁定,后端判断锁定用户是不能登陆的,不会得到token
    let isLogin = sessionStorage.getItem('token')
    if (whiteList.includes(to.name)) {
        next()//如果在白名单 直接进入
    } else {
        if (
            // 检查用户是否已登录
            !isLogin &&
            // ❗️ 避免无限重定向
            to.name !== 'Login'
        ) {
            // 将用户重定向到登录页面
            next({ name: 'Login' })
        } else {
            if (to.meta.rule) {
                // console.log(to.meta.rule);
                axios.post('/v1/isAuthenticated', {
                        obj: to.meta.rule[0],
                        act: to.meta.rule[1]
                },{
                    headers:{
                        "accept": "application / json",
                        "Authorization": "Bearer " + sessionStorage.getItem('token')
                    },
                }).then(function (response) {
                    console.log(response.data);
                    if (response.data === '锁定'){
                        sessionStorage.clear()
                        next({ name: 'Login' })
                    }else if(response.data){
                        next()
                    }else{
                        next({name:'error403'})
                    }
                }).catch(function (err) {
                    // token超时,将用户重定向到登录页面
                    next({ name: 'Login' })
                })
                

            } else {
                next()
            }

        }
    }

})



export default router