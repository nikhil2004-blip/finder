import { useRef, useEffect, useState } from 'react';
import { useSprings, animated } from '@react-spring/web';

export const BlurText = ({
    text,
    delay = 200,
    className = '',
}: {
    text: string;
    delay?: number;
    className?: string;
}) => {
    const words = text.split(' ');
    const [inView, setInView] = useState(false);
    const ref = useRef<HTMLParagraphElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setInView(true);
                    observer.unobserve(ref.current!);
                }
            },
            { threshold: 0.1 }
        );

        if (ref.current) {
            observer.observe(ref.current);
        }

        return () => observer.disconnect();
    }, []);

    const springs = useSprings(
        words.length,
        words.map((_, i) => ({
            from: { filter: 'blur(10px)', opacity: 0, transform: 'translate3d(0,-50px,0)' },
            to: inView
                ? async (next) => {
                    await next({ filter: 'blur(5px)', opacity: 0.5, transform: 'translate3d(0,5px,0)' });
                    await next({ filter: 'blur(0px)', opacity: 1, transform: 'translate3d(0,0,0)' });
                }
                : { filter: 'blur(10px)', opacity: 0, transform: 'translate3d(0,-50px,0)' },
            delay: i * delay,
            config: { mass: 1, tension: 280, friction: 60 }, // spring config
        }))
    );

    return (
        <p ref={ref} className={`${className} flex flex-wrap gap-2`}>
            {springs.map((props, index) => (
                <animated.span key={index} style={props} className="inline-block will-change-transform">
                    {words[index]}&nbsp;
                </animated.span>
            ))}
        </p>
    );
};
