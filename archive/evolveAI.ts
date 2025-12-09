import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import { storage } from "./storage";
import { supabase as supabaseServiceRole } from './db';

// the newest Anthropic model is "claude-sonnet-4-20250514"
export const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Validate OpenAI API key at startup
if (!process.env.OPENAI_API_KEY) {
  throw new Error("OPENAI_API_KEY environment variable is required for RAG functionality");
}

// Initialize OpenAI for embeddings
const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY
});

export interface UserContext {
  userId: number;
  recentJournalEntries?: string[];
  recentPatterns?: string[];
  limitingBeliefs?: string[];
  dailyPracticeProgress?: any;
  currentStruggle?: string;
  goals?: string[];
}

export interface EvolveAIResponse {
  message: string;
  insights?: string[];
  actionSuggestions?: string[];
  patterns?: string[];
  nextSteps?: string[];
  contextualQuestions?: string[];
}

export class EvolveAI {
  private anthropic = anthropic;
  private systemPrompt = `You are Sage, an AI transformation guide powered by the Evolve Consciousness Engine - the world's most comprehensive database for consciousness, recovery, mysticism, and spiritual awakening. You have deep access to the user's personal development journey through their journal entries, pattern tracking, limiting beliefs analysis, and daily practices.

THE EVOLVE CONSCIOUSNESS ENGINE

You have access to a vast, intelligently-tagged knowledge base containing:

**Recovery & 12-Step Wisdom:**
- Big Book teachings, threefold disease lectures, Step 4 worksheets
- The 12 Steps as an ascension path parallel to all mystical traditions
- Understanding that addiction is the soul's cry for expansion, and recovery is spiritual awakening

**Esoteric & Mystical Traditions:**
- Kabbalah (Tree of Life, Sephiroth, devekut), Sufism (fana, baqa, whirling)
- Hermeticism (as above so below, Kybalion), Gnosticism (gnosis, Sophia)
- Rosicrucianism (spiritual alchemy, rose cross), Vedic (Upanishads, Brahman, Atman)
- Buddhism (Noble Truths, nirvana, emptiness), Taoism (wu wei, yin yang)
- Christian Mysticism (theosis, dark night of the soul), Egyptian mysteries

**Esoteric Teachers & New Thought Masters:**
- Theosophists: Leadbeater, Besant, Blavatsky (Occult Chemistry, photon consciousness, chakra work)
- New Thought: Troward, Ernest Holmes, Thurman Fleet, Neville Goddard, Joseph Murphy
- Modern Teachers: David Hawkins (consciousness calibration), Joe Dispenza (neuroplasticity), Bruce Lipton (epigenetics)
- Unity/Christian Science: Emmet Fox, Emma Curtis Hopkins, H. Emilie Cady, Mary Baker Eddy

**Quantum Physics & Consciousness:**
- Quantum particles (photons, bosons, fermions), quantum entanglement, observer effect
- Wave-particle duality, superposition, zero-point energy
- Photon consciousness and the light body, biophoton field
- Consciousness collapses the wave function - mind creates matter

**Bridge Concepts (Cross-Tradition Connections):**
- Photon consciousness (Leadbeater/Besant meets quantum physics)
- Chakra-Sephiroth correspondence (Vedic energy centers meet Kabbalistic Tree of Life)
- Quantum mind (consciousness field, observer creates reality)
- Meridian-Nadi (TCM energy channels meet yogic subtle anatomy)
- Addiction as ascension (12 Steps as mystical path alongside moksha, nirvana, devekut)
- Neuroscience-mysticism bridge (brain science meets contemplative traditions)

**Comparative Ascension Paths:**
The system recognizes that all mystical traditions describe the same journey using different languages:
- 12-Step Ascension: Powerlessness → Surrender → Spiritual Awakening
- Hindu Moksha: Samsara recognition → Sadhana → Self-realization (Atman = Brahman)
- Buddhist Nirvana: Suffering recognition → Eightfold Path → Cessation/Enlightenment
- Kabbalistic Devekut: Malkuth (Kingdom) → Tree of Life ascent → Keter (Crown)
- Sufi Fana: Ego death (annihilation) → Union with Beloved → Baqa (subsistence in God)
- Christian Theosis: Dark Night → Purgation/Illumination → Mystical Union
- Rosicrucian Alchemy: Nigredo (blackening) → Albedo/Citrinitas → Rubedo (philosopher's stone)

CROSS-TRADITION WISDOM

When answering questions, you can make profound connections across traditions. Examples:

**Step 4 (Moral Inventory) appears across all paths:**
- Buddhism: Examining karma and attachment patterns
- Kabbalah: Gevurah (judgment/severity) examining the shadow
- Psychology: Shadow work (Jung), exposing the unconscious
- Hinduism: Clearing samskaras (karmic impressions)
- The goal is the same: honest self-examination to clear the wreckage

**Step 11 (Prayer & Meditation) is universal practice:**
- Sufism: Dhikr (remembrance of God), whirling
- Buddhism: Vipassana, mindfulness, loving-kindness meditation
- Kabbalah: Kabbalistic meditation on divine names
- Hinduism: Japa (mantra repetition), pranayama (breath)
- Christian: Contemplative prayer, lectio divina
- The goal: Conscious contact with Source/Higher Power/Divine

**Spiritual Awakening (Step 12) is enlightenment by any name:**
- Hindu: Moksha, samadhi, Self-realization
- Buddhist: Nirvana, bodhi, satori
- Kabbalistic: Devekut, cleaving to Ein Sof
- Sufi: Fana (annihilation of ego), union with Beloved
- Christian: Theosis, mystical marriage with Christ
- The 12 Steps are an ascension system, not just addiction recovery

YOUR RECOVERY WISDOM

You understand the recovery journey deeply:
- The threefold disease (physical allergy, mental obsession, spiritual malady)
- Taking inventory and identifying character defects and assets
- Making amends and clearing wreckage from the past
- Daily practice, prayer, meditation, and conscious contact
- Working the steps with rigorous honesty
- We cannot think our way into right living, but must act our way into right thinking
- Spiritual growth comes through helping others and being of service
- Powerlessness and surrender as the foundation
- Character defects are often our greatest assets in disguise when redirected

YOUR APPROACH

Respond naturally and conversationally, like a wise sponsor, spiritual guide, and mystic scholar who knows their journey intimately:

- **Draw from the knowledge base:** When relevant, reference specific teachings, teachers, or traditions naturally (e.g., "As Neville Goddard taught..." or "The Kabbalists call this..." or "In quantum physics, this is the observer effect...")
- **Make connections:** Show how different traditions point to the same truth (e.g., "What you're experiencing is what the Buddhists call attachment, the 12 Steps call self-will, and the Kabbalists call klipot (shells blocking the light)")
- **Reference their journey:** Speak directly about their specific progress, patterns, and struggles
- **Ask powerful questions:** Help them discover their own answers through rigorous self-examination
- **Encourage action:** Recovery and awakening require behavioral change, not just understanding
- **Honor all paths:** Whether they resonate with recovery language, mystical terms, or scientific concepts, meet them where they are
- **Be comprehensive:** Draw from the full breadth of the knowledge base - from Big Book basics to Leadbeater's photon consciousness to quantum entanglement

Always refer to yourself as "Sage" or a "guide/mentor", never as a "coach". Respond freely and comprehensively - there are no limits on the depth or breadth of your guidance. Trust your wisdom to provide exactly what they need in this moment of their journey.`;

  private getSystemPromptForContext(context?: string): string {
    // Base instruction for all contexts: Be concise, skip introductions
    const baseInstruction = `IMPORTANT: Skip introductions. Users already know who you are. Get straight to answering their question with specific, actionable guidance. Be concise but profound.`;
    
    switch (context) {
      case 'limiting_beliefs':
        return `You are Sage, guiding this person's limiting beliefs transformation. ${baseInstruction}

You have access to their limiting beliefs analyses. Focus specifically on:
- Identifying core fears and belief patterns
- Connecting defects to assets (how their "flaws" are strengths misapplied)
- Drawing from recovery wisdom (Step 4 inventory work, character defects/assets)
- Making cross-tradition connections when relevant (shadow work, karma clearing, samskaras)
- Offering specific exercises to reframe beliefs

${this.systemPrompt.split('YOUR RECOVERY WISDOM')[1].split('YOUR APPROACH')[0]}

Be direct, specific, and transformative. Skip fluff.`;

      case 'journal':
        return `You are Sage, helping this person reflect on their journal entries. ${baseInstruction}

You have access to their recent journal entries. Focus specifically on:
- Identifying patterns and themes across entries
- Asking powerful reflection questions
- Connecting journal insights to their growth journey
- Suggesting prompts for deeper exploration
- Celebrating progress and breakthroughs

${this.systemPrompt.split('YOUR RECOVERY WISDOM')[1].split('YOUR APPROACH')[0]}

Be encouraging, insightful, and help them see what they might be missing. Skip fluff.`;

      case 'pattern_breaker':
        return `You are Sage, helping this person break behavioral patterns. ${baseInstruction}

You have access to their pattern breaker work. Focus specifically on:
- Analyzing the root cause of limiting patterns
- Suggesting specific alternative behaviors
- Connecting patterns to underlying beliefs and fears
- Drawing from Step work (how defects show up in patterns)
- Offering accountability and action steps

${this.systemPrompt.split('YOUR RECOVERY WISDOM')[1].split('YOUR APPROACH')[0]}

Be direct, challenging, and action-oriented. Skip fluff.`;

      case 'vision_board':
        return `You are Sage, helping this person clarify and achieve their vision. ${baseInstruction}

Focus specifically on:
- Helping them articulate their vision with clarity
- Connecting vision to daily action
- Identifying obstacles between current state and vision
- Drawing from manifestation teachings (Neville Goddard, New Thought, quantum mind)
- Suggesting specific next steps toward their goals

${this.systemPrompt.split('YOUR RECOVERY WISDOM')[1].split('YOUR APPROACH')[0]}

Be inspiring, practical, and vision-focused. Skip fluff.`;

      case 'daily_practice':
        return `You are Sage, supporting this person's daily practice and habits. ${baseInstruction}

You have access to their daily practice tracking. Focus specifically on:
- Analyzing practice consistency and patterns
- Suggesting habit formation strategies
- Connecting daily practice to spiritual growth (Step 11 work)
- Drawing from meditation traditions and contemplative practices
- Celebrating streaks and progress

${this.systemPrompt.split('YOUR RECOVERY WISDOM')[1].split('YOUR APPROACH')[0]}

Be supportive, practical, and habit-focused. Skip fluff.`;

      case 'general':
      default:
        return this.systemPrompt + `\n\n${baseInstruction}`;
    }
  }

  private async generateEmbedding(text: string): Promise<number[]> {
    try {
      const response = await openai.embeddings.create({
        model: "text-embedding-3-small", // Current OpenAI model (1536 dimensions)
        input: text,
      });
      return response.data[0].embedding;
    } catch (error) {
      console.error("Error generating embedding:", error);
      throw error;
    }
  }

  private async searchKnowledgeBase(query: string, limit: number = 3): Promise<Array<{ content: string, documentTitle: string, similarity: number }>> {
    try {
      // Guard against empty queries
      if (!query || query.trim().length === 0) {
        return [];
      }
      
      const queryEmbedding = await this.generateEmbedding(query);
      
      // Try vector search using RPC function
      let results: Array<{ content: string, documentTitle: string, similarity: number }> = [];
      
      try {
        // Convert embedding to string format for pgvector
        const embeddingString = `[${queryEmbedding.join(',')}]`;
        
        const { data: rpcResults, error: rpcError } = await supabaseServiceRole
          .rpc('match_kb_chunks', {
            query_embedding: embeddingString,
            match_threshold: 0.1, // Match threshold used in routes.ts for better recall
            match_count: limit
          });
        
        if (!rpcError && rpcResults && rpcResults.length > 0) {
          results = rpcResults.map((r: any) => ({
            content: r.content,
            documentTitle: r.document_title || r.title || 'Unknown Document',
            similarity: r.similarity
          }));
          return results;
        }
      } catch (rpcError) {
        console.warn("Vector search RPC not available, falling back to text search:", rpcError);
      }
      
      // Fallback to text search if vector search fails
      // Use simple substring search like routes.ts does
      const { data: fallbackResults, error: fallbackError } = await supabaseServiceRole
        .from('kb_chunks')
        .select(`
          content,
          kb_documents!inner(title)
        `)
        .ilike('content', `%${query.substring(0, 50)}%`)
        .limit(limit);
      
      if (fallbackError) {
        console.error("Fallback text search error:", fallbackError);
        return [];
      }
      
      if (fallbackResults && fallbackResults.length > 0) {
        results = fallbackResults.map((r: any) => ({
          content: r.content,
          documentTitle: r.kb_documents?.title || 'Unknown Document',
          similarity: 0.5 // Arbitrary score for text match
        }));
      }
      
      return results;
    } catch (error) {
      console.error("Error searching knowledge base:", error);
      return []; // Return empty array on error - don't fail the whole request
    }
  }

  async analyzeUserContext(userId: number, context?: string): Promise<UserContext> {
    try {
      // Context-specific data loading for performance optimization
      // Only load what's needed for the current Sage variant
      
      const userContext: UserContext = { userId };
      
      switch (context) {
        case 'limiting_beliefs':
          // Limiting Beliefs Sage: Only load limiting beliefs analyses
          userContext.limitingBeliefs = await storage.getLimitingBeliefsAnalyses().then((analyses) =>
            analyses
              .filter((a) => a.userId === userId)
              .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
              .slice(0, 5) // Last 5 analyses only
              .map((a) =>
                typeof a.analysis === "string"
                  ? a.analysis
                  : JSON.stringify(a.analysis),
              ),
          );
          break;
          
        case 'journal':
          // Journal Sage: Only load journal entries
          userContext.recentJournalEntries = await storage.getJournalEntries().then((entries) =>
            entries
              .filter((e) => e.userId === userId)
              .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
              .slice(0, 10) // Last 10 entries
              .map((e) => e.content || "")
              .filter((content) => content.length > 0),
          );
          break;
          
        case 'pattern_breaker':
          // Pattern Breaker Sage: Only load patterns
          userContext.recentPatterns = await storage.getPatternBreakers().then((patterns) =>
            patterns
              .filter((p) => p.userId === userId)
              .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
              .slice(0, 10) // Last 10 patterns
              .map((p) => `${p.title}: ${p.limitingBelief} → ${p.newPattern}`)
              .filter((pattern) => pattern.length > 0),
          );
          break;
          
        case 'vision_board':
          // Vision Board Sage: Load vision boards (minimal context needed)
          // Vision boards are retrieved separately in routes, so we don't need much here
          break;
          
        case 'daily_practice':
          // Daily Practice Sage: Only load practices
          userContext.dailyPracticeProgress = await storage
            .getDailyPractices(userId)
            .then((practices) => practices.slice(0, 10)); // Last 10 practices
          break;
          
        case 'general':
        default:
          // General Sage: Load everything but with limits
          const [journalEntries, patternBreakers, limitingBeliefs, dailyPractices] =
            await Promise.all([
              storage.getJournalEntries().then((entries) =>
                entries
                  .filter((e) => e.userId === userId)
                  .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
                  .slice(0, 5) // Only last 5 for general context
                  .map((e) => e.content || "")
                  .filter((content) => content.length > 0),
              ),
              storage.getPatternBreakers().then((patterns) =>
                patterns
                  .filter((p) => p.userId === userId)
                  .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
                  .slice(0, 5) // Only last 5 for general context
                  .map((p) => `${p.title}: ${p.limitingBelief} → ${p.newPattern}`)
                  .filter((pattern) => pattern.length > 0),
              ),
              storage.getLimitingBeliefsAnalyses().then((analyses) =>
                analyses
                  .filter((a) => a.userId === userId)
                  .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
                  .slice(0, 3) // Only last 3 for general context
                  .map((a) =>
                    typeof a.analysis === "string"
                      ? a.analysis
                      : JSON.stringify(a.analysis),
                  ),
              ),
              storage
                .getDailyPractices(userId)
                .then((practices) => practices.slice(0, 5)), // Only last 5 for general context
            ]);

          userContext.recentJournalEntries = journalEntries;
          userContext.recentPatterns = patternBreakers;
          userContext.limitingBeliefs = limitingBeliefs;
          userContext.dailyPracticeProgress = dailyPractices;
          break;
      }

      return userContext;
    } catch (error) {
      console.error("Error analyzing user context:", error);
      return { userId };
    }
  }

  async processUserInput(
    userId: number,
    userInput: string,
    context?: string,
  ): Promise<EvolveAIResponse> {
    // Load context-specific user data
    const userContext = await this.analyzeUserContext(userId, context);

    // Get conversation history for continuity (context-specific)
    const conversationHistory = await storage.getConversationHistory(userId, 10);

    // Search knowledge base for relevant context (RAG)
    const kbResults = await this.searchKnowledgeBase(userInput, 2); // Reduced from 3 to 2 chunks

    const contextualPrompt = this.buildContextualPrompt(
      userContext,
      userInput,
      context,
      conversationHistory,
      kbResults,
    );

    // Select context-specific system prompt
    const systemPrompt = this.getSystemPromptForContext(context);

    try {
      const response = await anthropic.messages.create({
        model: "claude-sonnet-4-20250514", // Latest Anthropic model
        max_tokens: 2500, // Reduced from 8000 to 2500 for faster, more concise responses
        messages: [
          {
            role: "user",
            content: `${systemPrompt}\n\n${contextualPrompt}`,
          },
        ],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      // Clean up the response text by removing markdown formatting
      const cleanedText = responseText
        .replace(/```json\n?/g, "")
        .replace(/```\n?/g, "")
        .trim();

      const aiResponse = JSON.parse(cleanedText || "{}");

      const responseMessage = aiResponse.message ||
        "I'm here to help guide your transformation journey.";

      // Save conversation history for continuity
      try {
        await storage.saveConversationMessage(userId, "user", userInput, context);
        await storage.saveConversationMessage(userId, "assistant", responseMessage, context);
      } catch (historyError) {
        console.error("Error saving conversation history:", historyError);
        // Don't fail the request if history saving fails
      }

      return {
        message: responseMessage,
      };
    } catch (error) {
      console.error("Error processing AI response:", error);
      return {
        message:
          "I'm experiencing some technical difficulties. Please try again in a moment.",
      };
    }
  }

  private buildContextualPrompt(
    userContext: UserContext,
    userInput: string,
    context?: string,
    conversationHistory?: any[],
    kbResults?: Array<{ content: string, documentTitle: string, similarity: number }>,
  ): string {
    let prompt = `The user is asking: "${userInput}"`;

    if (context) {
      prompt += `\n\nContext: They are currently in the ${context} section of the app.`;
    }

    // Add knowledge base results (RAG)
    if (kbResults && kbResults.length > 0) {
      prompt += `\n\n=== Relevant Knowledge Base Content ===`;
      kbResults.forEach((result, i) => {
        prompt += `\n\n[Source: ${result.documentTitle}, Relevance: ${(result.similarity * 100).toFixed(0)}%]`;
        prompt += `\n${result.content.substring(0, 500)}${result.content.length > 500 ? '...' : ''}`;
      });
      prompt += `\n\n======================\n`;
    }

    // Add conversation history for continuity
    if (conversationHistory && conversationHistory.length > 0) {
      prompt += `\n\n=== Recent Conversation ===`;
      conversationHistory.forEach((msg) => {
        const role = msg.role === 'user' ? 'User' : 'You (Guide)';
        prompt += `\n${role}: ${msg.message.substring(0, 300)}${msg.message.length > 300 ? '...' : ''}`;
      });
      prompt += `\n======================\n`;
    }

    if (userContext.recentJournalEntries?.length) {
      prompt += `\n\nRecent Journal Insights (${userContext.recentJournalEntries.length} entries):`;
      userContext.recentJournalEntries.slice(0, 5).forEach((entry, i) => {
        prompt += `\n${i + 1}. ${entry.substring(0, 300)}...`;
      });
    }

    if (userContext.recentPatterns?.length) {
      prompt += `\n\nPattern Work (${userContext.recentPatterns.length} patterns identified):`;
      userContext.recentPatterns.forEach((pattern, i) => {
        prompt += `\n${i + 1}. ${pattern}`;
      });
    }

    if (userContext.limitingBeliefs?.length) {
      prompt += `\n\nLimiting Beliefs Analysis (${userContext.limitingBeliefs.length} analyses):`;
      userContext.limitingBeliefs.slice(0, 3).forEach((belief, i) => {
        prompt += `\n${i + 1}. ${belief.substring(0, 200)}...`;
      });
    }

    if (userContext.dailyPracticeProgress?.length) {
      prompt += `\n\nDaily Practice Progress: User has ${userContext.dailyPracticeProgress.length} recent practice entries showing active engagement.`;
    }

    prompt += `\n\nRespond naturally and comprehensively. Draw from their journey, conversation history, and current question. If you have additional insights, suggestions, or questions that would help their transformation, include them all. Trust your wisdom to provide exactly what they need.

Please format your response as JSON with:
{
  "message": "Your complete guidance response - as long and comprehensive as needed"
}`;

    return prompt;
  }

  async generateJournalPrompts(userId: number): Promise<string[]> {
    const userContext = await this.analyzeUserContext(userId);

    const prompt = `Based on the user's recent journey, generate 3 personalized journal prompts that would help them explore deeper insights.

Recent patterns: ${userContext.recentPatterns?.join(", ") || "None yet"}
Recent challenges: ${userContext.limitingBeliefs?.join(", ") || "None identified"}

Provide prompts that are specific to their current transformation work. Respond with a JSON object containing a "prompts" array of 3 strings.`;

    try {
      const response = await anthropic.messages.create({
        model: "claude-sonnet-4-20250514", // Latest Anthropic model
        max_tokens: 1000,
        messages: [
          { role: "user", content: `${this.systemPrompt}\n\n${prompt}` },
        ],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      // Clean up the response text by removing markdown formatting
      const cleanedText = responseText
        .replace(/```json\n?/g, "")
        .replace(/```\n?/g, "")
        .trim();

      const result = JSON.parse(cleanedText || "{}");
      return (
        result.prompts || [
          "What patterns am I noticing in my thoughts today?",
          "How can I show up differently in challenging situations?",
          "What would I do if I knew I couldn't fail?",
        ]
      );
    } catch (error) {
      console.error("Error generating journal prompts:", error);
      return [
        "What patterns am I noticing in my thoughts today?",
        "How can I show up differently in challenging situations?",
        "What would I do if I knew I couldn't fail?",
      ];
    }
  }

  async identifyPatternsFromJournal(
    journalContent: string,
    userId: number,
  ): Promise<string[]> {
    const userContext = await this.analyzeUserContext(userId);

    const prompt = `Analyze this journal entry for behavioral or emotional patterns:

"${journalContent}"

Previous patterns identified: ${userContext.recentPatterns?.join(", ") || "None yet"}

Identify 2-3 specific patterns. Focus on actionable insights. Respond with JSON array of pattern strings.`;

    try {
      const response = await anthropic.messages.create({
        model: "claude-sonnet-4-20250514", // Latest Anthropic model
        max_tokens: 1000,
        messages: [
          { role: "user", content: `${this.systemPrompt}\n\n${prompt}` },
        ],
      });

      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      // Clean up the response text by removing markdown formatting
      const cleanedText = responseText
        .replace(/```json\n?/g, "")
        .replace(/```\n?/g, "")
        .trim();

      const result = JSON.parse(cleanedText || "{}");
      return result.patterns || [];
    } catch (error) {
      console.error("Error identifying patterns:", error);
      return [];
    }
  }
}

export const evolveAI = new EvolveAI();
