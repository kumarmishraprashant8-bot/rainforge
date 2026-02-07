/**
 * Scroll Animations Hook
 * Animate elements when they enter the viewport
 */

import { useEffect, useRef, useState } from 'react';
import type { RefObject } from 'react';

interface UseScrollAnimationOptions {
    threshold?: number;
    rootMargin?: string;
    triggerOnce?: boolean;
}

export function useScrollAnimation<T extends HTMLElement = HTMLDivElement>(
    options: UseScrollAnimationOptions = {}
): { ref: RefObject<T>; isVisible: boolean; hasAnimated: boolean } {
    const { threshold = 0.1, rootMargin = '0px', triggerOnce = true } = options;

    const ref = useRef<T>(null);
    const [isVisible, setIsVisible] = useState(false);
    const [hasAnimated, setHasAnimated] = useState(false);

    useEffect(() => {
        const element = ref.current;
        if (!element) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    setHasAnimated(true);
                    if (triggerOnce) {
                        observer.disconnect();
                    }
                } else if (!triggerOnce) {
                    setIsVisible(false);
                }
            },
            { threshold, rootMargin }
        );

        observer.observe(element);
        return () => observer.disconnect();
    }, [threshold, rootMargin, triggerOnce]);

    return { ref: ref as RefObject<T>, isVisible, hasAnimated };
}

/**
 * Animated Section Wrapper
 */
export const AnimatedSection: React.FC<{
    children: React.ReactNode;
    className?: string;
    animation?: 'fade-in' | 'fade-in-up' | 'slide-in-right' | 'scale-in';
    delay?: number;
}> = ({ children, className = '', animation = 'fade-in-up', delay = 0 }) => {
    const { ref, isVisible } = useScrollAnimation();

    const animationClasses: Record<string, string> = {
        'fade-in': 'animate-fade-in',
        'fade-in-up': 'animate-fade-in-up',
        'slide-in-right': 'animate-slide-in-right',
        'scale-in': 'animate-scale-in',
    };

    return (
        <div
            ref={ref}
            className={`${className} ${isVisible ? animationClasses[animation] : 'opacity-0'}`}
            style={{ animationDelay: `${delay}ms` }}
        >
            {children}
        </div>
    );
};

/**
 * Staggered animation for lists
 */
export const StaggeredList: React.FC<{
    children: React.ReactNode[];
    className?: string;
    itemClassName?: string;
    staggerDelay?: number;
}> = ({ children, className = '', itemClassName = '', staggerDelay = 100 }) => {
    const { ref, isVisible } = useScrollAnimation();

    return (
        <div ref={ref} className={className}>
            {children.map((child, index) => (
                <div
                    key={index}
                    className={`${itemClassName} ${isVisible ? 'animate-fade-in-up' : 'opacity-0'}`}
                    style={{ animationDelay: `${index * staggerDelay}ms` }}
                >
                    {child}
                </div>
            ))}
        </div>
    );
};

/**
 * Parallax scroll effect
 */
export function useParallax(speed: number = 0.5) {
    const ref = useRef<HTMLDivElement>(null);
    const [offset, setOffset] = useState(0);

    useEffect(() => {
        const handleScroll = () => {
            if (!ref.current) return;
            const rect = ref.current.getBoundingClientRect();
            const scrolled = window.innerHeight - rect.top;
            setOffset(scrolled * speed);
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, [speed]);

    return { ref, offset };
}

/**
 * Counter animation for numbers
 */
export function useCountUp(
    end: number,
    duration: number = 2000,
    start: number = 0
): { ref: RefObject<HTMLSpanElement | null>; value: number } {
    const ref = useRef<HTMLSpanElement>(null);
    const [value, setValue] = useState(start);
    const { isVisible } = useScrollAnimation();

    useEffect(() => {
        if (!isVisible) return;

        const startTime = Date.now();
        const difference = end - start;

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease-out function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = start + difference * easeOut;

            setValue(Math.round(currentValue));

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [isVisible, end, duration, start]);

    return { ref, value };
}

export default useScrollAnimation;
