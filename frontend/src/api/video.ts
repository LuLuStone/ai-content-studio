import http from './http'

export interface VideoListItem {
  id: string
  title: string
  duration_seconds?: number
  style?: string
  status: string
  created_at: string
}

export interface VideoDetail {
  id: string
  title: string
  original_input: string
  script_json?: any
  video_file_path?: string
  thumbnail_path?: string
  duration_seconds?: number
  style?: string
  status: string
  created_at: string
  updated_at: string
}

export function getVideos(page = 1, pageSize = 20): Promise<VideoListItem[]> {
  return http.get('/videos', { params: { page, page_size: pageSize } })
}

export function getVideo(id: string): Promise<VideoDetail> {
  return http.get(`/videos/${id}`)
}

export function deleteVideo(id: string): Promise<void> {
  return http.delete(`/videos/${id}`)
}
