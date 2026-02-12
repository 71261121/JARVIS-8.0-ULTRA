/**
 * JARVIS 8.0 ULTRA - Psychological Engine
 * 
 * Implements science-backed psychological techniques for motivation:
 * 1. Loss Aversion (Kahneman & Tversky, 1979)
 * 2. Variable Reward System (Dopamine optimization)
 * 3. Social Comparison & Leaderboards
 * 4. Achievement System
 * 
 * Research Sources:
 * - Kahneman & Tversky (1979) - Loss Aversion
 * - The Decision Lab - Behavioral Economics
 * - MDPI Journal - Gamified Learning Research
 * - Springer - Gamification in Education
 */

export interface XPResult {
  xpEarned: number;
  xpLost: number;
  totalXP: number;
  multiplier: number;
  reason: string;
}

export interface StreakResult {
  currentStreak: number;
  longestStreak: int;
  isBroken: boolean;
  bonus: number;
  penalty: number;
}

export interface RewardResult {
  coins: number;
  xp: number;
  isBonus: boolean;
  isMystery: boolean;
  message: string;
}

export interface Achievement {
  id: string;
  code: string;
  name: string;
  description: string;
  icon: string;
  xpReward: number;
  coinReward: number;
  conditionType: string;
  conditionValue: number;
  isSecret: boolean;
}

export interface UserStats {
  totalXP: number;
  currentStreak: number;
  longestStreak: number;
  focusCoins: number;
  level: number;
  totalSessions: number;
  totalQuestions: number;
  correctAnswers: number;
}

// Loss Aversion: Loss feels 2x more painful than equivalent gain
const LOSS_AVERSION_MULTIPLIER = 2;

// XP Constants
const XP_PER_QUESTION = 10;
const XP_CORRECT_BONUS = 5;
const XP_STREAK_BONUS_BASE = 20;
const XP_SESSION_COMPLETION = 50;
const XP_MOCK_TEST_COMPLETION = 100;
const XP_DAILY_GOAL = 200;

// Level thresholds (XP required for each level)
const LEVEL_THRESHOLDS = [
  0, 500, 1200, 2200, 3500, 5200, 7500, 10500, 14500, 20000,
  27000, 36000, 48000, 64000, 85000, 112000, 147000, 192000, 250000, 320000
];

// Coin Constants
const COINS_PER_QUESTION = 2;
const COINS_CORRECT_BONUS = 3;
const COINS_STREAK_BONUS = 10;
const COINS_SKIP_PENALTY = 20; // Loss aversion - losing coins hurts more

/**
 * Calculate XP earned from a study session
 * Uses loss aversion - show potential loss more prominently than gain
 */
export function calculateSessionXP(
  questionsAnswered: number,
  correctAnswers: number,
  sessionDurationMinutes: number,
  targetMinutes: number,
  isDistractionFree: boolean
): XPResult {
  let xpEarned = 0;
  let xpLost = 0;
  let multiplier = 1.0;
  const reasons: string[] = [];
  
  // Base XP for questions
  const baseXP = questionsAnswered * XP_PER_QUESTION;
  xpEarned += baseXP;
  reasons.push(`${questionsAnswered} questions: +${baseXP} XP`);
  
  // Correct answer bonus
  if (correctAnswers > 0) {
    const correctBonus = correctAnswers * XP_CORRECT_BONUS;
    xpEarned += correctBonus;
    reasons.push(`${correctAnswers} correct: +${correctBonus} XP`);
  }
  
  // Accuracy multiplier
  if (questionsAnswered > 0) {
    const accuracy = correctAnswers / questionsAnswered;
    if (accuracy >= 0.9) {
      multiplier = 1.5;
      reasons.push('90%+ accuracy: 1.5x multiplier!');
    } else if (accuracy >= 0.8) {
      multiplier = 1.25;
      reasons.push('80%+ accuracy: 1.25x multiplier');
    } else if (accuracy < 0.5) {
      // Loss aversion - low accuracy means losing potential XP
      multiplier = 0.75;
      xpLost = Math.round(baseXP * 0.25);
      reasons.push('< 50% accuracy: -25% XP penalty');
    }
  }
  
  // Session completion bonus
  if (sessionDurationMinutes >= targetMinutes * 0.9) {
    xpEarned += XP_SESSION_COMPLETION;
    reasons.push(`Session complete: +${XP_SESSION_COMPLETION} XP`);
  } else {
    // Loss message - more impactful
    const missedMinutes = targetMinutes - sessionDurationMinutes;
    xpLost += 30;
    reasons.push(`Missed ${missedMinutes} minutes: LOSE 30 XP potential`);
  }
  
  // Distraction-free bonus
  if (isDistractionFree) {
    xpEarned += 30;
    reasons.push('Distraction-free: +30 XP');
  }
  
  // Apply multiplier
  xpEarned = Math.round(xpEarned * multiplier);
  
  const totalXP = xpEarned - xpLost;
  
  return {
    xpEarned,
    xpLost,
    totalXP: Math.max(0, totalXP),
    multiplier,
    reason: reasons.join('\n')
  };
}

/**
 * Update streak and apply loss aversion psychology
 * Breaking a streak feels VERY painful (2x the reward of building it)
 */
export function updateStreak(
  currentStreak: number,
  longestStreak: number,
  didStudyToday: boolean
): StreakResult & { warning: string } {
  let warning = '';
  
  if (didStudyToday) {
    const newStreak = currentStreak + 1;
    const bonus = calculateStreakBonus(newStreak);
    
    if (newStreak > longestStreak) {
      warning = `🎉 NEW RECORD! ${newStreak} day streak! +${bonus} bonus XP!`;
    } else {
      warning = `🔥 ${newStreak} day streak! Keep going! +${bonus} bonus XP`;
    }
    
    return {
      currentStreak: newStreak,
      longestStreak: Math.max(newStreak, longestStreak),
      isBroken: false,
      bonus,
      penalty: 0,
      warning
    };
  } else {
    // LOSS AVERSION: Show what they're losing
    const potentialBonus = calculateStreakBonus(currentStreak + 1);
    const penalty = potentialBonus * LOSS_AVERSION_MULTIPLIER;
    
    warning = `💔 STREAK BROKEN! You had ${currentStreak} days.\n`;
    warning += `You LOST ${penalty} potential XP by not studying today.\n`;
    warning += `Your next streak starts tomorrow. Don't give up!`;
    
    return {
      currentStreak: 0,
      longestStreak,
      isBroken: true,
      bonus: 0,
      penalty,
      warning
    };
  }
}

/**
 * Calculate streak bonus (compounding)
 */
export function calculateStreakBonus(streakDays: number): number {
  if (streakDays < 3) return XP_STREAK_BONUS_BASE;
  
  // Exponential bonus for longer streaks
  // 3 days: 25, 7 days: 50, 14 days: 100, 30 days: 250
  return Math.round(XP_STREAK_BONUS_BASE * Math.pow(1.1, streakDays - 1));
}

/**
 * Variable Reward System - Like slot machines
 * Unpredictable rewards create stronger dopamine response
 */
export function calculateVariableReward(
  baseXP: number,
  baseCoins: number
): RewardResult {
  // Random bonus chance (like a slot machine)
  const random = Math.random();
  
  // 5% chance of big bonus (jackpot)
  if (random < 0.05) {
    const jackpotXP = baseXP * 3;
    const jackpotCoins = baseCoins * 5;
    return {
      coins: jackpotCoins,
      xp: jackpotXP,
      isBonus: true,
      isMystery: true,
      message: `🎰 JACKPOT! You earned ${jackpotXP} XP and ${jackpotCoins} coins!`
    };
  }
  
  // 15% chance of medium bonus
  if (random < 0.20) {
    const bonusXP = Math.round(baseXP * 1.5);
    const bonusCoins = Math.round(baseCoins * 2);
    return {
      coins: bonusCoins,
      xp: bonusXP,
      isBonus: true,
      isMystery: true,
      message: `🎁 BONUS! Extra rewards: +${bonusXP} XP, +${bonusCoins} coins!`
    };
  }
  
  // 25% chance of small bonus
  if (random < 0.45) {
    const bonusXP = Math.round(baseXP * 1.2);
    return {
      coins: baseCoins,
      xp: bonusXP,
      isBonus: true,
      isMystery: false,
      message: `✨ Small bonus: +${bonusXP} XP`
    };
  }
  
  // Normal reward
  return {
    coins: baseCoins,
    xp: baseXP,
    isBonus: false,
    isMystery: false,
    message: `Earned ${baseXP} XP and ${baseCoins} coins`
  };
}

/**
 * Mystery Box System - Variable reward for topic completion
 */
export function openMysteryBox(): {
  type: 'xp' | 'coins' | 'achievement' | 'nothing';
  value: number;
  message: string;
} {
  const random = Math.random();
  
  // 2% achievement unlock
  if (random < 0.02) {
    return {
      type: 'achievement',
      value: 0,
      message: '🌟 RARE! You unlocked a secret achievement!'
    };
  }
  
  // 15% big XP
  if (random < 0.17) {
    const xp = 100 + Math.floor(Math.random() * 200);
    return {
      type: 'xp',
      value: xp,
      message: `💎 BIG WIN! +${xp} XP!`
    };
  }
  
  // 25% coins
  if (random < 0.42) {
    const coins = 20 + Math.floor(Math.random() * 50);
    return {
      type: 'coins',
      value: coins,
      message: `💰 Found ${coins} Focus Coins!`
    };
  }
  
  // 20% small XP
  if (random < 0.62) {
    const xp = 25 + Math.floor(Math.random() * 50);
    return {
      type: 'xp',
      value: xp,
      message: `✨ +${xp} XP!`
    };
  }
  
  // 38% nothing (but show encouraging message)
  return {
    type: 'nothing',
    value: 0,
    message: 'Keep studying for better rewards next time!'
  };
}

/**
 * Calculate level from total XP
 */
export function calculateLevel(totalXP: number): number {
  for (let i = LEVEL_THRESHOLDS.length - 1; i >= 0; i--) {
    if (totalXP >= LEVEL_THRESHOLDS[i]) {
      return i + 1;
    }
  }
  return 1;
}

/**
 * Get XP required for next level
 */
export function getXPForNextLevel(currentLevel: number): number {
  if (currentLevel >= LEVEL_THRESHOLDS.length) {
    return LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1] * 2;
  }
  return LEVEL_THRESHOLDS[currentLevel];
}

/**
 * Get XP progress to next level (0-100)
 */
export function getLevelProgress(totalXP: number): {
  currentLevel: number;
  progress: number;
  xpInCurrentLevel: number;
  xpNeededForNext: number;
} {
  const currentLevel = calculateLevel(totalXP);
  const currentThreshold = LEVEL_THRESHOLDS[currentLevel - 1] || 0;
  const nextThreshold = LEVEL_THRESHOLDS[currentLevel] || currentThreshold * 2;
  
  const xpInCurrentLevel = totalXP - currentThreshold;
  const xpNeededForNext = nextThreshold - currentThreshold;
  const progress = Math.round((xpInCurrentLevel / xpNeededForNext) * 100);
  
  return {
    currentLevel,
    progress: Math.min(100, progress),
    xpInCurrentLevel,
    xpNeededForNext
  };
}

/**
 * Social Comparison - Leaderboard calculation
 * Uses percentile rank for motivation
 */
export function calculateLeaderboardPosition(
  userXP: number,
  allUserXPs: number[]
): {
  rank: number;
  percentile: number;
  message: string;
  usersAhead: number;
  usersBehind: number;
} {
  // Sort descending
  const sorted = [...allUserXPs].sort((a, b) => b - a);
  const rank = sorted.indexOf(userXP) + 1;
  const total = allUserXPs.length;
  
  // Percentile (higher is better)
  const percentile = Math.round(((total - rank + 1) / total) * 100);
  
  // Motivational message based on position
  let message = '';
  if (percentile >= 99) {
    message = '🏆 TOP 1%! You\'re a champion!';
  } else if (percentile >= 95) {
    message = '🥇 TOP 5%! Almost at the summit!';
  } else if (percentile >= 90) {
    message = '🥈 TOP 10%! Excellent performance!';
  } else if (percentile >= 75) {
    message = '🥉 TOP 25%! Great progress!';
  } else if (percentile >= 50) {
    message = '📈 Above average! Keep climbing!';
  } else {
    message = '💪 Room to grow! Every session counts!';
  }
  
  return {
    rank,
    percentile,
    message,
    usersAhead: rank - 1,
    usersBehind: total - rank
  };
}

/**
 * Loss Aversion Warning Message
 * More impactful than gain messages
 */
export function generateLossWarning(
  potentialXP: number,
  streakDays: number,
  coinsAtRisk: number
): string {
  const messages = [
    `⚠️ WARNING: Skipping today costs you ${potentialXP} XP!`,
    `🔥 Your ${streakDays}-day streak will be BROKEN!`,
    `💰 ${coinsAtRisk} Focus Coins will be LOST!`,
    `📊 Your theta score will DECREASE!`,
    `🎯 Your percentile rank will DROP!`
  ];
  
  // Return random warning for variety
  return messages[Math.floor(Math.random() * messages.length)];
}

/**
 * Check achievement unlock conditions
 */
export function checkAchievements(stats: UserStats): Achievement[] {
  const unlocked: Achievement[] = [];
  
  // Define achievements
  const achievements: Achievement[] = [
    {
      id: 'first_session',
      code: 'first_session',
      name: 'First Steps',
      description: 'Complete your first study session',
      icon: '🎯',
      xpReward: 50,
      coinReward: 20,
      conditionType: 'sessions',
      conditionValue: 1,
      isSecret: false
    },
    {
      id: 'streak_7',
      code: 'streak_7',
      name: 'Week Warrior',
      description: 'Maintain a 7-day streak',
      icon: '🔥',
      xpReward: 200,
      coinReward: 50,
      conditionType: 'streak',
      conditionValue: 7,
      isSecret: false
    },
    {
      id: 'streak_30',
      code: 'streak_30',
      name: 'Monthly Master',
      description: 'Maintain a 30-day streak',
      icon: '👑',
      xpReward: 1000,
      coinReward: 200,
      conditionType: 'streak',
      conditionValue: 30,
      isSecret: false
    },
    {
      id: 'questions_100',
      code: 'questions_100',
      name: 'Century',
      description: 'Answer 100 questions',
      icon: '💯',
      xpReward: 100,
      coinReward: 30,
      conditionType: 'questions',
      conditionValue: 100,
      isSecret: false
    },
    {
      id: 'questions_500',
      code: 'questions_500',
      name: 'Knowledge Seeker',
      description: 'Answer 500 questions',
      icon: '📚',
      xpReward: 300,
      coinReward: 100,
      conditionType: 'questions',
      conditionValue: 500,
      isSecret: false
    },
    {
      id: 'accuracy_90',
      code: 'accuracy_90',
      name: 'Sharp Shooter',
      description: 'Achieve 90%+ accuracy in a session',
      icon: '🎯',
      xpReward: 150,
      coinReward: 50,
      conditionType: 'accuracy',
      conditionValue: 90,
      isSecret: false
    },
    {
      id: 'level_5',
      code: 'level_5',
      name: 'Rising Star',
      description: 'Reach Level 5',
      icon: '⭐',
      xpReward: 200,
      coinReward: 75,
      conditionType: 'level',
      conditionValue: 5,
      isSecret: false
    },
    {
      id: 'level_10',
      code: 'level_10',
      name: 'Elite Scholar',
      description: 'Reach Level 10',
      icon: '🌟',
      xpReward: 500,
      coinReward: 150,
      conditionType: 'level',
      conditionValue: 10,
      isSecret: false
    }
  ];
  
  // Check each achievement
  for (const achievement of achievements) {
    let unlocked_achievement = false;
    
    switch (achievement.conditionType) {
      case 'sessions':
        unlocked_achievement = stats.totalSessions >= achievement.conditionValue;
        break;
      case 'streak':
        unlocked_achievement = stats.currentStreak >= achievement.conditionValue;
        break;
      case 'questions':
        unlocked_achievement = stats.totalQuestions >= achievement.conditionValue;
        break;
      case 'accuracy':
        if (stats.totalQuestions > 0) {
          const accuracy = (stats.correctAnswers / stats.totalQuestions) * 100;
          unlocked_achievement = accuracy >= achievement.conditionValue;
        }
        break;
      case 'level':
        unlocked_achievement = stats.level >= achievement.conditionValue;
        break;
    }
    
    if (unlocked_achievement) {
      unlocked.push(achievement);
    }
  }
  
  return unlocked;
}

// Utility
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

// Export all
export const PsychologicalEngine = {
  calculateSessionXP,
  updateStreak,
  calculateStreakBonus,
  calculateVariableReward,
  openMysteryBox,
  calculateLevel,
  getXPForNextLevel,
  getLevelProgress,
  calculateLeaderboardPosition,
  generateLossWarning,
  checkAchievements,
  LOSS_AVERSION_MULTIPLIER,
  XP_PER_QUESTION,
  XP_CORRECT_BONUS,
  LEVEL_THRESHOLDS
};

export default PsychologicalEngine;
