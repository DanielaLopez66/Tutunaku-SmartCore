// ============================================================
// TUTUNAKU — Corazón Saltarín
// Corazón juguetón con diseño animado y original
// ============================================================
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

interface Props {
  size?: number
  animated?: boolean
  className?: string
}

export default function CorazonSaltarin({ size = 80, animated = true, className = '' }: Props) {
  const [isWinking, setIsWinking] = useState(false)
  const [showHearts, setShowHearts] = useState(false)
  const [isHappy, setIsHappy] = useState(false)

  // Efecto para el parpadeo cada 3 segundos
  useEffect(() => {
    const winkInterval = setInterval(() => {
      setIsWinking(true)
      setTimeout(() => setIsWinking(false), 200)
    }, 3000)

    return () => clearInterval(winkInterval)
  }, [])

  // Efecto para cambio de estado feliz aleatorio
  useEffect(() => {
    const happyInterval = setInterval(() => {
      setIsHappy(true)
      setTimeout(() => setIsHappy(false), 1000)
    }, 8000)

    return () => clearInterval(happyInterval)
  }, [])

  const Wrapper = animated ? motion.div : 'div'
  const wrapperProps = animated
    ? {
        onHoverStart: () => setShowHearts(true),
        onHoverEnd: () => setShowHearts(false),
        whileHover: { 
          scale: 1.15,
          rotate: [0, -5, 5, -5, 0],
          transition: { duration: 0.5 }
        },
        animate: { 
          y: [0, -8, 0, -4, 0],
          rotate: isHappy ? [0, -3, 3, -3, 0] : 0,
          scale: isHappy ? [1, 1.1, 1] : 1
        },
        transition: {
          y: { duration: 3, repeat: Infinity, ease: "easeInOut" },
          rotate: { duration: 0.5 },
          scale: { duration: 0.5 }
        }
      }
    : {}

  return (
    <Wrapper 
      {...wrapperProps} 
      className={`relative inline-block cursor-pointer ${className}`}
    >
      {/* Corazones y estrellas al hacer hover */}
      <AnimatePresence>
        {showHearts && (
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ 
                  x: size/2 - 10, 
                  y: size/2 - 10, 
                  scale: 0,
                  opacity: 1,
                  rotate: 0
                }}
                animate={{ 
                  x: size/2 - 10 + (Math.random() - 0.5) * 150,
                  y: -30 - Math.random() * 50,
                  scale: 0.5 + Math.random(),
                  opacity: 0,
                  rotate: Math.random() * 360
                }}
                exit={{ opacity: 0 }}
                transition={{ 
                  duration: 1.2,
                  delay: i * 0.1,
                  ease: "easeOut"
                }}
                className="absolute"
                style={{
                  left: 0,
                  top: 0,
                  filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.1))'
                }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="#FF6B6B">
                  <path d="M12 21s-6.7-4.35-9.3-8.1C.8 10.1 1.4 6.6 4.2 5.1c2.1-1.1 4.4-.4 5.8 1.3.5.6 1.5.6 2 0 1.4-1.7 3.7-2.4 5.8-1.3 2.8 1.5 3.4 5 1.5 7.8C18.7 16.65 12 21 12 21z" />
                </svg>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>

      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="Corazón saltarín"
      >
        {/* Sombra más dinámica */}
        <ellipse cx="50" cy="94" rx="28" ry="6" fill="rgba(0,0,0,0.1)" />
        
        {/* Capa de brillo detrás */}
        <circle cx="50" cy="40" r="32" fill="url(#glowGrad)" opacity="0.3" />

        {/* Cuerpo del corazón - forma más caricaturesca */}
        <path
          d="M50 86 C50 86 8 58 8 30 C8 14 22 4 36 4 C44 4 48 10 50 16 
             C52 10 56 4 64 4 C78 4 92 14 92 30 C92 58 50 86 50 86Z"
          fill="url(#heartGrad)"
          stroke="white"
          strokeWidth="3"
        />

        {/* Reflejos brillantes */}
        <ellipse cx="35" cy="25" rx="8" ry="4" fill="white" opacity="0.3" transform="rotate(-20 35 25)" />
        <ellipse cx="65" cy="25" rx="8" ry="4" fill="white" opacity="0.2" transform="rotate(20 65 25)" />

        {/* Marco decorativo alrededor */}
        <path
          d="M50 82 C50 82 14 56 14 32 C14 18 26 10 38 10 C44 10 47 14 50 19 
             C53 14 56 10 62 10 C74 10 86 18 86 32 C86 56 50 82 50 82Z"
          fill="none"
          stroke="white"
          strokeWidth="1.5"
          strokeDasharray="4 4"
          opacity="0.5"
        />

        {/* Ojos grandes y expresivos */}
        <g>
          {/* Ojo izquierdo */}
          <circle cx="35" cy="45" r="9" fill="white" stroke="#FF4D4D" strokeWidth="2" />
          <circle cx="35" cy="45" r="5.5" fill="#2D3436" />
          <circle cx="37.5" cy="42.5" r="2" fill="white" />
          {/* Brillo extra */}
          <circle cx="32" cy="42" r="1.2" fill="white" opacity="0.8" />
          
          
          {/* Parpadeo izquierdo */}
          <AnimatePresence>
            {isWinking && (
              <motion.path
                d="M27 45 L43 45"
                stroke="#2D3436"
                strokeWidth="4"
                strokeLinecap="round"
                initial={{ scaleY: 0, opacity: 0 }}
                animate={{ scaleY: 1, opacity: 1 }}
                exit={{ scaleY: 0, opacity: 0 }}
                transition={{ duration: 0.1 }}
              />
            )}
          </AnimatePresence>
        </g>

        <g>
          {/* Ojo derecho */}
          <circle cx="65" cy="45" r="9" fill="white" stroke="#FF4D4D" strokeWidth="2" />
          <circle cx="65" cy="45" r="5.5" fill="#2D3436" />
          <circle cx="67.5" cy="42.5" r="2" fill="white" />
          {/* Brillo extra */}
          <circle cx="62" cy="42" r="1.2" fill="white" opacity="0.8" />
          

          
          {/* Parpadeo derecho */}
          <AnimatePresence>
            {isWinking && (
              <motion.path
                d="M57 45 L73 45"
                stroke="#2D3436"
                strokeWidth="4"
                strokeLinecap="round"
                initial={{ scaleY: 0, opacity: 0 }}
                animate={{ scaleY: 1, opacity: 1 }}
                exit={{ scaleY: 0, opacity: 0 }}
                transition={{ duration: 0.1 }}
              />
            )}
          </AnimatePresence>
        </g>

        {/* Mejillas sonrosadas grandes */}
        <circle cx="25" cy="60" r="7" fill="#FFB6C1" opacity="0.5" />
        <circle cx="25" cy="60" r="4" fill="#FF9AAC" opacity="0.3" />
        <circle cx="75" cy="60" r="7" fill="#FFB6C1" opacity="0.5" />
        <circle cx="75" cy="60" r="4" fill="#FF9AAC" opacity="0.3" />

        {/* Corazoncitos decorativos en las mejillas */}
        <path
          d="M5 8.5C5 8.5 1 5.8 1 3.3C1 1.9 2.1 1 3.3 1C4 1 4.6 1.4 5 2C5.4 1.4 6 1 6.7 1C7.9 1 9 1.9 9 3.3C9 5.8 5 8.5 5 8.5Z"
          fill="#FF4D4D" opacity="0.6" transform="translate(19,59) scale(0.6)"
        />
        <path
          d="M5 8.5C5 8.5 1 5.8 1 3.3C1 1.9 2.1 1 3.3 1C4 1 4.6 1.4 5 2C5.4 1.4 6 1 6.7 1C7.9 1 9 1.9 9 3.3C9 5.8 5 8.5 5 8.5Z"
          fill="#FF4D4D" opacity="0.6" transform="translate(69,59) scale(0.6)"
        />

        {/* Ceja izquierda animada */}
        <motion.path
          d="M27 33 Q32 28 37 33"
          stroke="#2D3436"
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
          animate={isHappy ? { d: "M27 28 Q32 23 37 28" } : { d: "M27 33 Q32 28 37 33" }}
          transition={{ duration: 0.3 }}
        />

        {/* Ceja derecha animada */}
        <motion.path
          d="M57 33 Q62 28 67 33"
          stroke="#2D3436"
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
          animate={isHappy ? { d: "M57 28 Q62 23 67 28" } : { d: "M57 33 Q62 28 67 33" }}
          transition={{ duration: 0.3 }}
        />

        {/* Estrellitas brillantes alrededor */}
        <circle cx="85" cy="20" r="2" fill="#FFD700" opacity="0.8">
          <animate
            attributeName="opacity"
            values="0.8;1;0.8"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="15" cy="20" r="1.5" fill="#FFD700" opacity="0.8">
          <animate
            attributeName="opacity"
            values="0.8;1;0.8"
            dur="1.5s"
            repeatCount="indefinite"
          />
        </circle>

        {/* Gradientes */}
        <defs>
          <linearGradient id="heartGrad" x1="8" y1="4" x2="92" y2="86" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FF6B6B" />
            <stop offset="30%" stopColor="#FF4D4D" />
            <stop offset="70%" stopColor="#E63946" />
            <stop offset="100%" stopColor="#C41E3A" />
          </linearGradient>
          <radialGradient id="glowGrad" cx="50" cy="40" r="32" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFB6C1" stopOpacity="0.4" />
            <stop offset="70%" stopColor="#FF69B4" stopOpacity="0.1" />
            <stop offset="100%" stopColor="#FF4D4D" stopOpacity="0" />
          </radialGradient>
        </defs>
      </svg>
    </Wrapper>
  )
}