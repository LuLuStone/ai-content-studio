import http from './http'

export interface PodcastListItem {
  id: string
  title: string
  description?: string
  duration_seconds?: number
  speaker_count: number
  style?: string
  status: string
  created_at: string
}

export interface PodcastDetail {
  id: string
  title: string
  description?: string
  original_input: string
  script_json: any
  speakers_json: any[]
  audio_file_path?: string
  duration_seconds?: number
  speaker_count: number
  style?: string
  status: string
  created_at: string
  updated_at: string
}

export function getPodcasts(page = 1, pageSize = 20): Promise<PodcastListItem[]> {
  return http.get('/podcasts', { params: { page, page_size: pageSize } })
}

export function getPodcast(id: string): Promise<PodcastDetail> {
  return http.get(`/podcasts/${id}`)
}

export function deletePodcast(id: string): Promise<void> {
  return http.delete(`/podcasts/${id}`)
}

export function getPodcastAudioUrl(id: string): string {
  return `/api/podcasts/${id}/audio`
}
