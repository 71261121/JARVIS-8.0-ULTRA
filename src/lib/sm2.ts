/**
 * JARVIS 8.0 ULTRA - SM-2 Spaced Repetition Algorithm
 * 
 * Based on the SuperMemo 2 Algorithm by Piotr Wozniak
 * Enhanced with Ebbinghaus Forgetting Curve optimization
 * 
 * Research Sources:
 * - SuperMemo (supermemo.com)
 * - Ebbinghaus Forgetting Curve (1885)
 * - Cepeda et al. (2006) on spaced repetition effectiveness
 */

export interface SM2Parameters {
  easeFactor: number;      // Difficulty multiplier (default 2.5)
  interval: number;        // Days until next review
  repetitions: number;     // Consecutive correct answers
}

export interface SM2Result {
  easeFactor: number;
  interval: number;
  repetitions: number;
  nextReviewDate: Date;
  quality: number;
}

export interface ReviewItem {
  id: string;
  userId: string;
  topicId: string;
  easeFactor: number;
  interval: number;
  repetitions: number;
  lastReviewDate?: Date;
  nextReviewDate: Date;
}

/**
 * Quality rating scale (0-5):
 * 0 - Complete blackout, no recall
 * 1 - Incorrect but recognized the answer
 * 2 - Incorrect but remembered on second thought
 * 3 - Correct but with difficulty
 * 4 - Correct after hesitation
 * 5 - Perfect response, immediate recall
 */

const QUALITY_MIN = 0;
const QUALITY_MAX = 5;
const EASE_FACTOR_MIN = 1.3;
const EASE_FACTOR_DEFAULT = 2.5;

// Standard SM-2 intervals (in days)
const INTERVALS = {
  FIRST: 1,
  SECOND: 3,
  THIRD_FACTOR: 6  // Used as multiplier after second interval
};

/**
 * Calculate next review using SM-2 algorithm
 * 
 * Algorithm:
 * 1. If quality < 3: reset repetitions, interval = 1
 * 2. If quality >= 3:
 *    - If repetitions = 0: interval = 1
 *    - If repetitions = 1: interval = 3
 *    - If repetitions >= 2: interval = interval * easeFactor
 * 3. Update easeFactor: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
 */
export function calculateNextReview(
  currentParams: SM2Parameters,
  quality: number
): SM2Result {
  // Validate quality
  const q = clamp(quality, QUALITY_MIN, QUALITY_MAX);
  
  let { easeFactor, interval, repetitions } = currentParams;
  
  // Quality < 3 means failed recall - reset
  if (q < 3) {
    repetitions = 0;
    interval = INTERVALS.FIRST;
  } else {
    // Successful recall
    repetitions++;
    
    if (repetitions === 1) {
      interval = INTERVALS.FIRST;
    } else if (repetitions === 2) {
      interval = INTERVALS.SECOND;
    } else {
      // For repetitions >= 3, use ease factor
      interval = Math.round(interval * easeFactor);
    }
  }
  
  // Update ease factor using SM-2 formula
  // EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
  easeFactor = easeFactor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));
  
  // Clamp ease factor
  easeFactor = Math.max(EASE_FACTOR_MIN, easeFactor);
  
  // Calculate next review date
  const nextReviewDate = new Date();
  nextReviewDate.setDate(nextReviewDate.getDate() + interval);
  
  return {
    easeFactor,
    interval,
    repetitions,
    nextReviewDate,
    quality: q
  };
}

/**
 * Calculate retention probability based on Ebbinghaus Forgetting Curve
 * R(t) = e^(-t/S) where:
 * - R = retention probability
 * - t = time since last review
 * - S = memory stability (related to easeFactor and repetitions)
 */
export function calculateRetentionProbability(
  daysSinceReview: number,
  easeFactor: number,
  repetitions: number
): number {
  // Memory stability increases with repetitions and ease factor
  const stability = easeFactor * Math.pow(1.5, repetitions) * 10;
  
  if (stability <= 0) return 0;
  
  const retention = Math.exp(-daysSinceReview / stability);
  
  return clamp(retention, 0, 1);
}

/**
 * Calculate optimal review time based on forgetting curve
 * Returns days until optimal review (when retention drops to ~90%)
 */
export function calculateOptimalReviewDelay(
  easeFactor: number,
  repetitions: number,
  targetRetention: number = 0.9
): number {
  const stability = easeFactor * Math.pow(1.5, repetitions) * 10;
  
  // Solve for t in R(t) = targetRetention
  // t = -S * ln(targetRetention)
  const delay = -stability * Math.log(targetRetention);
  
  return Math.max(1, Math.round(delay));
}

/**
 * Get items due for review today
 */
export function getDueReviews(
  items: ReviewItem[],
  asOfDate: Date = new Date()
): ReviewItem[] {
  const today = new Date(asOfDate);
  today.setHours(23, 59, 59, 999);
  
  return items.filter(item => {
    const nextReview = new Date(item.nextReviewDate);
    return nextReview <= today;
  });
}

/**
 * Get items overdue for review
 */
export function getOverdueReviews(
  items: ReviewItem[],
  asOfDate: Date = new Date()
): ReviewItem[] {
  const today = new Date(asOfDate);
  today.setHours(0, 0, 0, 0);
  
  return items.filter(item => {
    const nextReview = new Date(item.nextReviewDate);
    return nextReview < today;
  });
}

/**
 * Calculate urgency score for prioritizing reviews
 * Higher score = more urgent
 */
export function calculateReviewUrgency(item: ReviewItem): number {
  const now = new Date();
  const nextReview = new Date(item.nextReviewDate);
  const daysOverdue = Math.floor((now.getTime() - nextReview.getTime()) / (1000 * 60 * 60 * 24));
  
  // More overdue = higher urgency
  // Lower ease factor = higher urgency (harder item)
  // Lower repetitions = higher urgency (less established memory)
  
  let urgency = 0;
  
  // Overdue penalty
  if (daysOverdue > 0) {
    urgency += daysOverdue * 10;
  }
  
  // Difficulty factor
  urgency += (EASE_FACTOR_DEFAULT - item.easeFactor) * 5;
  
  // New item bonus (needs more attention)
  if (item.repetitions < 3) {
    urgency += (3 - item.repetitions) * 5;
  }
  
  return Math.max(0, urgency);
}

/**
 * Sort review items by urgency (most urgent first)
 */
export function sortByUrgency(items: ReviewItem[]): ReviewItem[] {
  return [...items].sort((a, b) => {
    const urgencyA = calculateReviewUrgency(a);
    const urgencyB = calculateReviewUrgency(b);
    return urgencyB - urgencyA;
  });
}

/**
 * Calculate review statistics
 */
export function calculateReviewStats(items: ReviewItem[]): {
  total: number;
  due: number;
  overdue: number;
  learned: number;
  learning: number;
  averageEaseFactor: number;
  averageInterval: number;
} {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  
  let due = 0;
  let overdue = 0;
  let learned = 0;
  let learning = 0;
  let totalEaseFactor = 0;
  let totalInterval = 0;
  
  for (const item of items) {
    const nextReview = new Date(item.nextReviewDate);
    
    if (nextReview <= now) due++;
    if (nextReview < now) overdue++;
    if (item.repetitions >= 3) learned++;
    else learning++;
    
    totalEaseFactor += item.easeFactor;
    totalInterval += item.interval;
  }
  
  return {
    total: items.length,
    due,
    overdue,
    learned,
    learning,
    averageEaseFactor: items.length > 0 ? totalEaseFactor / items.length : EASE_FACTOR_DEFAULT,
    averageInterval: items.length > 0 ? totalInterval / items.length : 0
  };
}

/**
 * Get recommended daily review count based on workload
 */
export function getRecommendedDailyReviews(
  totalItems: number,
  daysUntilExam: number
): number {
  // Base calculation: review all items multiple times before exam
  const targetReviews = totalItems * 3; // Each item reviewed ~3 times
  const dailyReviews = Math.ceil(targetReviews / daysUntilExam);
  
  // Cap at reasonable limits
  const minReviews = 20;
  const maxReviews = 100;
  
  return clamp(dailyReviews, minReviews, maxReviews);
}

/**
 * Predict long-term retention rate
 */
export function predictRetentionRate(
  items: ReviewItem[],
  daysInFuture: number
): number {
  if (items.length === 0) return 100;
  
  let totalRetention = 0;
  
  for (const item of items) {
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + daysInFuture);
    
    const lastReview = item.lastReviewDate || new Date();
    const daysSinceReview = Math.floor(
      (futureDate.getTime() - new Date(lastReview).getTime()) / (1000 * 60 * 60 * 24)
    );
    
    const retention = calculateRetentionProbability(
      daysSinceReview,
      item.easeFactor,
      item.repetitions
    );
    
    totalRetention += retention;
  }
  
  return Math.round((totalRetention / items.length) * 100);
}

// Utility function
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

// Export all
export const SM2Engine = {
  calculateNextReview,
  calculateRetentionProbability,
  calculateOptimalReviewDelay,
  getDueReviews,
  getOverdueReviews,
  calculateReviewUrgency,
  sortByUrgency,
  calculateReviewStats,
  getRecommendedDailyReviews,
  predictRetentionRate,
  EASE_FACTOR_MIN,
  EASE_FACTOR_DEFAULT,
  INTERVALS
};

export default SM2Engine;
