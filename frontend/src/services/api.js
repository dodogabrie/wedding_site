import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

function getVoteWarning(headers) {
  return headers?.['x-rsvp-warning'] || ''
}

function maybeShowVoteWarning(headers) {
  const warning = getVoteWarning(headers)
  if (warning) {
    window.alert(warning)
  }
}

/**
 * Fetch all families with their guests.
 * @returns {Promise<Array>} List of families with nested guests
 */
export async function getFamilies() {
  const { data } = await api.get('/families')
  return data
}

/**
 * Fetch all individual guests (those without a family).
 * @returns {Promise<Array>} List of individual guests
 */
export async function getGuests() {
  const { data } = await api.get('/guests')
  return data
}

/**
 * Update a single guest's RSVP status.
 * @param {number} guestId - The guest's ID
 * @param {Object} update - Object with attending (bool|null) and optional dietary_notes
 * @returns {Promise<Object>} Updated guest data
 */
export async function updateGuest(guestId, update, options = {}) {
  const { data, headers } = await api.patch(`/guests/${guestId}`, update)
  const warning = getVoteWarning(headers)
  if (!options.suppressWarningAlert && warning) {
    window.alert(warning)
  }
  if (options.returnMeta) {
    return { data, warning, headers }
  }
  return data
}

/**
 * Bulk update attendance for all guests in a family.
 * @param {number} familyId - The family's ID
 * @param {Object} guestUpdates - Object mapping guest_id to attending status
 * @returns {Promise<Object>} Updated family data with guests
 */
export async function updateFamilyGuests(familyId, guestUpdates) {
  const { data, headers } = await api.patch(`/families/${familyId}/guests`, {
    guest_updates: guestUpdates
  })
  maybeShowVoteWarning(headers)
  return data
}

/**
 * Get RSVP statistics.
 * @returns {Promise<Object>} Stats with total_guests, confirmed, declined, pending
 */
export async function getStats() {
  const { data } = await api.get('/rsvp/stats')
  return data
}

/**
 * Admin API methods
 */
const adminHeaders = () => ({
  'X-Admin-Password': sessionStorage.getItem('admin_password')
})

export const adminApi = {
  /**
   * Get all families and individual guests with full details.
   */
  getData: async () => {
    const { data } = await api.get('/admin/data', { headers: adminHeaders() })
    return data
  },

  /**
   * Administratively update a guest's details.
   */
  updateGuest: async (guestId, update) => {
    const { data } = await api.patch(`/admin/guests/${guestId}`, update, { headers: adminHeaders() })
    return data
  },

  /**
   * Create a new guest.
   */
  createGuest: async (guestData) => {
    const { data } = await api.post('/admin/guests', guestData, { headers: adminHeaders() })
    return data
  },

  /**
   * Remove a guest from the list.
   */
  deleteGuest: async (guestId) => {
    await api.delete(`/admin/guests/${guestId}`, { headers: adminHeaders() })
  },

  /**
   * Create a new family group.
   */
  createFamily: async (familyData) => {
    const { data } = await api.post('/admin/families', familyData, { headers: adminHeaders() })
    return data
  },

  /**
   * Update family details.
   */
  updateFamily: async (familyId, update) => {
    const { data } = await api.patch(`/admin/families/${familyId}`, update, { headers: adminHeaders() })
    return data
  },

  /**
   * Delete a family group.
   */
  deleteFamily: async (familyId) => {
    await api.delete(`/admin/families/${familyId}`, { headers: adminHeaders() })
  }
}

export default api
