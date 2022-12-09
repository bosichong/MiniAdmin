<!--
 * @Author: J.sky bosichong@qq.com
 * @Date: 2022-11-30 10:11:04
 * @LastEditors: J.sky bosichong@qq.com
 * @LastEditTime: 2022-12-09 23:41:23
 * @FilePath: /MiniAdmin/front/src/components/admin/CasbinAction.vue
-->
<template lang="">
    <a-card style="margin-bottom: 10px;">
          <a-space>
          <a-button type="primary" @click="showDrawer">创建动作</a-button>
          </a-space>
    </a-card>
    <a-table :columns="columns" :data-source="data">
      <template #headerCell="{ columns }">
      </template>
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <span>
            <a-button type="primary" size="small" @click="editshowDrawer(record.id)">
                <template #icon><EditFilled /></template></a-button>
            <a-divider type="vertical" />
            <a-button type="primary" size="small" @click="deleteca(record.id)"><template #icon><DeleteFilled /></template></a-button>
          </span>
        </template>
      </template>
    </a-table>
  
    <a-drawer title="创建动作" width="550" v-model:visible="visible">
      <a-form :model="createcaform" :rules="caformrules" layout="vertical" @finish="oncaFinish"
              @finishFailed="oncaFinishFailed">
            <a-form-item label="动作名称" name="name">
              <a-input v-model:value="createcaform.name" placeholder="Please enter name" />
            </a-form-item>
            <a-form-item label="action_key" name="action_key">
              <a-input v-model:value="createcaform.action_key" placeholder="Please enter action_key" />
            </a-form-item>
            <a-form-item label="简介" name="description">
              <a-input v-model:value="createcaform.description" placeholder="Please enter description" />
            </a-form-item>
      </a-form>
      <template #extra>
          <a-button @click="onClose">取消</a-button>
          <a-button :disabled="disabled" type="primary" @click="oncaFinish">提交</a-button>
      </template>
    </a-drawer>

    <a-drawer title="编辑资源" width="550" v-model:visible="editvisible">
    <a-form :model="editcaform" :rules="caformrules" layout="vertical" @finish="oncaFinish">
        <a-input v-model:value="editcaform.ca_id" type="hidden" />
          <a-form-item label="资源名称" name="name">
            <a-input v-model:value="editcaform.name" placeholder="Please enter name" />
          </a-form-item>
          <a-form-item label="action_key" name="action_key">
            <a-input v-model:value="editcaform.action_key" placeholder="Please enter action_key" />
          </a-form-item>
          <a-form-item label="简介" name="description">
            <a-input v-model:value="editcaform.description" placeholder="Please enter description" />
          </a-form-item>
    </a-form>
    <template #extra>
        <a-button @click="editonClose">取消</a-button>
        <a-button :disabled="editdisabled" type="primary" @click="editca">提交</a-button>
    </template>
  </a-drawer>
</template>
<script setup>
import { PlusOutlined, ExclamationCircleOutlined,EditFilled,DeleteFilled, } from '@ant-design/icons-vue';
import { reactive, ref, computed, createVNode } from 'vue';
import axios from 'axios'
import { Modal } from 'ant-design-vue';



const editcaform = reactive({
    ca_id: 0,
    name: '',
    action_key: '',
    description: '',
})

const editvisible = ref(false)

const editdisabled = computed(() => {
    return !(editcaform.name && editcaform.action_key && editcaform.description);
});
// 打开编辑资料的抽屉
const editshowDrawer = (ca_id) => {
    axios.get('/v1/ca/get_ca', {
        params: {
            ca_id: ca_id
        }
    }).then(function (response) {
        editcaform.name = response.data.name
        editcaform.action_key = response.data.action_key
        editcaform.description = response.data.description
        editcaform.ca_id = ca_id
        editvisible.value = true
    })


}
const editonClose = () => {
    editvisible.value = false;
};

// 提交修改用户组(角色)的资料
const editca = () => {
    axios.post('/v1/ca/update_ca', {
        old_ca_id: editcaform.ca_id,
        name: editcaform.name,
        action_key: editcaform.action_key,
        description: editcaform.description
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

const deleteca = (ca_id) =>{
    Modal.confirm({
    title: '确定要删除吗?',
    icon: createVNode(ExclamationCircleOutlined),
    content: '确定后会删除此资源及其相关的权限!',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk() {
      axios.get('v1/ca/delete_ca', {
        params: { ca_id : ca_id},
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

const createcaform = reactive({
    name: '',
    action_key: '',
    description: '',
})
const caformrules = {
    name: [{
        required: true,
        message: 'Please enter name',
    }],
    action_key: [{
        required: true,
        message: 'Please enter action_key',
    }],
    description: [{
        required: true,
        message: 'Please enter description',
    }],
}
const visible = ref(false)

const showDrawer = () => {
    visible.value = true
}
const onClose = () => {
    visible.value = false;
};

// 增加ca
const oncaFinish = () => {
    // console.log(createcaform);
    axios.post('/v1/ca/create_ca', {
        name: createcaform.name,
        action_key: createcaform.action_key,
        description: createcaform.description,
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
        createcaform.name = ''
        createcaform.action_key = ''
        createcaform.description = ''
    }).then(function (error) {

    })

};
const oncaFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
};
const disabled = computed(() => {
    return !(createcaform.name && createcaform.action_key && createcaform.description);
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
        title: '动作key',
        dataIndex: 'action_key',
        key: 'action_key',
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
    axios.get('v1/ca/get_cas',).then(function (response) {
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