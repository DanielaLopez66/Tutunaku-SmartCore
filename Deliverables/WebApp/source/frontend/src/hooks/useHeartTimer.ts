import { useState, useEffect } from 'react'

export function useHeartTimer(hearts: number, lastRefill?: string) {
  const [timeLeft, setTimeLeft] = useState<string | null>(null)

  useEffect(() => {
    if (hearts >= 5 || !lastRefill) {
      setTimeLeft(null)
      return
    }

    const updateTimer = () => {
      // MySQL DATETIME returns naive time without Z. Force it to be UTC.
      const refStr = lastRefill.endsWith('Z') || lastRefill.includes('+') ? lastRefill : lastRefill + 'Z'
      const refillTime = new Date(refStr).getTime() + 60 * 60 * 1000
      const now = Date.now()
      const diff = refillTime - now

      if (diff <= 0) {
        setTimeLeft('00:00')
      } else {
        const m = Math.floor(diff / 60000)
        const s = Math.floor((diff % 60000) / 1000)
        setTimeLeft(`${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`)
      }
    }

    updateTimer()
    const interval = setInterval(updateTimer, 1000)
    return () => clearInterval(interval)
  }, [hearts, lastRefill])

  return timeLeft
}
