/**
 * JARVIS 8.0 ULTRA - Item Response Theory (IRT) Engine
 * 
 * Implements the 3-Parameter Logistic Model (3PL) for Computerized Adaptive Testing (CAT)
 * Based on research from Columbia University and Cambridge Assessment
 * 
 * The 3PL Model: P(θ) = c + (1 - c) / (1 + exp(-a(θ - b)))
 * Where:
 * - θ (theta) = student ability (-3 to +3)
 * - a = discrimination parameter (0.5 to 2.5)
 * - b = difficulty parameter (-3 to +3)
 * - c = guessing parameter (0 to 0.5, typically 0.25 for 4-choice MCQ)
 */

export interface IRTParameters {
  difficulty: number;      // b parameter (-3 to +3)
  discrimination: number;  // a parameter (0.5 to 2.5)
  guessing: number;        // c parameter (0 to 0.5)
}

export interface IRTResult {
  thetaBefore: number;
  thetaAfter: number;
  thetaChange: number;
  probabilityCorrect: number;
  information: number;
}

export interface QuestionIRT extends IRTParameters {
  id: string;
  subjectId: string;
  topicId: string;
}

// Constants for IRT
const THETA_MIN = -3.0;
const THETA_MAX = 3.0;
const DISCRIMINATION_MIN = 0.5;
const DISCRIMINATION_MAX = 2.5;
const GUESSING_DEFAULT = 0.25; // For 4-choice MCQ

/**
 * Calculate the probability of a correct answer using 3PL model
 * P(θ) = c + (1 - c) / (1 + exp(-a(θ - b)))
 */
export function probabilityCorrect(
  theta: number,
  params: IRTParameters
): number {
  const { difficulty, discrimination, guessing } = params;
  
  // Clamp values to valid ranges
  const t = clamp(theta, THETA_MIN, THETA_MAX);
  const b = clamp(difficulty, THETA_MIN, THETA_MAX);
  const a = clamp(discrimination, DISCRIMINATION_MIN, DISCRIMINATION_MAX);
  const c = clamp(guessing, 0, 0.5);
  
  // 3PL Formula
  const exponent = -a * (t - b);
  const probability = c + (1 - c) / (1 + Math.exp(exponent));
  
  return probability;
}

/**
 * Calculate Fisher Information for a question at given theta
 * I(θ) = a² * P(θ) * (1 - P(θ)) / (P(θ) - c)² * (1 - c)²
 * Simplified: I(θ) = a² * P * Q / (P - c)² where Q = 1 - P
 */
export function fisherInformation(
  theta: number,
  params: IRTParameters
): number {
  const { discrimination, guessing } = params;
  const P = probabilityCorrect(theta, params);
  const Q = 1 - P;
  const a = clamp(discrimination, DISCRIMINATION_MIN, DISCRIMINATION_MAX);
  const c = clamp(guessing, 0, 0.5);
  
  // Fisher Information formula for 3PL
  const numerator = a * a * P * Q;
  const denominator = Math.pow(P - c, 2);
  
  if (denominator === 0) return 0;
  
  return numerator / denominator * Math.pow(1 - c, 2);
}

/**
 * Update theta estimate using Maximum Likelihood Estimation (MLE)
 * This is the core CAT algorithm for updating ability estimate
 * 
 * MLE Update Formula:
 * θ_new = θ_old + (observed - expected) / information
 */
export function updateTheta(
  currentTheta: number,
  params: IRTParameters,
  isCorrect: boolean
): IRTResult {
  const thetaBefore = currentTheta;
  
  // Calculate probability and information
  const P = probabilityCorrect(currentTheta, params);
  const I = fisherInformation(currentTheta, params);
  
  // Avoid division by zero
  if (I < 0.001) {
    return {
      thetaBefore,
      thetaAfter: thetaBefore,
      thetaChange: 0,
      probabilityCorrect: P,
      information: I
    };
  }
  
  // MLE update
  const observed = isCorrect ? 1 : 0;
  const thetaChange = (observed - P) / I;
  
  // Apply damping factor for stability (reduces large jumps)
  const dampingFactor = 0.7;
  const adjustedChange = thetaChange * dampingFactor;
  
  // Calculate new theta with bounds
  let thetaAfter = thetaBefore + adjustedChange;
  thetaAfter = clamp(thetaAfter, THETA_MIN, THETA_MAX);
  
  return {
    thetaBefore,
    thetaAfter,
    thetaChange: thetaAfter - thetaBefore,
    probabilityCorrect: P,
    information: I
  };
}

/**
 * Select the optimal next question for CAT
 * Uses Maximum Information criterion - selects question with highest Fisher Information
 * at current theta estimate
 */
export function selectOptimalQuestion(
  currentTheta: number,
  questions: QuestionIRT[],
  answeredQuestionIds: Set<string>
): QuestionIRT | null {
  // Filter out already answered questions
  const availableQuestions = questions.filter(q => !answeredQuestionIds.has(q.id));
  
  if (availableQuestions.length === 0) return null;
  
  // Calculate information for each question
  let maxInformation = -Infinity;
  let optimalQuestion: QuestionIRT | null = null;
  
  for (const question of availableQuestions) {
    const params: IRTParameters = {
      difficulty: question.difficulty,
      discrimination: question.discrimination,
      guessing: GUESSING_DEFAULT
    };
    
    const information = fisherInformation(currentTheta, params);
    
    // Select question with maximum information near student's ability
    // Adding slight randomness to avoid always picking same questions
    const randomFactor = 0.95 + Math.random() * 0.1; // 0.95 to 1.05
    const adjustedInfo = information * randomFactor;
    
    if (adjustedInfo > maxInformation) {
      maxInformation = adjustedInfo;
      optimalQuestion = question;
    }
  }
  
  return optimalQuestion;
}

/**
 * Calculate Standard Error of theta estimate
 * SE(θ) = 1 / sqrt(I(θ)) where I(θ) is total information
 */
export function calculateStandardError(
  theta: number,
  questionParams: IRTParameters[]
): number {
  let totalInformation = 0;
  
  for (const params of questionParams) {
    totalInformation += fisherInformation(theta, params);
  }
  
  if (totalInformation <= 0) return THETA_MAX - THETA_MIN;
  
  return 1 / Math.sqrt(totalInformation);
}

/**
 * Check if CAT should stop (ability estimate is stable)
 * Stopping rule: SE < 0.3 or max questions reached
 */
export function shouldStopCAT(
  theta: number,
  questionParams: IRTParameters[],
  maxQuestions: number,
  currentQuestionCount: number,
  targetSE: number = 0.3
): { stop: boolean; reason: string } {
  // Check question limit
  if (currentQuestionCount >= maxQuestions) {
    return { stop: true, reason: 'Maximum questions reached' };
  }
  
  // Check standard error
  const se = calculateStandardError(theta, questionParams);
  if (se < targetSE) {
    return { stop: true, reason: `Target precision achieved (SE = ${se.toFixed(3)})` };
  }
  
  // Minimum questions before checking precision
  if (currentQuestionCount < 5) {
    return { stop: false, reason: 'Minimum questions not reached' };
  }
  
  return { stop: false, reason: `SE = ${se.toFixed(3)}, continuing` };
}

/**
 * Convert theta to percentage score for display
 * Maps theta from [-3, 3] to [0, 100]
 */
export function thetaToPercentage(theta: number): number {
  const normalized = (theta - THETA_MIN) / (THETA_MAX - THETA_MIN);
  return Math.round(normalized * 100);
}

/**
 * Convert percentage to theta
 * Maps from [0, 100] to [-3, 3]
 */
export function percentageToTheta(percentage: number): number {
  return THETA_MIN + (percentage / 100) * (THETA_MAX - THETA_MIN);
}

/**
 * Get ability level description based on theta
 */
export function getAbilityLevel(theta: number): {
  level: string;
  description: string;
  color: string;
} {
  if (theta < -2) {
    return { level: 'Beginner', description: 'Foundation building needed', color: '#ef4444' };
  } else if (theta < -1) {
    return { level: 'Developing', description: 'Making progress', color: '#f97316' };
  } else if (theta < 0) {
    return { level: 'Competent', description: 'Approaching average', color: '#eab308' };
  } else if (theta < 1) {
    return { level: 'Proficient', description: 'Above average', color: '#22c55e' };
  } else if (theta < 2) {
    return { level: 'Advanced', description: 'Strong performance', color: '#3b82f6' };
  } else {
    return { level: 'Expert', description: 'Exceptional ability', color: '#8b5cf6' };
  }
}

/**
 * Calculate expected score for a set of questions
 */
export function calculateExpectedScore(
  theta: number,
  questions: IRTParameters[]
): number {
  let expectedCorrect = 0;
  
  for (const params of questions) {
    expectedCorrect += probabilityCorrect(theta, params);
  }
  
  return Math.round(expectedCorrect);
}

// Utility function
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

// Export all functions and types
export const IRTEngine = {
  probabilityCorrect,
  fisherInformation,
  updateTheta,
  selectOptimalQuestion,
  calculateStandardError,
  shouldStopCAT,
  thetaToPercentage,
  percentageToTheta,
  getAbilityLevel,
  calculateExpectedScore,
  THETA_MIN,
  THETA_MAX,
  GUESSING_DEFAULT
};

export default IRTEngine;
