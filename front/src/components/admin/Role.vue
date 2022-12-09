<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-30 10:10:09
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-09 20:38:54
 * @FilePath: /MiniAdmin/front/src/components/admin/Role.vue
-->
<template lang="">
  <a-card style="margin-bottom: 10px;">
        <a-space>
        <a-button type="primary" @click="showDrawer">创建用户组</a-button>
        </a-space>
  </a-card>
  <a-table :columns="columns" :data-source="data">
    <template #headerCell="{ columns }">
    </template>
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'action'">
        <span>
          <a-button type="primary" size="small" @click="editshowDrawer(record.id)">
            <template #icon><EditFilled /></template>
          </a-button>
          <a-divider type="vertical" />
          <a-button type="primary" size="small" @click="deleteRole(record.id)">
          <template #icon><DeleteFilled /></template>
          </a-button>
          <a-divider type="vertical" />
          <a-button type="primary" size="small" @click="showChangeRole(record.id)">
          编辑权限
          </a-button>
        </span>
      </template>
    </template>
  </a-table>

  <a-drawer title="创建用户组(角色)" width="550" v-model:visible="visible">
    <a-form :model="createroleform" :rules="roleformrules" layout="vertical" @finish="onRoleFinish"
            @finishFailed="onRoleFinishFailed">
          <a-form-item label="角色名称" name="name">
            <a-input v-model:value="createroleform.name" placeholder="Please enter name" />
          </a-form-item>
          <a-form-item label="role_key" name="role_key">
            <a-input v-model:value="createroleform.role_key" placeholder="Please enter role_key" />
          </a-form-item>
          <a-form-item label="角色简介" name="description">
            <a-input v-model:value="createroleform.description" placeholder="Please enter description" />
          </a-form-item>
    </a-form>
    <template #extra>
        <a-button @click="onClose">取消</a-button>
        <a-button :disabled="disabled" type="primary" @click="onRoleFinish">提交</a-button>
    </template>
  </a-drawer>


  <a-drawer title="编辑用户组(角色)" width="550" v-model:visible="editvisible">
    <a-form :model="editroleform" :rules="roleformrules" layout="vertical" @finish="onRoleFinish">
        <a-input v-model:value="editroleform.role_id" type="hidden" />
          <a-form-item label="角色名称" name="name">
            <a-input v-model:value="editroleform.name" placeholder="Please enter name" />
          </a-form-item>
          <a-form-item label="role_key" name="role_key">
            <a-input v-model:value="editroleform.role_key" placeholder="Please enter role_key" />
          </a-form-item>
          <a-form-item label="角色简介" name="description">
            <a-input v-model:value="editroleform.description" placeholder="Please enter description" />
          </a-form-item>
    </a-form>
    <template #extra>
        <a-button @click="editonClose">取消</a-button>
        <a-button :disabled="editdisabled" type="primary" @click="editRole">提交</a-button>
    </template>
  </a-drawer>



  <a-drawer title="编辑权限" width="550" v-model:visible="changevisible">
    <template #extra>
        <a-button @click="changeonClose">取消</a-button>
        <a-button type="primary" @click="changerole">提交</a-button>
    </template>


    <div  v-for="(item,index) of options.value" >
        <a-checkbox-group v-model:value="checkeds.value[index]" :options="item" />
    </div>
        
  </a-drawer>

</template>
<script setup>
import { EditFilled, DeleteFilled, ExclamationCircleOutlined } from '@ant-design/icons-vue';
import { reactive, ref, computed, createVNode } from 'vue';
import axios from 'axios'
import { Modal } from 'ant-design-vue';

const options = reactive([]) // 渲染所有权限的多选框
const checkeds = reactive([]) // 选中已经选择的
const change_role_id = ref(0) // 当前用户组的id
const changevisible = ref(false)

// 打开编辑权限的抽屉
const showChangeRole = (role_id) => {
  axios.get('/v1/role/get_coca', {
    params: { role_id: role_id },
  }).then((response) => {
    options.value = response.data.options
    checkeds.value = response.data.checkeds
    change_role_id.value = role_id
    // console.log(response.data);

  })
  changevisible.value = true

}
const changeonClose = () => {
  changevisible.value = false;
}
// 修改用户组权限
const changerole = () => {
  // console.log(checkeds.value);
  // console.log(change_role_id.value);
  axios.post('v1/role/change_role', {
    role_id: change_role_id.value,
    checkeds: checkeds.value,
  }).then((response) => {
    if (response.data) {
      let model = Modal.info()
      model.update({
        title: '提示!',
        content: '修改成功!',
        onOk: () => {
          editvisible.value = false
          openPage()
        }
      })
    } else {
      let modal = Modal.error()
      modal.update({
        title: '错误!',
        content: "修改失败!请检查权限参数",
      })
    }
  })
}

// ##########################
const editroleform = reactive({
  role_id: 0,
  name: '',
  role_key: '',
  description: '',
})

const editvisible = ref(false)

const editdisabled = computed(() => {
  return !(editroleform.name && editroleform.role_key && editroleform.description);
});
// 打开编辑资料的抽屉
const editshowDrawer = (role_id) => {
  axios.get('/v1/role/get_role_by_id', {
    params: {
      role_id: role_id
    }
  }).then(function (response) {
    editroleform.name = response.data.name
    editroleform.role_key = response.data.role_key
    editroleform.description = response.data.description
    editroleform.role_id = role_id
    editvisible.value = true
  })


}
const editonClose = () => {
  editvisible.value = false;
};

// 提交修改用户组(角色)的资料
const editRole = () => {
  axios.post('/v1/role/update_role', {
    old_role_id: editroleform.role_id,
    name: editroleform.name,
    role_key: editroleform.role_key,
    description: editroleform.description
  },).then(function (response) {
    if (response.data) {
      let model = Modal.info()
      model.update({
        title: '提示!',
        content: '修改成功!',
        onOk: () => {
          editvisible.value = false
          openPage()
        }
      })
    } else {
      let modal = Modal.error()
      modal.update({
        title: '错误!',
        content: "修改失败!",
      })
    }
  }).catch(function (error) {
    let modal = Modal.error()
      modal.update({
        title: '错误!',
        content: "修改失败!",
      })
  })
}

const deleteRole = (role_id) => {
  Modal.confirm({
    title: '确定要删除吗?',
    icon: createVNode(ExclamationCircleOutlined),
    content: '确定后会删除此用户组(角色)',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk() {
      axios.get('v1/role/delete_role', {
        params: { role_id: role_id },
      }).then(function (response) {
        if (response.data) {
          openPage()
          let model = Modal.info()
          model.update({
            title: '提示!',
            content: '删除成功!'
          })
        }
      }).catch(function (error) {
        let model = Modal.error()
        model.update({
          title: '提示!',
          content: '删除失败!'
        })

      })
    },
    onCancel() {
      console.log('Cancel');
    },
  });
}

// ###############

const createroleform = reactive({
  name: '',
  role_key: '',
  description: '',
})
const roleformrules = {
  name: [{
    required: true,
    message: 'Please enter user name',
  }],
  role_key: [{
    required: true,
    message: 'Please enter user role_key',
  }],
  description: [{
    required: true,
    message: 'Please enter role description',
  }],
}
const visible = ref(false)

const showDrawer = () => {
  visible.value = true
}
const onClose = () => {
  visible.value = false;
};


// 增加role
const onRoleFinish = () => {
  // console.log(createroleform);
  axios.post('/v1/role/create_role', {
    name: createroleform.name,
    role_key: createroleform.role_key,
    description: createroleform.description,
    user_id: sessionStorage.getItem('user_id')
  }).then(function (response) {
    if (response.data) {
      let model = Modal.info()
      model.update({
        title: '提示!',
        content: '创建成功!',
        onOk: () => {
          visible.value = false
          openPage()
        }
      })
    } else {
      let modal = Modal.error()
      modal.update({
        title: '错误!',
        content: "创建失败!",
      })
    }
    createroleform.name = ''
    createroleform.role_key = ''
    createroleform.description = ''
  }).then(function (error) {

  })

};
const onRoleFinishFailed = (errorInfo) => {
  console.log("Failed:", errorInfo);
};
const disabled = computed(() => {
  return !(createroleform.name && createroleform.role_key && createroleform.description);
});

// 表头
const columns = ref([
  {
    title: 'Id',
    dataIndex: 'id',
    key: 'id',
  },
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
  }, {
    title: '角色key',
    dataIndex: 'role_key',
    key: 'role_key',
  }, {
    title: '简介',
    key: 'description',
    dataIndex: 'description',
  }, {
    title: '管理',
    key: 'action',
  }])
const data = ref([]) // 数据

// 默认打开页面后的请求数据
const openPage = () => {
  axios.get('v1/role/get_roles',).then(function (response) {
    data.value = response.data
    // console.log(data);
  }).catch(function (error) {
    console.log(error)
  })
}
openPage()



</script>
<style lang="">
    
</style>