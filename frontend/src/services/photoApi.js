import axios from 'axios'

const api = axios.create({
  baseURL: '/api/photos',
})

/**
 * Upload a photo to the gallery.
 * @param {File} file - Image file to upload
 * @param {string|null} uploaderName - Name of the uploader
 * @param {string|null} caption - Optional caption
 * @param {Function} onProgress - Progress callback (0-100)
 * @returns {Promise<Object>} Uploaded photo data
 */
export async function uploadPhoto(file, uploaderName, caption, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  if (uploaderName) formData.append('uploader_name', uploaderName)
  if (caption) formData.append('caption', caption)

  const { data } = await api.post('', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
  return data
}

/**
 * Fetch paginated list of photos (newest first).
 * @param {number} page - Page number (1-indexed)
 * @param {number} perPage - Items per page
 * @param {string|null} search - Optional search string to filter by name/caption
 * @returns {Promise<Object>} PhotoListResponse with photos array and pagination
 */
export async function getPhotos(page = 1, perPage = 20, search = null) {
  const params = { page, per_page: perPage }
  if (search) params.search = search
  const { data } = await api.get('', { params })
  return data
}
