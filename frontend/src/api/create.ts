import http from './http'

export interface CreateRequest {
  input_text: string
  type: 'podcast' | 'audiobook' | 'video' | 'image'
  options: Record<string, any>
}

export interface CreateResponse {
  task_id: string
  status: string
  message: string
}

export function createContent(data: CreateRequest): Promise<CreateResponse> {
  return http.post('/create', data)
}

// 统一获取所有创作列表（用于创作列表页）
export interface CreationItem {
  id: string
  title: string
  description?: string
  _type: 'podcast' | 'audiobook' | 'video' | 'image'
  duration_seconds?: number
  style?: string
  mode?: string
  speaker_count?: number
  image_file_path?: string
  status: string
  created_at: string
}

export async function getAllCreations(params: {
  page?: number
  page_size?: number
  type?: string
  keyword?: string
}): Promise<{ items: CreationItem[]; total: number }> {
  const { page = 1, page_size = 20, type = '', keyword = '' } = params

  // 并行请求四个接口
  const requests: Promise<any[]>[] = []
  const types = type ? [type] : ['podcast', 'audiobook', 'video', 'image']

  if (types.includes('podcast')) requests.push(http.get('/podcasts', { params: { page, page_size } }).catch(() => []))
  if (types.includes('audiobook')) requests.push(http.get('/audiobooks', { params: { page, page_size } }).catch(() => []))
  if (types.includes('video')) requests.push(http.get('/videos', { params: { page, page_size } }).catch(() => []))
  if (types.includes('image')) requests.push(http.get('/images', { params: { page, page_size } }).catch(() => []))

  const results = await Promise.all(requests)

  let allItems: CreationItem[] = []
  const typeMap: Record<string, string> = { podcast: 'podcast', audiobook: 'audiobook', video: 'video', image: 'image' }
  let idx = 0

  for (const t of types) {
    const items = (results[idx] || []).map((item: any) => ({ ...item, _type: t }))
    allItems = allItems.concat(items)
    idx++
  }

  // 关键字过滤
  if (keyword) {
    const kw = keyword.toLowerCase()
    allItems = allItems.filter(item => item.title.toLowerCase().includes(kw))
  }

  // 按时间排序
  allItems.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  // 客户端分页（因为数据量不大）
  const total = allItems.length
  const start = (page - 1) * page_size
  const items = allItems.slice(start, start + page_size)

  return { items, total }
}
