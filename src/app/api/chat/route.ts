/**
 * JARVIS API - Chat/Doubt Clearing Endpoint
 * Uses z-ai-web-dev-sdk for AI-powered doubt clearing
 */

import { NextRequest, NextResponse } from 'next/server';
import ZAI from 'z-ai-web-dev-sdk';

const SYSTEM_PROMPT = `You are JARVIS, an expert AI tutor for Loyola Academy B.Sc Computer Science entrance exam preparation in Hyderabad, India.

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
- For math problems, show step-by-step solutions

Exam Pattern: 50 questions, 50 minutes (1 min per question)
Answer in Hinglish (Hindi + English mix) when student asks in that style.`;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, subject, context } = body;

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    const zai = await ZAI.create();

    // Build messages array
    const messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }> = [
      { role: 'system', content: SYSTEM_PROMPT }
    ];

    // Add context if provided (previous conversation)
    if (context && Array.isArray(context)) {
      for (const msg of context) {
        messages.push({
          role: msg.role,
          content: msg.content
        });
      }
    }

    // Add subject context if provided
    if (subject) {
      messages.push({
        role: 'user',
        content: `[Context: Student is asking about ${subject}] ${message}`
      });
    } else {
      messages.push({
        role: 'user',
        content: message
      });
    }

    const completion = await zai.chat.completions.create({
      messages,
      temperature: 0.7,
      max_tokens: 500
    });

    const response = completion.choices[0]?.message?.content || 'Sorry, I could not generate a response.';

    return NextResponse.json({
      success: true,
      response,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to process your question. Please try again.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'JARVIS Chat API',
    description: 'AI-powered doubt clearing for B.Sc CS entrance preparation',
    usage: {
      method: 'POST',
      body: {
        message: 'string (required) - Your question',
        subject: 'string (optional) - maths, physics, chemistry, english',
        context: 'array (optional) - Previous messages for context'
      }
    }
  });
}
