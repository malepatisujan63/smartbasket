'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  color: string;
  angle: number;
  velocity: number;
  rotation: number;
  rotationSpeed: number;
  shape: 'circle' | 'square' | 'strip';
  targetXOffset: number;
  duration: number;
  delay: number;
}

const COLORS = ['#FF6B00', '#1E3A8A', '#10B981', '#3B82F6', '#F59E0B', '#EC4899', '#8B5CF6'];

const Confetti: React.FC = () => {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    const newParticles: Particle[] = [];
    for (let i = 0; i < 80; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * 100, // percentage across screen width
        y: -10 - Math.random() * 30, // start above viewport
        size: Math.random() * 10 + 6,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        angle: (Math.random() - 0.5) * 60,
        velocity: Math.random() * 4 + 3,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 15,
        shape: Math.random() > 0.6 ? 'strip' : Math.random() > 0.3 ? 'square' : 'circle',
        targetXOffset: (Math.random() - 0.5) * 30,
        duration: Math.random() * 2.5 + 2,
        delay: Math.random() * 0.4,
      });
    }
    const rafId = requestAnimationFrame(() => {
      setParticles(newParticles);
    });
    return () => cancelAnimationFrame(rafId);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          initial={{
            left: `${p.x}vw`,
            top: `${p.y}vh`,
            rotate: p.rotation,
            opacity: 1,
            scale: 0,
          }}
          animate={{
            top: '105vh',
            left: `${p.x + p.targetXOffset}vw`,
            rotate: p.rotation + 720,
            opacity: [1, 1, 0.8, 0],
            scale: [0, 1, 1, 0.5],
          }}
          transition={{
            duration: p.duration,
            ease: [0.25, 0.46, 0.45, 0.94],
            delay: p.delay,
          }}
          style={{
            position: 'absolute',
            width: p.shape === 'strip' ? `${p.size * 0.5}px` : `${p.size}px`,
            height: p.shape === 'strip' ? `${p.size * 1.8}px` : `${p.size}px`,
            backgroundColor: p.color,
            borderRadius: p.shape === 'circle' ? '50%' : p.shape === 'square' ? '2px' : '4px',
            boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
          }}
        />
      ))}
    </div>
  );
};

export default Confetti;
