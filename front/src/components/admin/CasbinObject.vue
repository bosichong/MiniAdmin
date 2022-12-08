<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-30 10:08:35
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-08 18:08:45
 * @FilePath: /MiniAdmin/front/src/components/admin/CasbinObject.vue
-->
<template lang="">
    <a-card style="margin-bottom: 10px;">
          <a-space>
          <a-button type="primary" @click="showDrawer">创建资源</a-button>
          </a-space>
    </a-card>
    <a-table :columns="columns" :data-source="data">
      <template #headerCell="{ columns }">
      </template>
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <span>
            <a-button type="primary" size="small" @click="editshowDrawer(record.id)">编辑</a-button>
            <a-divider type="vertical" />
            <a-button type="primary" size="small" @click="deleteRole(record.id)">删除</a-button>
          </span>
        </template>
      </template>
    </a-table>
  
    <a-drawer title="创建资源" width="550" v-model:visible="visible">
      <a-form :model="createCoform" :rules="coformrules" layout="vertical" @finish="onCoFinish"
              @finishFailed="onCoFinishFailed">
            <a-form-item label="资源名称" name="name">
              <a-input v-model:value="createCoform.name" placeholder="Please enter name" />
            </a-form-item>
            <a-form-item label="object_key" name="object_key">
              <a-input v-model:value="createCoform.object_key" placeholder="Please enter object_key" />
            </a-form-item>
            <a-form-item label="简介" name="description">
              <a-input v-model:value="createCoform.description" placeholder="Please enter description" />
            </a-form-item>
      </a-form>
      <template #extra>
          <a-button @click="onClose">取消</a-button>
          <a-button :disabled="disabled" type="primary" @click="onCoFinish">提交</a-button>
      </template>
    </a-drawer>

    <a-drawer title="编辑资源" width="550" v-model:visible="editvisible">
    <a-form :model="editcoform" :rules="coformrules" layout="vertical" @finish="onCoFinish">
        <a-input v-model:value="editcoform.co_id" type="hidden" />
          <a-form-item label="资源名称" name="name">
            <a-input v-model:value="editcoform.name" placeholder="Please enter name" />
          </a-form-item>
          <a-form-item label="object_" name="object_key">
            <a-input v-model:value="editcoform.object_key" placeholder="Please enter object_key" />
          </a-form-item>
          <a-form-item label="简介" name="description">
            <a-input v-model:value="editcoform.description" placeholder="Please enter description" />
          </a-form-item>
    </a-form>
    <template #extra>
        <a-button @click="editonClose">取消</a-button>
        <a-button :disabled="editdisabled" type="primary" @click="editRole">提交</a-button>
    </template>
  </a-drawer>
</template>
<script setup>
import { PlusOutlined, ExclamationCircleOutlined } from '@ant-design/icons-vue';
import { reactive, ref, computed, createVNode } from 'vue';
import axios from 'axios'
import { Modal } from 'ant-design-vue';


const editcoform = reactive({
    co_id: 0,
    name: '',
    object_key: '',
    description: '',
})

const editvisible = ref(false)

const editdisabled = computed(() => {
    return !(editcoform.name && editcoform.object_key && editcoform.description);
});
// 打开编辑资料的抽屉
const editshowDrawer = (co_id) => {
    axios.get('/v1/co/get_co', {
        params: {
            co_id: co_id
        }
    }).then(function (response) {
        editcoform.name = response.data.name
        editcoform.object_key = response.data.object_key
        editcoform.description = response.data.description
        editcoform.co_id = co_id
        editvisible.value = true
    })


}
const editonClose = () => {
    editvisible.value = false;
};

// 提交修改用户组(角色)的资料
const editRole = () => {
    axios.post('/v1/co/update_co', {
        old_co_id: editcoform.co_id,
        name: editcoform.name,
        object_key: editcoform.object_key,
        description: editcoform.description
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
    })
}

const deleteRole = (co_id) =>{
    Modal.confirm({
    title: '确定要删除吗?',
    icon: createVNode(ExclamationCircleOutlined),
    content: '确定后会删除此资源及其相关的权限!',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk() {
      axios.get('v1/co/delete_co', {
        params: { co_id : co_id},
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

const createCoform = reactive({
    name: '',
    object_key: '',
    description: '',
})
const coformrules = {
    name: [{
        required: true,
        message: 'Please enter name',
    }],
    object_key: [{
        required: true,
        message: 'Please enter object_key',
    }],
    description: [{
        required: true,
        message: 'Please enter  description',
    }],
}
const visible = ref(false)

const showDrawer = () => {
    visible.value = true
}
const onClose = () => {
    visible.value = false;
};

// 增加co
const onCoFinish = () => {
    // console.log(createCoform);
    axios.post('/v1/co/create_co', {
        name: createCoform.name,
        object_key: createCoform.object_key,
        description: createCoform.description,
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
        createCoform.name = ''
        createCoform.object_key = ''
        createCoform.description = ''
    }).then(function (error) {

    })

};
const onCoFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
};
const disabled = computed(() => {
    return !(createCoform.name && createCoform.object_key && createCoform.description);
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
        title: '资源key',
        dataIndex: 'object_key',
        key: 'object_key',
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
    axios.get('v1/co/get_cos',).then(function (response) {
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