export const RSVP_EVENT_OPTIONS = [
  { key: 'attend_ceremony', label: 'Cerimonia' },
  { key: 'attend_lunch', label: 'Pranzo' }
]

export const ALLERGEN_OPTIONS = [
  { value: 'glutine', label: 'Glutine' },
  { value: 'lattosio', label: 'Lattosio' },
  { value: 'uova', label: 'Uova' },
  { value: 'arachidi', label: 'Arachidi' },
  { value: 'frutta_a_guscio', label: 'Frutta a guscio' },
  { value: 'soia', label: 'Soia' },
  { value: 'sesamo', label: 'Sesamo' },
  { value: 'pesce', label: 'Pesce' },
  { value: 'crostacei', label: 'Crostacei' },
  { value: 'molluschi', label: 'Molluschi' },
  { value: 'senape', label: 'Senape' },
  { value: 'sedano', label: 'Sedano' },
  { value: 'solfiti', label: 'Solfiti' }
]

export function getGuestAttendanceState(guest) {
  let ceremony = guest?.attend_ceremony ?? null
  let lunch = guest?.attend_lunch ?? null

  const hasNewFields = guest && ('attend_ceremony' in guest || 'attend_lunch' in guest)
  if (!hasNewFields || (ceremony === null && lunch === null)) {
    if (guest?.attendance_choice === 'ceremony') return { attend_ceremony: true, attend_lunch: false }
    if (guest?.attendance_choice === 'lunch') return { attend_ceremony: false, attend_lunch: true }
    if (guest?.attendance_choice === 'decline') return { attend_ceremony: false, attend_lunch: false }
    if (guest?.attending === true) return { attend_ceremony: true, attend_lunch: null }
    if (guest?.attending === false) return { attend_ceremony: false, attend_lunch: false }
  }

  return {
    attend_ceremony: ceremony,
    attend_lunch: lunch
  }
}

export function isGuestAttending(guest) {
  const state = getGuestAttendanceState(guest)
  return state.attend_ceremony === true || state.attend_lunch === true
}

export function isDeclinedState(state) {
  return state.attend_ceremony === false && state.attend_lunch === false
}

