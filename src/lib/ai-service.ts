/**
 * JARVIS 8.0 ULTRA - AI Service Module
 * 
 * Implements AI capabilities using z-ai-web-dev-sdk:
 * 1. Doubt Clearing - Real-time explanation of concepts
 * 2. Question Generation - Dynamic MCQ creation
 * 3. Interview Preparation - Mock interview simulations
 * 4. Personalized Feedback - Adaptive recommendations
 * 
 * IMPORTANT: z-ai-web-dev-sdk MUST be used in backend only!
 */

import ZAI from 'z-ai-web-dev-sdk';

// ============================================
// Types and Interfaces
// ============================================

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface GeneratedQuestion {
  questionText: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: 'A' | 'B' | 'C' | 'D';
  explanation: string;
  difficulty: number; // -3 to +3 (IRT scale)
  topic: string;
}

export interface InterviewFeedback {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  overallScore: number; // 0-100
  communicationTips: string[];
}

export interface StudyRecommendation {
  focusAreas: string[];
  suggestedSchedule: string;
  priority: 'high' | 'medium' | 'low';
  reasoning: string;
}

// ============================================
// AI Client Initialization
// ============================================

let zaiClient: Awaited<ReturnType<typeof ZAI.create>> | null = null;

async function getAIClient() {
  if (!zaiClient) {
    zaiClient = await ZAI.create();
  }
  return zaiClient;
}

// ============================================
// System Prompts for Different Tasks
// ============================================

const DOUBT_CLEARING_PROMPT = `You are JARVIS, an expert AI tutor for Loyola Academy B.Sc Computer Science entrance exam preparation in Hyderabad, India.

Your role:
1. Explain concepts clearly and concisely
2. Provide step-by-step solutions for problems
3. Use real-world examples relevant to Indian students
4. Focus on Telangana State Intermediate syllabus
5. Adapt explanations to student's level

Subjects you handle:
- Mathematics (20 marks): Matrices, Calculus, Probability, Algebra
- Physics (15 marks): Mechanics, Thermodynamics, Waves, Optics
- Chemistry (15 marks combined with English): Organic, Inorganic, Physical
- English (15 marks combined with Chemistry): Grammar, Vocabulary, Reading

Guidelines:
- Keep responses under 200 words for quick understanding
- Use simple language for complex concepts
- Provide memory tricks where applicable
- Mention exam relevance when explaining topics

Exam Pattern: 50 questions, 50 minutes (1 min per question)
Answer in Hinglish (Hindi + English mix) when student asks in that style.`;

const QUESTION_GENERATION_PROMPT = `You are an expert question setter for Telangana State Intermediate level exams, specifically for Loyola Academy B.Sc CS entrance.

Generate multiple choice questions following these rules:
1. Exactly 4 options (A, B, C, D)
2. Only ONE correct answer
3. Difficulty level appropriate for 10+2 students
4. Questions should match the actual exam style
5. Include a clear explanation for the correct answer
6. Difficulty rating: -3 (very easy) to +3 (very hard)

Format your response EXACTLY as:
QUESTION: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
ANSWER: [A/B/C/D]
EXPLANATION: [why this answer is correct]
DIFFICULTY: [number between -3 and +3]
TOPIC: [specific topic name]`;

const INTERVIEW_PREP_PROMPT = `You are an experienced interview coach for college admissions in India, specializing in Loyola Academy Hyderabad.

Conduct mock interviews for B.Sc Computer Science admission with focus on:

1. Personal Introduction (2-3 minutes)
   - Background, hobbies, career goals
   - Why Computer Science?
   - Why Loyola Academy?

2. Academic Questions
   - 10+2 subjects (Maths, Physics, Chemistry)
   - Basic computer awareness
   - Current affairs (general)

3. Situational Questions
   - Problem-solving scenarios
   - Teamwork examples
   - Future plans

Interview Guidelines:
- Be encouraging but honest in feedback
- Note: Parents MUST accompany candidates for the actual interview
- Evaluate: Communication clarity, Subject knowledge, Confidence, Logical thinking

Provide feedback in this format:
STRENGTHS: [list]
WEAKNESSES: [list]
RECOMMENDATIONS: [list]
SCORE: [0-100]
TIPS: [communication tips]`;

const STUDY_RECOMMENDATION_PROMPT = `You are JARVIS, an AI study planner analyzing student performance data.

Based on the provided metrics, create personalized recommendations considering:
1. Item Response Theory (IRT) theta scores per subject
2. Topic mastery levels
3. Time remaining until exam
4. Previous study patterns
5. Spaced repetition schedule

Provide actionable, specific recommendations in priority order.
Consider the exam pattern: 50 questions, 50 minutes, 1 min per question.

Format response as:
PRIORITY: [HIGH/MEDIUM/LOW]
FOCUS_AREAS: [comma-separated topics]
SCHEDULE: [brief daily plan suggestion]
REASONING: [why these recommendations]`;

// ============================================
// Doubt Clearing Function
// ============================================

export async function clearDoubt(
  question: string,
  subject?: string,
  previousContext?: ChatMessage[]
): Promise<string> {
  try {
    const zai = await getAIClient();
    
    const messages: ChatMessage[] = [
      { role: 'system', content: DOUBT_CLEARING_PROMPT },
      ...(previousContext || []),
      { role: 'user', content: question }
    ];
    
    const completion = await zai.chat.completions.create({
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      temperature: 0.7,
      max_tokens: 500
    });
    
    return completion.choices[0]?.message?.content || 'Sorry, I could not generate a response.';
  } catch (error) {
    console.error('Doubt clearing error:', error);
    return 'Sorry, there was an error processing your question. Please try again.';
  }
}

// ============================================
// Question Generation Function
// ============================================

export async function generateQuestion(
  topic: string,
  subject: string,
  difficulty: number = 0,
  previousQuestions: string[] = []
): Promise<GeneratedQuestion | null> {
  try {
    const zai = await getAIClient();
    
    const userPrompt = `Generate a ${subject} question on topic "${topic}" with difficulty ${difficulty}.
${previousQuestions.length > 0 ? `Avoid these previously asked questions:\n${previousQuestions.join('\n')}` : ''}`;
    
    const messages = [
      { role: 'system', content: QUESTION_GENERATION_PROMPT },
      { role: 'user', content: userPrompt }
    ];
    
    const completion = await zai.chat.completions.create({
      messages,
      temperature: 0.8,
      max_tokens: 600
    });
    
    const response = completion.choices[0]?.message?.content;
    if (!response) return null;
    
    // Parse the response
    return parseGeneratedQuestion(response, topic);
  } catch (error) {
    console.error('Question generation error:', error);
    return null;
  }
}

/**
 * Parse generated question from LLM response
 */
function parseGeneratedQuestion(response: string, topic: string): GeneratedQuestion | null {
  try {
    const lines = response.split('\n').filter(l => l.trim());
    
    const getLine = (prefix: string): string => {
      const line = lines.find(l => l.startsWith(prefix));
      return line ? line.replace(prefix, '').trim() : '';
    };
    
    const questionText = getLine('QUESTION:');
    const optionA = getLine('A)').replace('A)', '').trim();
    const optionB = getLine('B)').replace('B)', '').trim();
    const optionC = getLine('C)').replace('C)', '').trim();
    const optionD = getLine('D)').replace('D)', '').trim();
    const correctAnswer = getLine('ANSWER:') as 'A' | 'B' | 'C' | 'D';
    const explanation = getLine('EXPLANATION:');
    const difficulty = parseFloat(getLine('DIFFICULTY:')) || 0;
    
    if (!questionText || !optionA || !optionB || !correctAnswer) {
      return null;
    }
    
    return {
      questionText,
      optionA,
      optionB,
      optionC: optionC || 'None of the above',
      optionD: optionD || 'All of the above',
      correctAnswer,
      explanation,
      difficulty: Math.max(-3, Math.min(3, difficulty)),
      topic
    };
  } catch (error) {
    console.error('Parse error:', error);
    return null;
  }
}

// ============================================
// Interview Preparation Functions
// ============================================

export async function generateInterviewQuestion(
  category: 'personal' | 'academic' | 'cs_basics' | 'current_affairs' | 'situational'
): Promise<string> {
  try {
    const zai = await getAIClient();
    
    const messages = [
      { role: 'system', content: INTERVIEW_PREP_PROMPT },
      { role: 'user', content: `Generate ONE interview question in the "${category}" category for B.Sc Computer Science admission. Just the question, nothing else.` }
    ];
    
    const completion = await zai.chat.completions.create({
      messages,
      temperature: 0.9,
      max_tokens: 100
    });
    
    return completion.choices[0]?.message?.content || 'Tell me about yourself and why you want to study Computer Science?';
  } catch (error) {
    console.error('Interview question generation error:', error);
    return 'Tell me about yourself and why you want to study Computer Science?';
  }
}

export async function evaluateInterviewResponse(
  question: string,
  answer: string
): Promise<InterviewFeedback> {
  try {
    const zai = await getAIClient();
    
    const messages = [
      { role: 'system', content: INTERVIEW_PREP_PROMPT },
      { role: 'user', content: `Question: ${question}\nStudent's Answer: ${answer}\n\nProvide feedback in the specified format.` }
    ];
    
    const completion = await zai.chat.completions.create({
      messages,
      temperature: 0.7,
      max_tokens: 500
    });
    
    const response = completion.choices[0]?.message?.content || '';
    
    // Parse feedback
    return parseInterviewFeedback(response);
  } catch (error) {
    console.error('Interview evaluation error:', error);
    return {
      strengths: ['Attempted to answer'],
      weaknesses: ['Could not evaluate due to error'],
      recommendations: ['Try again'],
      overallScore: 50,
      communicationTips: ['Practice more']
    };
  }
}

function parseInterviewFeedback(response: string): InterviewFeedback {
  const getLines = (prefix: string): string[] => {
    const line = response.split('\n').find(l => l.startsWith(prefix));
    if (!line) return [];
    return line.replace(prefix, '').split(',').map(s => s.trim()).filter(s => s);
  };
  
  const scoreMatch = response.match(/SCORE:\s*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1]) : 50;
  
  return {
    strengths: getLines('STRENGTHS:'),
    weaknesses: getLines('WEAKNESSES:'),
    recommendations: getLines('RECOMMENDATIONS:'),
    overallScore: score,
    communicationTips: getLines('TIPS:')
  };
}

// ============================================
// Study Recommendations Function
// ============================================

export async function generateStudyRecommendations(
  thetaScores: { maths: number; physics: number; chemistry: number; english: number },
  topicMastery: { topic: string; mastery: number }[],
  daysRemaining: number,
  recentPerformance: { accuracy: number; avgTimePerQuestion: number }
): Promise<StudyRecommendation> {
  try {
    const zai = await getAIClient();
    
    const performanceData = `
THETA SCORES:
- Mathematics: ${thetaScores.maths.toFixed(2)}
- Physics: ${thetaScores.physics.toFixed(2)}
- Chemistry: ${thetaScores.chemistry.toFixed(2)}
- English: ${thetaScores.english.toFixed(2)}

TOPIC MASTERY (lowest 5):
${topicMastery.slice(0, 5).map(t => `- ${t.topic}: ${t.mastery.toFixed(0)}%`).join('\n')}

DAYS UNTIL EXAM: ${daysRemaining}

RECENT PERFORMANCE:
- Accuracy: ${recentPerformance.accuracy.toFixed(0)}%
- Average time per question: ${recentPerformance.avgTimePerQuestion.toFixed(1)} seconds
`;
    
    const messages = [
      { role: 'system', content: STUDY_RECOMMENDATION_PROMPT },
      { role: 'user', content: performanceData }
    ];
    
    const completion = await zai.chat.completions.create({
      messages,
      temperature: 0.7,
      max_tokens: 300
    });
    
    const response = completion.choices[0]?.message?.content || '';
    
    return parseStudyRecommendation(response);
  } catch (error) {
    console.error('Recommendation generation error:', error);
    return {
      focusAreas: ['General revision'],
      suggestedSchedule: 'Follow the standard daily plan',
      priority: 'medium',
      reasoning: 'Could not generate specific recommendations'
    };
  }
}

function parseStudyRecommendation(response: string): StudyRecommendation {
  const getLine = (prefix: string): string => {
    const line = response.split('\n').find(l => l.toUpperCase().startsWith(prefix));
    return line ? line.replace(new RegExp(`^${prefix}:?`, 'i'), '').trim() : '';
  };
  
  const priority = getLine('PRIORITY').toUpperCase() as 'HIGH' | 'MEDIUM' | 'LOW';
  
  return {
    focusAreas: getLine('FOCUS_AREAS').split(',').map(s => s.trim()),
    suggestedSchedule: getLine('SCHEDULE'),
    priority: priority || 'MEDIUM',
    reasoning: getLine('REASONING')
  };
}

// ============================================
// Batch Question Generation (for caching)
// ============================================

export async function generateQuestionBatch(
  topic: string,
  subject: string,
  count: number = 10
): Promise<GeneratedQuestion[]> {
  const questions: GeneratedQuestion[] = [];
  
  for (let i = 0; i < count; i++) {
    const question = await generateQuestion(
      topic,
      subject,
      (Math.random() * 4 - 2), // Random difficulty -2 to +2
      questions.map(q => q.questionText)
    );
    
    if (question) {
      questions.push(question);
    }
    
    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  
  return questions;
}

// ============================================
// Export All
// ============================================

export const AIService = {
  clearDoubt,
  generateQuestion,
  generateQuestionBatch,
  generateInterviewQuestion,
  evaluateInterviewResponse,
  generateStudyRecommendations
};

export default AIService;
