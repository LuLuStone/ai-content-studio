import http from './http'

export interface ImageListItem {
  id: string
  title: string
  image_file_path?: string
  style?: string
  status: string
  created_at: string
}

export interface ImageDetail {
  id: string
  title: string
  original_input: string
  prompt_cn?: string
  prompt_en?: string
  image_file_path?: string
  style?: string
  aspect_ratio?: string
  status: string
  created_at: string
  updated_at: string
}

export function getImages(page = 1, pageSize = 20): Promise<ImageListItem[]> {
  return http.get('/images', { params: { page, page_size: pageSize } })
}

export function getImage(id: string): Promise<ImageDetail> {
  return http.get(`/images/${id}`)
}

export function deleteImage(id: string): Promise<void> {
  return http.delete(`/images/${id}`)
}
