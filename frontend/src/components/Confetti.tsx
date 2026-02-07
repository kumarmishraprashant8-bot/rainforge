/**
 * Confetti Component
 * Celebration animation for achievements
 */

import { useEffect, useState } from 'react';

interface ConfettiPiece {
    id: number;
    x: number;
    color: string;
    delay: number;
    duration: number;
}

interface ConfettiProps {
    isActive: boolean;
    duration?: number;
}

const COLORS = ['#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

const Confetti = ({ isActive, duration = 3000 }: ConfettiProps) => {
    const [pieces, setPieces] = useState<ConfettiPiece[]>([]);

    useEffect(() => {
        if (isActive) {
            const newPieces: ConfettiPiece[] = [];
            for (let i = 0; i < 50; i++) {
                newPieces.push({
                    id: i,
                    x: Math.random() * 100,
                    color: COLORS[Math.floor(Math.random() * COLORS.length)],
                    delay: Math.random() * 0.5,
                    duration: 2 + Math.random() * 2,
                });
            }
            setPieces(newPieces);

            const timer = setTimeout(() => {
                setPieces([]);
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [isActive, duration]);

    if (!isActive || pieces.length === 0) return null;

    return (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
            {pieces.map((piece) => (
                <div
                    key={piece.id}
                    className="absolute w-3 h-3 animate-confetti"
                    style={{
                        left: `${piece.x}%`,
                        top: '-20px',
                        backgroundColor: piece.color,
                        animationDelay: `${piece.delay}s`,
                        animationDuration: `${piece.duration}s`,
                        borderRadius: Math.random() > 0.5 ? '50%' : '0',
                        transform: `rotate(${Math.random() * 360}deg)`,
                    }}
                />
            ))}
            <style>{`
                @keyframes confetti {
                    0% {
                        transform: translateY(0) rotate(0deg);
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(100vh) rotate(720deg);
                        opacity: 0;
                    }
                }
                .animate-confetti {
                    animation: confetti linear forwards;
                }
            `}</style>
        </div>
    );
};

export default Confetti;
