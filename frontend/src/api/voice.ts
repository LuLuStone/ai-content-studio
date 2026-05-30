import http from './http'

export interface VoiceItem {
  id: string
  name: string
  description: string | null
  sample_duration: string | null
  preview_file_path: string | null
  created_at: string
}

export interface PresetVoice {
  id: string
  name: string
  description: string
  gender: string
  lang: string
  has_preview: boolean
}

export interface VoiceDetail extends VoiceItem {
  sample_file_path: string
  updated_at: string
}

// ===== 预置音色 =====

/** 获取预置音色列表 */
export function getPresetVoices(): Promise<PresetVoice[]> {
  return http.get('/voices/presets')
}

/** 试听预置音色 */
export function previewPresetVoice(voiceId: string, force: boolean = false): Promise<Blob> {
  return http.post(`/voices/presets/${voiceId}/preview?force=${force}`, null, { responseType: 'blob' })
}

/** 获取预置音色试听缓存 URL */
export function getPresetAudioUrl(voiceId: string): string {
  return `/api/voices/presets/${voiceId}/audio`
}

// ===== 自定义音色 =====

/** 获取自定义音色列表 */
export function getVoices(): Promise<VoiceItem[]> {
  return http.get('/voices')
}

/** 上传音色 */
export async function createVoice(name: string, description: string, file: File): Promise<VoiceDetail> {
  const formData = new FormData()
  formData.append('name', name)
  formData.append('description', description)
  formData.append('file', file)
  return http.post('/voices', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 重命名音色 */
export function renameVoice(voiceId: string, name: string, description?: string): Promise<VoiceDetail> {
  return http.patch(`/voices/${voiceId}`, { name, description })
}

/** 试听自定义音色 */
export function previewVoice(voiceId: string, force: boolean = false): Promise<Blob> {
  return http.post(`/voices/${voiceId}/preview?force=${force}`, null, { responseType: 'blob' })
}

/** 获取音色样本 URL */
export function getVoiceSampleUrl(voiceId: string): string {
  return `/api/voices/${voiceId}/sample`
}

/** 删除音色 */
export function deleteVoice(voiceId: string): Promise<any> {
  return http.delete(`/voices/${voiceId}`)
}
