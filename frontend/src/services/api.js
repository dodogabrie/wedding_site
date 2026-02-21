import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

function maybeShowVoteWarning(headers) {
  const warning = headers?.['x-rsvp-warning']
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
export async function updateGuest(guestId, update) {
  const { data, headers } = await api.patch(`/guests/${guestId}`, update)
  maybeShowVoteWarning(headers)
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

export default api
