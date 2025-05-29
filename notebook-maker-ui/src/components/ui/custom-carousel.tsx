"use client";

import React, { useState, useEffect } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface CarouselItemProps extends React.HTMLAttributes<HTMLDivElement> {
  isActive?: boolean;
  isNext?: boolean;
  isPrev?: boolean;
}

interface CustomCarouselProps {
  children: React.ReactNode;
  className?: string;
  autoPlay?: boolean;
  autoPlayInterval?: number;
  onChangeIndex?: (index: number) => void;
  currentIndex?: number;
}

export function CustomCarousel({
  children,
  className,
  autoPlay = false,
  autoPlayInterval = 3000,
  onChangeIndex,
  currentIndex,
}: CustomCarouselProps) {
  const [currentIndexState, setCurrentIndexState] = useState(currentIndex ?? 0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const childrenArray = React.Children.toArray(children);
  const totalItems = childrenArray.length;

  useEffect(() => {
    if (typeof currentIndex === "number" && currentIndex !== currentIndexState) {
      setCurrentIndexState(currentIndex);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentIndex]);

  // Ensure proper indexing with looping
  const normalizedIndex = ((currentIndexState % totalItems) + totalItems) % totalItems;

  // Check for mobile viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640);
    };
    
    // Initial check
    checkMobile();
    
    // Add resize listener
    window.addEventListener('resize', checkMobile);
    
    // Cleanup
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (onChangeIndex) {
      onChangeIndex(normalizedIndex);
    }
  }, [normalizedIndex, onChangeIndex]);

  // Autoplay logic
  const handleNextClick = React.useCallback(() => {
    if (isAnimating) return;
    setIsAnimating(true);
    setCurrentIndexState(prev => (prev + 1) % totalItems);
    setTimeout(() => setIsAnimating(false), 300); // Match transition duration
  }, [isAnimating, totalItems]);

  useEffect(() => {
    if (!autoPlay) return;

    const interval = setInterval(() => {
      handleNextClick();
    }, autoPlayInterval);

    return () => clearInterval(interval);
  }, [autoPlay, autoPlayInterval, handleNextClick]);

  const handlePrevClick = React.useCallback(() => {
    if (isAnimating) return;
    setIsAnimating(true);
    setCurrentIndexState(prev => (prev - 1 + totalItems) % totalItems);
    setTimeout(() => setIsAnimating(false), 300); // Match transition duration
  }, [isAnimating, totalItems]);

  // Calculate the position of each item relative to the current index
  const renderItems = () => {
    return childrenArray.map((child, index) => {
      // Calculate the position of this item relative to current
      let position = (index - normalizedIndex);
      if (position < -Math.floor(totalItems / 2)) position += totalItems;
      if (position > Math.floor(totalItems / 2)) position -= totalItems;
      
      // Calculate visual properties based on position
      const isActive = index === normalizedIndex;
      const isNext = position === 1;
      const isPrev = position === -1;
      
      // Calculate transform and styles
      let scale = 1;
      let opacity = 1;
      let zIndex = 10 - Math.abs(position);
      let width = "33.3%";
      let left = "33.3%";
      
      if (isMobile) {
        // For mobile, only show active item
        if (isActive) {
          width = "90%";
          left = "5%";
          scale = 1;
          opacity = 1;
          zIndex = 10;
        } else {
          // Hide all non-active items on mobile
          opacity = 0;
          zIndex = 1;
          // Position next and prev items for animation
          if (isNext) {
            left = "100%";
          } else if (isPrev) {
            left = "-100%";
          }
        }
      } else {
        // For desktop
        if (isActive) {
          width = "40%";
          left = "30%";
          scale = 1;
          opacity = 1;
          zIndex = 10;
        } else if (isNext) {
          width = "30%";
          left = "70%";
          scale = 0.9;
          opacity = 0.8;
          zIndex = 5;
        } else if (isPrev) {
          width = "30%";
          left = "0%";
          scale = 0.9;
          opacity = 0.8;
          zIndex = 5;
        } else {
          // Hide other items
          opacity = 0;
          zIndex = 1;
        }
      }
      
      return (
        <div 
          key={index}
          className={cn(
            "absolute top-0 h-full transition-all duration-300 ease-in-out",
            isActive || (!isMobile && (isNext || isPrev)) ? "cursor-pointer" : "pointer-events-none"
          )}
          style={{
            width,
            left,
            transform: `scale(${scale})`,
            opacity,
            zIndex
          }}
          onClick={() => {
            if (isAnimating) return;
            if (!isMobile && isNext) handleNextClick();
            else if (!isMobile && isPrev) handlePrevClick();
            else if (position !== 0) setCurrentIndexState(index);
          }}
        >
          {React.cloneElement(child as React.ReactElement<CarouselItemProps>, {
            isActive,
            isNext: !isMobile && isNext,
            isPrev: !isMobile && isPrev
          })}
        </div>
      );
    });
  };

  return (
    <div className={cn("relative w-full", className)}>
      <div className="overflow-visible relative h-[260px]">
        <div className="absolute top-0 left-0 w-full h-full">
          {renderItems()}
        </div>
      </div>

      <Button
        variant="outline"
        size="icon"
        className={cn(
          "absolute left-4 top-1/2 -translate-y-1/2 h-8 w-8 rounded-full hover:border-white z-30",
          isMobile ? "left-1" : "left-4"
        )}
        onClick={handlePrevClick}
        disabled={isAnimating}
      >
        <ArrowLeft className="h-4 w-4" />
        <span className="sr-only">Previous</span>
      </Button>

      <Button
        variant="outline"
        size="icon"
        className={cn(
          "absolute right-4 top-1/2 -translate-y-1/2 h-8 w-8 rounded-full hover:border-white z-30",
          isMobile ? "right-1" : "right-4"
        )}
        onClick={handleNextClick}
        disabled={isAnimating}
      >
        <ArrowRight className="h-4 w-4" />
        <span className="sr-only">Next</span>
      </Button>
    </div>
  );
}

export function CustomCarouselItem({ 
  children, 
  className,
  isActive,
  isNext,
  isPrev,
  ...props 
}: CarouselItemProps) {
  return (
    <div
      className={cn(
        "select-none transition-all duration-300 w-full h-full",
        isActive ? "px-1" : isNext ? "pl-4" : isPrev ? "pr-4" : "px-1",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
} 