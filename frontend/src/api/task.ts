import http from './http'

export interface TaskStatus {
  task_id: string
  type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
  result_id?: string
  error_message?: string
  step_data?: Record<string, any>
  created_at?: string
  updated_at?: string
}

export function getTaskStatus(taskId: string): Promise<TaskStatus> {
  return http.get(`/tasks/${taskId}`)
}

export function getActiveTasks(): Promise<TaskStatus[]> {
  return http.get('/tasks/active')
}
