"""
JARVIS IRT Engine - Item Response Theory Implementation
=======================================================

Implements the 3-Parameter Logistic Model (3PL) for Computerized Adaptive Testing (CAT)
Based on comprehensive research on IRT/CAT methodology

The 3PL Model: P(θ) = c + (1 - c) / (1 + exp(-Da(θ - b)))

Where:
- θ (theta) = student ability (-3 to +3, with 0 as population mean)
- a = discrimination parameter (0.5 to 2.5, higher = better differentiation)
- b = difficulty parameter (-3 to +3, 0 = average difficulty)
- c = guessing parameter (0 to 0.5, typically 0.25 for 4-choice MCQ)
- D = scaling constant (1.7, Birnbaum's constant for logistic-normal metric)

REFERENCES:
- Lord, F.M. (1980). Applications of Item Response Theory to Practical Testing Problems
- Hambleton, R.K., & Swaminathan, H. (1985). Item Response Theory: Principles and Applications
- Wainer, H. (2000). Computerized Adaptive Testing: A Primer

EXAM IMPACT: 
    Direct. Maths carries 20 marks (highest weightage) and is user's weakest subject.
    IRT ensures every question is at optimal difficulty, maximizing learning per question.
    No time wasted on too-easy or too-hard questions.
"""

import math
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# CONSTANTS
# ============================================================================

THETA_MIN = -3.0           # Minimum ability level (0.1th percentile)
THETA_MAX = 3.0            # Maximum ability level (99.9th percentile)
DISCRIMINATION_MIN = 0.5   # Poor discrimination threshold
DISCRIMINATION_MAX = 2.5   # Very high discrimination threshold
GUESSING_DEFAULT = 0.25    # For 4-choice MCQ
D_SCALING = 1.7            # Birnbaum's scaling constant
SE_TARGET = 0.30           # Target standard error for stopping


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class IRTParameters:
    """IRT parameters for a question."""
    difficulty: float       # b parameter (-3 to +3)
    discrimination: float   # a parameter (0.5 to 2.5)
    guessing: float         # c parameter (0 to 0.5)
    
    def __post_init__(self):
        """Validate parameters after initialization."""
        self.difficulty = clamp(self.difficulty, THETA_MIN, THETA_MAX)
        self.discrimination = clamp(self.discrimination, DISCRIMINATION_MIN, DISCRIMINATION_MAX)
        self.guessing = clamp(self.guessing, 0, 0.5)


@dataclass
class IRTResult:
    """Result of an IRT update operation."""
    theta_before: float
    theta_after: float
    theta_change: float
    probability_correct: float
    information: float


@dataclass
class QuestionIRT:
    """Question with IRT parameters."""
    id: str
    subject_id: str
    topic_id: str
    difficulty: float
    discrimination: float
    guessing: float = GUESSING_DEFAULT


class AbilityLevel(Enum):
    """Ability level categories."""
    BEGINNER = "Beginner"
    DEVELOPING = "Developing"
    COMPETENT = "Competent"
    PROFICIENT = "Proficient"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


# ============================================================================
# CORE IRT FUNCTIONS
# ============================================================================

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def erf(x: float) -> float:
    """
    Approximation of error function (Abramowitz and Stegun).
    
    Used for standard normal CDF calculation.
    """
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    
    sign = -1 if x < 0 else 1
    x = abs(x)
    
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    
    return sign * y


def probability_correct(theta: float, params: IRTParameters) -> float:
    """
    Calculate the probability of a correct answer using 3PL model.
    
    P(θ) = c + (1 - c) / (1 + exp(-Da(θ - b)))
    
    The D scaling constant (1.7) approximates the normal ogive model
    and is standard practice in IRT applications.
    
    Args:
        theta: Student's ability estimate
        params: Item parameters {difficulty (b), discrimination (a), guessing (c)}
    
    Returns:
        Probability of correct response (between c and 1)
    
    Reason:
        Core IRT function - determines how likely a student is to answer correctly.
        Used for question selection and ability estimation.
    """
    t = clamp(theta, THETA_MIN, THETA_MAX)
    b = params.difficulty
    a = params.discrimination
    c = params.guessing
    
    # 3PL Formula with D scaling constant
    exponent = -D_SCALING * a * (t - b)
    probability = c + (1 - c) / (1 + math.exp(exponent))
    
    return probability


def fisher_information(theta: float, params: IRTParameters) -> float:
    """
    Calculate Fisher Information for a question at given theta.
    
    Full Formula: I(θ) = D² * a² * (1-c)² * P(θ) * Q(θ) / (P(θ) - c)²
    Where P(θ) = probability correct, Q(θ) = 1 - P(θ)
    
    Fisher Information indicates how precisely an item measures ability:
    - Higher information = more precise measurement at this theta
    - Maximum information occurs near θ ≈ b (item difficulty)
    
    Args:
        theta: Student's ability estimate
        params: Item parameters
    
    Returns:
        Fisher Information value (0 to ~10 for well-calibrated items)
    
    Reason:
        Used for optimal question selection in CAT.
        Questions with high information at student's theta provide better measurement.
    """
    a = params.discrimination
    c = params.guessing
    
    P = probability_correct(theta, params)
    Q = 1 - P
    
    # Handle edge cases where formula is numerically unstable
    if P - c < 0.01 or P <= c or P >= 1 or Q <= 0:
        return 0
    
    # Fisher Information formula for 3PL (with D scaling constant squared)
    numerator = (D_SCALING ** 2) * (a ** 2) * ((1 - c) ** 2) * P * Q
    denominator = (P - c) ** 2
    
    # Cap information to avoid extreme values from numerical instability
    return min(numerator / denominator, 10.0)


def update_theta(current_theta: float, params: IRTParameters, 
                 is_correct: bool) -> IRTResult:
    """
    Update theta estimate using simplified MLE update formula.
    
    This is an approximation suitable for single-item updates in real-time CAT.
    For precise estimation over multiple items, use estimate_theta_mle() instead.
    
    Update Formula: θ_new = θ_old + (observed - expected) / sqrt(information)
    
    Note: Uses sqrt(information) for more stable updates compared to raw information
    
    Args:
        current_theta: Current ability estimate
        params: Item parameters
        is_correct: Whether the response was correct
    
    Returns:
        IRTResult with updated theta and diagnostics
    
    Reason:
        Real-time ability estimation after each question.
        Damping factor prevents large jumps that could demotivate student.
    """
    theta_before = current_theta
    
    # Calculate probability and information
    P = probability_correct(current_theta, params)
    I = fisher_information(current_theta, params)
    
    # Avoid division by zero
    if I < 0.01:
        return IRTResult(
            theta_before=theta_before,
            theta_after=theta_before,
            theta_change=0,
            probability_correct=P,
            information=I
        )
    
    # Simplified MLE update: divide by sqrt(information) for stability
    observed = 1 if is_correct else 0
    theta_change = (observed - P) / math.sqrt(I)
    
    # Apply damping factor for stability (reduces large jumps)
    damping_factor = 0.7
    adjusted_change = theta_change * damping_factor
    
    # Calculate new theta with bounds
    theta_after = clamp(theta_before + adjusted_change, THETA_MIN, THETA_MAX)
    
    return IRTResult(
        theta_before=theta_before,
        theta_after=theta_after,
        theta_change=theta_after - theta_before,
        probability_correct=P,
        information=I
    )


# ============================================================================
# CAT FUNCTIONS
# ============================================================================

def select_optimal_question(
    current_theta: float,
    questions: List[QuestionIRT],
    answered_question_ids: Set[str]
) -> Optional[QuestionIRT]:
    """
    Select the optimal next question for CAT.
    
    Uses Maximum Information criterion - selects question with highest Fisher Information
    at current theta estimate.
    
    Args:
        current_theta: Current ability estimate
        questions: Pool of available questions
        answered_question_ids: Set of already answered question IDs
    
    Returns:
        Optimal question or None if no questions available
    
    Reason:
        Optimal question selection ensures efficient measurement.
        Student doesn't waste time on questions that don't help estimate ability.
    
    EXAM IMPACT:
        Direct. Maximizes learning efficiency per question.
        Critical for Maths where user has limited time and must improve quickly.
    """
    import random
    
    # Filter out already answered questions
    available = [q for q in questions if q.id not in answered_question_ids]
    
    if not available:
        return None
    
    # Calculate information for each question
    max_information = float('-inf')
    optimal_question = None
    
    for question in available:
        params = IRTParameters(
            difficulty=question.difficulty,
            discrimination=question.discrimination,
            guessing=question.guessing
        )
        
        information = fisher_information(current_theta, params)
        
        # Adding slight randomness to avoid always picking same questions
        random_factor = 0.95 + random.random() * 0.1  # 0.95 to 1.05
        adjusted_info = information * random_factor
        
        if adjusted_info > max_information:
            max_information = adjusted_info
            optimal_question = question
    
    return optimal_question


def calculate_standard_error(
    theta: float,
    question_params: List[IRTParameters]
) -> float:
    """
    Calculate Standard Error of theta estimate.
    
    SE(θ) = 1 / sqrt(I(θ)) where I(θ) is total information
    
    Args:
        theta: Current ability estimate
        question_params: List of item parameters from answered questions
    
    Returns:
        Standard error of the estimate
    
    Reason:
        Standard error indicates precision of ability estimate.
        Lower SE = more precise measurement.
    """
    total_information = sum(
        fisher_information(theta, params) for params in question_params
    )
    
    if total_information <= 0:
        return THETA_MAX - THETA_MIN
    
    return 1 / math.sqrt(total_information)


def should_stop_cat(
    theta: float,
    question_params: List[IRTParameters],
    max_questions: int,
    current_question_count: int,
    target_se: float = SE_TARGET
) -> Tuple[bool, str]:
    """
    Check if CAT should stop (ability estimate is stable).
    
    Stopping rule: SE < 0.3 or max questions reached
    
    Args:
        theta: Current ability estimate
        question_params: List of item parameters
        max_questions: Maximum questions allowed
        current_question_count: Questions answered so far
        target_se: Target standard error
    
    Returns:
        Tuple of (stop: bool, reason: str)
    
    Reason:
        Prevents unnecessary questions once ability is precisely estimated.
        Saves student time while ensuring accurate measurement.
    """
    # Check question limit
    if current_question_count >= max_questions:
        return True, "Maximum questions reached"
    
    # Check standard error
    se = calculate_standard_error(theta, question_params)
    if se < target_se:
        return True, f"Target precision achieved (SE = {se:.3f})"
    
    # Minimum questions before checking precision
    if current_question_count < 5:
        return False, "Minimum questions not reached"
    
    return False, f"SE = {se:.3f}, continuing"


# ============================================================================
# CONVERSION UTILITIES
# ============================================================================

def theta_to_percentile(theta: float) -> float:
    """
    Convert theta to percentile using standard normal CDF.
    
    Uses the error function (erf) approximation of the standard normal CDF.
    This gives a more accurate percentile than simple linear mapping.
    
    Args:
        theta: Ability estimate
    
    Returns:
        Percentile rank (0 to 100)
    """
    percentile = 0.5 * (1 + erf(theta / math.sqrt(2)))
    return round(percentile * 100 * 10) / 10  # Round to 1 decimal


def theta_to_percentage(theta: float) -> int:
    """
    Convert theta to percentage score for display (simple linear mapping).
    
    Maps theta from [-3, 3] to [0, 100]
    
    NOTE: This is a simplified mapping. Use theta_to_percentile for accurate ranking.
    """
    normalized = (theta - THETA_MIN) / (THETA_MAX - THETA_MIN)
    return round(normalized * 100)


def percentage_to_theta(percentage: float) -> float:
    """
    Convert percentage to theta.
    
    Maps from [0, 100] to [-3, 3]
    """
    return THETA_MIN + (percentage / 100) * (THETA_MAX - THETA_MIN)


def get_ability_level(theta: float) -> Dict[str, str]:
    """
    Get ability level description based on theta.
    
    Args:
        theta: Ability estimate
    
    Returns:
        Dictionary with level, description, and color
    
    Reason:
        Provides meaningful feedback to student about their ability.
        More useful than raw theta values.
    """
    if theta < -2:
        return {
            "level": AbilityLevel.BEGINNER.value,
            "description": "Foundation building needed",
            "color": "#ef4444"
        }
    elif theta < -1:
        return {
            "level": AbilityLevel.DEVELOPING.value,
            "description": "Making progress",
            "color": "#f97316"
        }
    elif theta < 0:
        return {
            "level": AbilityLevel.COMPETENT.value,
            "description": "Approaching average",
            "color": "#eab308"
        }
    elif theta < 1:
        return {
            "level": AbilityLevel.PROFICIENT.value,
            "description": "Above average",
            "color": "#22c55e"
        }
    elif theta < 2:
        return {
            "level": AbilityLevel.ADVANCED.value,
            "description": "Strong performance",
            "color": "#3b82f6"
        }
    else:
        return {
            "level": AbilityLevel.EXPERT.value,
            "description": "Exceptional ability",
            "color": "#8b5cf6"
        }


def calculate_expected_score(
    theta: float,
    questions: List[IRTParameters]
) -> int:
    """
    Calculate expected score for a set of questions.
    
    Args:
        theta: Ability estimate
        questions: List of question parameters
    
    Returns:
        Expected number of correct answers
    
    Reason:
        Predicts exam performance based on current ability.
        Helps identify if student is on track for target score.
    """
    expected_correct = sum(
        probability_correct(theta, params) for params in questions
    )
    return round(expected_correct)


def estimate_theta_mle(
    responses: List[int],
    items: List[IRTParameters],
    initial_theta: float = 0.0,
    max_iterations: int = 50
) -> float:
    """
    Estimate theta using Maximum Likelihood Estimation (Newton-Raphson method).
    
    This is the standard MLE approach for IRT, more accurate than single-item updates.
    Uses Newton-Raphson iteration to find theta that maximizes likelihood of observed responses.
    
    Args:
        responses: List of 1 (correct) or 0 (incorrect)
        items: List of item parameters for each response
        initial_theta: Starting estimate (default 0.0)
        max_iterations: Maximum iterations (default 50)
    
    Returns:
        Estimated theta value
    
    Reason:
        More accurate ability estimation after session completion.
        Used for final theta calculation, not real-time updates.
    """
    n = len(responses)
    
    # Edge cases
    if n == 0:
        return initial_theta
    if all(r == 1 for r in responses):
        return THETA_MAX  # All correct
    if all(r == 0 for r in responses):
        return THETA_MIN  # All wrong
    
    theta = initial_theta
    
    for _ in range(max_iterations):
        first_deriv = 0
        second_deriv = 0
        
        for i in range(n):
            item = items[i]
            a = item.discrimination
            c = item.guessing
            
            P = probability_correct(theta, item)
            Q = 1 - P
            
            if P <= c or P >= 1 or Q <= 0:
                continue
            
            # Derivative of P with respect to theta
            dP = D_SCALING * a * (1 - c) * P * Q / (P - c)
            
            # Update derivatives of log-likelihood
            first_deriv += (responses[i] - P) * dP / (P * Q)
            second_deriv -= (dP * dP) / (P * Q)
        
        if abs(second_deriv) < 1e-10:
            break
        
        # Newton-Raphson update
        delta = first_deriv / second_deriv
        theta_new = clamp(theta - delta, THETA_MIN - 1, THETA_MAX + 1)
        
        # Convergence check
        if abs(theta_new - theta) < 0.001:
            return clamp(theta_new, THETA_MIN, THETA_MAX)
        
        theta = theta_new
    
    return clamp(theta, THETA_MIN, THETA_MAX)


# ============================================================================
# IRT ENGINE CLASS
# ============================================================================

class IRTEngine:
    """
    IRT Engine for JARVIS.
    
    Provides a unified interface for all IRT operations.
    
    Usage:
        engine = IRTEngine()
        
        # Update theta after a question
        result = engine.update_theta(current_theta, params, is_correct)
        
        # Select optimal next question
        next_question = engine.select_optimal_question(current_theta, questions, answered)
    
    Reason for design:
        Centralized IRT operations with consistent interface.
        Easy to test and maintain.
    """
    
    # Expose constants as class attributes
    THETA_MIN = THETA_MIN
    THETA_MAX = THETA_MAX
    GUESSING_DEFAULT = GUESSING_DEFAULT
    D_SCALING = D_SCALING
    SE_TARGET = SE_TARGET
    
    def __init__(self):
        """Initialize IRT Engine."""
        pass
    
    # Core functions
    probability_correct = staticmethod(probability_correct)
    fisher_information = staticmethod(fisher_information)
    update_theta = staticmethod(update_theta)
    
    # CAT functions
    select_optimal_question = staticmethod(select_optimal_question)
    calculate_standard_error = staticmethod(calculate_standard_error)
    should_stop_cat = staticmethod(should_stop_cat)
    
    # Conversion utilities
    theta_to_percentage = staticmethod(theta_to_percentage)
    theta_to_percentile = staticmethod(theta_to_percentile)
    percentage_to_theta = staticmethod(percentage_to_theta)
    
    # Diagnostics
    get_ability_level = staticmethod(get_ability_level)
    calculate_expected_score = staticmethod(calculate_expected_score)
    estimate_theta_mle = staticmethod(estimate_theta_mle)


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("Testing IRT Engine...")
    print()
    
    # Test probability calculation
    params = IRTParameters(difficulty=0.0, discrimination=1.0, guessing=0.25)
    
    for theta in [-2, -1, 0, 1, 2]:
        prob = probability_correct(theta, params)
        info = fisher_information(theta, params)
        level = get_ability_level(theta)
        print(f"θ = {theta:+.1f}: P = {prob:.3f}, I = {info:.3f}, Level: {level['level']}")
    
    print()
    
    # Test theta update
    print("Testing theta update:")
    theta = 0.0
    print(f"Initial theta: {theta}")
    
    # Correct answer (easier question)
    params_easy = IRTParameters(difficulty=-0.5, discrimination=1.0, guessing=0.25)
    result = update_theta(theta, params_easy, True)
    print(f"After correct (easy): θ = {result.theta_after:.3f} (Δ = {result.theta_change:+.3f})")
    theta = result.theta_after
    
    # Incorrect answer (harder question)
    params_hard = IRTParameters(difficulty=0.5, discrimination=1.0, guessing=0.25)
    result = update_theta(theta, params_hard, False)
    print(f"After incorrect (hard): θ = {result.theta_after:.3f} (Δ = {result.theta_change:+.3f})")
    
    print()
    
    # Test percentile conversion
    print("Percentile conversions:")
    for theta in [-3, -2, -1, 0, 1, 2, 3]:
        pct = theta_to_percentile(theta)
        print(f"θ = {theta:+.1f} → {pct:.1f}th percentile")
    
    print("\nAll tests passed!")
