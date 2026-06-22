<template>
  <div class="translation-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>翻译管理</h2>
          <p class="subtitle">多引擎翻译，支持术语库和AI润色</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="translate-card">
          <template #header>
            <span>文本翻译</span>
          </template>
          <el-form :model="translateForm" label-width="80px">
            <el-form-item label="源语言">
              <el-select v-model="translateForm.source_lang" style="width: 100%">
                <el-option label="自动检测" value="auto" />
                <el-option label="英语" value="en" />
                <el-option label="中文" value="zh-CN" />
                <el-option label="匈牙利语" value="hu" />
                <el-option label="罗马尼亚语" value="ro" />
                <el-option label="德语" value="de" />
              </el-select>
            </el-form-item>
            <el-form-item label="目标语言">
              <el-select v-model="translateForm.target_lang" style="width: 100%">
                <el-option label="中文" value="zh-CN" />
                <el-option label="英语" value="en" />
                <el-option label="匈牙利语" value="hu" />
                <el-option label="罗马尼亚语" value="ro" />
                <el-option label="德语" value="de" />
              </el-select>
            </el-form-item>
            <el-form-item label="翻译引擎">
              <el-select v-model="translateForm.engine" style="width: 100%">
                <el-option label="AI翻译" value="ai" />
                <el-option label="Google翻译" value="google" />
                <el-option label="DeepL翻译" value="deepl" />
              </el-select>
            </el-form-item>
            <el-form-item label="源文本">
              <el-input
                v-model="translateForm.text"
                type="textarea"
                :rows="6"
                placeholder="请输入要翻译的文本"
              />
            </el-form-item>
            <el-form-item label="AI润色">
              <el-switch v-model="translateForm.polish" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doTranslate" :loading="translating">
                开始翻译
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="result-card">
          <template #header>
            <span>翻译结果</span>
          </template>
          <div v-if="translatedText" class="translated-text">
            {{ translatedText }}
          </div>
          <div v-else class="empty-state">
            <el-empty description="翻译结果将显示在这里" />
          </div>
          <div v-if="translationInfo" class="translation-info">
            <el-descriptions :column="2" size="small">
              <el-descriptions-item label="质量评分">{{ translationInfo.quality_score }}</el-descriptions-item>
              <el-descriptions-item label="翻译耗时">{{ translationInfo.translation_time }}s</el-descriptions-item>
              <el-descriptions-item label="已润色">{{ translationInfo.is_polished ? '是' : '否' }}</el-descriptions-item>
              <el-descriptions-item label="使用术语">{{ translationInfo.used_terms?.length || 0 }}个</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="terms-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>术语库管理</span>
          <el-button size="small" type="primary" @click="showTermDialog = true">添加术语</el-button>
        </div>
      </template>
      <el-table :data="terms" style="width: 100%">
        <el-table-column prop="source" label="源术语" width="200" />
        <el-table-column prop="target" label="目标术语" width="200" />
        <el-table-column prop="source_lang" label="源语言" width="120" />
        <el-table-column prop="target_lang" label="目标语言" width="120" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" text @click="deleteTerm(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加术语对话框 -->
    <el-dialog v-model="showTermDialog" title="添加术语" width="500px">
      <el-form :model="termForm" label-width="100px">
        <el-form-item label="源术语">
          <el-input v-model="termForm.source" placeholder="源语言术语" />
        </el-form-item>
        <el-form-item label="目标术语">
          <el-input v-model="termForm.target" placeholder="目标语言术语" />
        </el-form-item>
        <el-form-item label="源语言">
          <el-select v-model="termForm.source_lang" style="width: 100%">
            <el-option label="英语" value="en" />
            <el-option label="中文" value="zh-CN" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标语言">
          <el-select v-model="termForm.target_lang" style="width: 100%">
            <el-option label="中文" value="zh-CN" />
            <el-option label="英语" value="en" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTermDialog = false">取消</el-button>
        <el-button type="primary" @click="addTerm">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const translating = ref(false)
const translatedText = ref('')
const translationInfo = ref<any>(null)

const translateForm = ref({
  text: '',
  source_lang: 'auto',
  target_lang: 'zh-CN',
  engine: 'ai',
  polish: false
})

const showTermDialog = ref(false)
const termForm = ref({
  source: '',
  target: '',
  source_lang: 'en',
  target_lang: 'zh-CN'
})

const terms = ref([
  { id: 1, source: 'vape', target: '电子烟', source_lang: 'en', target_lang: 'zh-CN' },
  { id: 2, source: 'pod', target: '烟弹', source_lang: 'en', target_lang: 'zh-CN' },
  { id: 3, source: 'e-liquid', target: '烟油', source_lang: 'en', target_lang: 'zh-CN' }
])

const doTranslate = async () => {
  if (!translateForm.value.text) {
    ElMessage.warning('请输入要翻译的文本')
    return
  }
  
  translating.value = true
  
  // 模拟翻译
  setTimeout(() => {
    translatedText.value = `【翻译结果】${translateForm.value.text}（这是模拟的翻译结果）`
    translationInfo.value = {
      quality_score: 0.92,
      translation_time: 1.5,
      is_polished: translateForm.value.polish,
      used_terms: ['vape', 'pod']
    }
    translating.value = false
  }, 1500)
}

const addTerm = () => {
  if (!termForm.value.source || !termForm.value.target) {
    ElMessage.error('请填写源术语和目标术语')
    return
  }
  
  terms.value.push({
    id: Date.now(),
    ...termForm.value
  })
  
  showTermDialog.value = false
  ElMessage.success('术语添加成功')
  
  termForm.value = {
    source: '',
    target: '',
    source_lang: 'en',
    target_lang: 'zh-CN'
  }
}

const deleteTerm = (term: any) => {
  terms.value = terms.value.filter(t => t.id !== term.id)
  ElMessage.success('删除成功')
}
</script>

<style scoped>
.translation-page {
  padding: 0;
}

.page-header-card {
  margin-bottom: 20px;
  border: none;
  border-radius: 8px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #1f2937;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.translate-card,
.result-card {
  height: 100%;
  border: none;
  border-radius: 8px;
}

.translated-text {
  min-height: 200px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  line-height: 1.8;
}

.empty-state {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.translation-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.terms-card {
  border: none;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
