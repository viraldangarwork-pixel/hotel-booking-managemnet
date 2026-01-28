/**
 * Formatting utility functions
 */
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

/**
 * Format currency
 */
export function formatCurrency(amount, currency = 'INR', locale = 'en-IN') {
  if (amount === null || amount === undefined) return '-'

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}

/**
 * Format date
 */
export function formatDate(date, format = 'DD MMM YYYY') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * Format datetime
 */
export function formatDateTime(date, format = 'DD MMM YYYY, h:mm A') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date) {
  if (!date) return '-'
  return dayjs(date).fromNow()
}

/**
 * Format phone number
 */
export function formatPhone(phone) {
  if (!phone) return '-'

  // Remove non-numeric except +
  const cleaned = phone.replace(/[^\d+]/g, '')

  // Format Indian number
  if (cleaned.startsWith('+91') && cleaned.length === 13) {
    return `+91 ${cleaned.slice(3, 8)} ${cleaned.slice(8)}`
  }

  // Format 10 digit number
  if (cleaned.length === 10) {
    return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`
  }

  return phone
}

/**
 * Mask email for privacy
 */
export function maskEmail(email) {
  if (!email || !email.includes('@')) return email

  const [local, domain] = email.split('@')
  const maskedLocal = local.length <= 2
    ? local[0] + '*'
    : local[0] + '*'.repeat(local.length - 2) + local.slice(-1)

  return `${maskedLocal}@${domain}`
}

/**
 * Mask phone for privacy
 */
export function maskPhone(phone) {
  if (!phone || phone.length < 6) return phone
  return phone.slice(0, 4) + '*'.repeat(phone.length - 6) + phone.slice(-2)
}

/**
 * Format number with commas
 */
export function formatNumber(num, locale = 'en-IN') {
  if (num === null || num === undefined) return '-'
  return new Intl.NumberFormat(locale).format(num)
}

/**
 * Format percentage
 */
export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toFixed(decimals)}%`
}

/**
 * Format file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Calculate nights between dates
 */
export function calculateNights(checkIn, checkOut) {
  if (!checkIn || !checkOut) return 0
  return dayjs(checkOut).diff(dayjs(checkIn), 'day')
}

/**
 * Get status badge class
 */
export function getStatusClass(status) {
  const statusClasses = {
    available: 'badge-success',
    booked: 'badge-info',
    checked_in: 'badge-warning',
    checked_out: 'badge-secondary',
    maintenance: 'badge-error',
    cleaning: 'badge-warning',
    pending: 'badge-warning',
    confirmed: 'badge-info',
    cancelled: 'badge-error',
    completed: 'badge-success',
  }

  return statusClasses[status?.toLowerCase()] || 'badge-secondary'
}

/**
 * Get status color for charts
 */
export function getStatusColor(status) {
  const colors = {
    available: '#10b981',
    booked: '#3b82f6',
    checked_in: '#f59e0b',
    checked_out: '#6b7280',
    maintenance: '#ef4444',
    cleaning: '#f97316',
  }

  return colors[status?.toLowerCase()] || '#6b7280'
}
