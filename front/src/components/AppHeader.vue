<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-29 19:48:29
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-13 09:28:26
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



  <a-drawer width="550" v-model:visible="visible" class="custom-class" style="color: red" title="编辑资料"
    placement="right" @after-visible-change="afterVisibleChange">
    <a-form :model="formUserEdit" :label-col="labelCol" :wrapper-col="wrapperCol">
      <a-input v-model:value="formUserEdit.user_id" type="hidden" />
      <a-form-item label="登陆帐户:">
        <a-input v-model:value="formUserEdit.username">
          <template #prefix>
            <UserOutlined class="site-form-item-icon" />
          </template>
        </a-input>
      </a-form-item>
      <a-form-item label="登陆密码:" name="password">
        <a-input-password v-model:value="formUserEdit.password">
          <template #prefix>
            <LockOutlined class="site-form-item-icon" />
          </template>
        </a-input-password>
      </a-form-item>
      <a-form-item label="性别:">
        <a-radio-group v-model:value="formUserEdit.sex">
          <a-radio value="1">男</a-radio>
          <a-radio value="0">女</a-radio>
        </a-radio-group>
      </a-form-item>
      <a-form-item label="Email:">
        <a-input v-model:value="formUserEdit.email" />
      </a-form-item>
      <a-form-item label="备注:">
        <a-input v-model:value="formUserEdit.remark" />
      </a-form-item>
      <a-form-item :wrapper-col="{ span: 14, offset: 4 }">
        <a-button type="primary" @click="onSubmit()">提交修改</a-button>
        <a-button style="margin-left: 10px" @click="onClose">取消</a-button>
      </a-form-item>
    </a-form>
  </a-drawer>


</template>
<script setup>
import { useRouter } from "vue-router";
import { ref, reactive, } from 'vue';
import axios from 'axios'
import {DownOutlined , UsergroupAddOutlined, ExclamationCircleOutlined, LockOutlined, UserOutlined, EditFilled, DeleteFilled, } from '@ant-design/icons-vue';

import { Modal } from 'ant-design-vue';


const router = useRouter();
const username = ref(sessionStorage.getItem('username'))



const handleMenuClick = e => {
  
  if (e.key === '3') {
    sessionStorage.clear()
    router.push('/login')
  }else if (e.key === '1'){
    let id = sessionStorage.getItem('user_id')
    // console.log(id);
    showDrawer(id)
  }
};



// ###########################
// 编辑资料抽屉

const visible = ref(false);// 抽屉开关
const afterVisibleChange = bool => {
  // console.log('visible', bool);
};

// 打开编辑用户资料的抽屉
const showDrawer = (user_id) => {
  axios.get("v1/user/user_by_id", {
    params: { user_id: user_id }
  }).then((function (response) {
    formUserEdit.user_id = user_id
    formUserEdit.username = response.data.username
    formUserEdit.email = response.data.email
    formUserEdit.sex = response.data.sex
    formUserEdit.remark = response.data.remark
    visible.value = true;
  })).catch(function (error) {
    if (error) {
      let model = Modal.error()
      model.update({
        title: '错误!',
        content: error.response.data.detail,
        onOk: () => {
          visible.value = false
        }
      })

    }
  })


}


// 编辑用户资料的表单相关
const formUserEdit = reactive({
  user_id: 0,
  username: '',
  password: '',
  sex: '',
  email: '',
  avatar: '',
  remark: '',
});

/**
 * 提交修改用户资料
 */
const onSubmit = () => {
  // console.log('submit!', toRaw(formUserEdit));
  axios.post('/v1/user/update_me', {
    user_id: formUserEdit.user_id,
    username: formUserEdit.username,
    password: formUserEdit.password,
    email: formUserEdit.email,
    sex: formUserEdit.sex,
    remark: formUserEdit.remark,
    avatar: formUserEdit.avatar,
  },).then((response) => {
      let model = Modal.info()
      model.update({
        title: '提示!',
        content: '修改成功!',
      })
  }).catch(function (error) {
    if (error) {
      let model = Modal.error()
      model.update({
        title: '错误!',
        content: error.response.data.detail,
      })

    }
  })
};
const onClose = () => {
  visible.value = false;
}

const labelCol = reactive({
  style: {
    width: '150px',
  },
})
const wrapperCol = reactive({
  span: 14,
})

</script>
<style lang="">
    
</style>