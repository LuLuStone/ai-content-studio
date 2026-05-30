import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCreateStore = defineStore('create', () => {
  const currentTaskId = ref<string | null>(null)
  const isCreating = ref(false)

  function setTaskId(id: string) {
    currentTaskId.value = id
    isCreating.value = true
  }

  function clearTask() {
    currentTaskId.value = null
    isCreating.value = false
  }

  return { currentTaskId, isCreating, setTaskId, clearTask }
})
