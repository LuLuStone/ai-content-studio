import http from './http'

export interface AudiobookListItem {
  id: string
  title: string
  duration_seconds?: number
  mode: string
  status: string
  created_at: string
}

export interface AudiobookDetail {
  id: string
  title: string
  original_input: string
  script_json?: any
  characters_json?: any[]
  audio_file_path?: string
  duration_seconds?: number
  mode: string
  status: string
  created_at: string
  updated_at: string
}

export function getAudiobooks(page = 1, pageSize = 20): Promise<AudiobookListItem[]> {
  return http.get('/audiobooks', { params: { page, page_size: pageSize } })
}

export function getAudiobook(id: string): Promise<AudiobookDetail> {
  return http.get(`/audiobooks/${id}`)
}

export function deleteAudiobook(id: string): Promise<void> {
  return http.delete(`/audiobooks/${id}`)
}

export function getAudiobookAudioUrl(id: string): string {
  return `/api/audiobooks/${id}/audio`
}
