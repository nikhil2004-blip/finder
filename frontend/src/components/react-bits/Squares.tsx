import { useRef, useEffect, useState } from 'react';

interface SquaresProps {
    direction?: 'diagonal' | 'up' | 'down' | 'left' | 'right';
    speed?: number;
    squareSize?: number;
    borderColor?: string;
    hoverFillColor?: string;
}

export const Squares = ({
    direction = 'diagonal',
    speed = 0.5,
    squareSize = 40,
    borderColor = '#333',
    hoverFillColor = '#222'
}: SquaresProps) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();
    const numSquaresX = useRef<number>(0);
    const numSquaresY = useRef<number>(0);
    const gridOffset = useRef<{ x: number, y: number }>({ x: 0, y: 0 });
    const [hoveredSquare, setHoveredSquare] = useState<{ x: number, y: number } | null>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const resizeCanvas = () => {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            numSquaresX.current = Math.ceil(canvas.width / squareSize) + 1;
            numSquaresY.current = Math.ceil(canvas.height / squareSize) + 1;
        };

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const animate = () => {
            if (!ctx || !canvas) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Move grid
            switch (direction) {
                case 'right': gridOffset.current.x = (gridOffset.current.x - speed) % squareSize; break;
                case 'left': gridOffset.current.x = (gridOffset.current.x + speed) % squareSize; break;
                case 'up': gridOffset.current.y = (gridOffset.current.y + speed) % squareSize; break;
                case 'down': gridOffset.current.y = (gridOffset.current.y - speed) % squareSize; break;
                case 'diagonal':
                    gridOffset.current.x = (gridOffset.current.x - speed) % squareSize;
                    gridOffset.current.y = (gridOffset.current.y - speed) % squareSize;
                    break;
            }

            const startX = Math.floor(gridOffset.current.x);
            const startY = Math.floor(gridOffset.current.y);

            ctx.lineWidth = 1;

            for (let x = 0; x < numSquaresX.current; x++) {
                for (let y = 0; y < numSquaresY.current; y++) {
                    const squareX = x * squareSize + startX;
                    const squareY = y * squareSize + startY;

                    // Draw Hover effect
                    if (hoveredSquare &&
                        Math.floor((hoveredSquare.x - startX) / squareSize) === x &&
                        Math.floor((hoveredSquare.y - startY) / squareSize) === y) {
                        ctx.fillStyle = hoverFillColor;
                        ctx.fillRect(squareX, squareY, squareSize, squareSize);
                    }

                    ctx.strokeStyle = borderColor;
                    ctx.strokeRect(squareX, squareY, squareSize, squareSize);
                }
            }

            requestRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            if (requestRef.current) cancelAnimationFrame(requestRef.current);
        };
    }, [direction, speed, squareSize, borderColor, hoverFillColor, hoveredSquare]);

    const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
        const rect = canvasRef.current?.getBoundingClientRect();
        if (rect) {
            setHoveredSquare({
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            });
        }
    };

    const handleMouseLeave = () => {
        setHoveredSquare(null);
    }

    return (
        <canvas
            ref={canvasRef}
            className="w-full h-full block"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        />
    );
};
