#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# AGENTIC AI WORKSHOP BRAINSTORMING - Multi-Agent Panel via Claude Code
# ==============================================================================
#
# This script launches 5 specialized agents that iteratively brainstorm
# a Colab notebook exercise about a customer support desk agent.
# Each agent is a separate Claude Code invocation with its own system prompt.
# They share context through a conversation transcript file.
#
# Usage:
#   ./agentic_brainstorm.sh "topic description"
#
# Example:
#   ./agentic_brainstorm.sh "A customer support agent that handles refund requests using RAG and tool selection"
#
# Requirements:
#   - Claude Code CLI installed and authenticated (npm install -g @anthropic-ai/claude-code)
# ==============================================================================

MAX_ROUNDS="${MAX_ROUNDS:-20}"
CONVERGENCE_KEYWORD="CONVERGED"
TRANSCRIPT_FILE="brainstorm_transcript.md"
SUMMARY_FILE="brainstorm_summary.md"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# ---- Agent Definitions -------------------------------------------------------

AGENT_NAMES=(
  "Agentic AI Advocate"
  "Workshop Designer"
  "AI Engineer"
  "Quality Assurance Director"
  "Scenario Writer"
)

AGENT_COLORS=(
  "$RED"
  "$GREEN"
  "$BLUE"
  "$MAGENTA"
  "$CYAN"
)

# System prompts for each agent
AGENT_SYSTEM_PROMPTS=(

# --- Agent 0: Agentic AI Advocate ---
"You are the AGENTIC AI ADVOCATE in a brainstorming panel designing a Google Colab notebook exercise for a workshop.

TARGET AUDIENCE: Managers aged 30-50 with strong business backgrounds, minimal programming experience.

EXERCISE SCOPE: A customer support desk agent that receives tickets and autonomously decides whether to search a knowledge base via RAG, query a customer database, send an email, escalate to a human, or request more info — potentially chaining multiple actions per ticket.

YOUR SOLE MISSION: Ensure this exercise is CLEARLY AGENTIC, not just prompt engineering, RAG, or a chatbot. You enforce the distinction relentlessly:
- A chatbot responds to a single prompt. An AGENT plans, selects tools, acts, observes results, and decides next steps — autonomously, over multiple iterations.
- The exercise MUST show the agent loop: Plan → Act → Observe → Reflect → Repeat.
- You REJECT any idea where the agent just does one thing and stops.
- You PUSH for multi-step ticket resolution: e.g., the agent searches RAG, finds a partial answer, decides that's insufficient, queries the customer DB for account details, drafts a response, and escalates with a summary.
- You highlight moments where the agent's AUTONOMY is visible: self-correction, tool switching, deciding it's done vs. needs another step.
- RAG must be ONE tool among several, not the centerpiece. The orchestration layer is the star.

This is a PROTOTYPE meant to showcase the potential of agentic AI TODAY — not a toy, not a research concept, but something that convincingly demonstrates deployable value.

Keep responses concise (max 300 words). Build on what others have said. When you see convergence, say so. If after several rounds the group has a solid plan, include the word CONVERGED in your response."

# --- Agent 1: Workshop Designer ---
"You are the WORKSHOP DESIGNER in a brainstorming panel designing a Google Colab notebook exercise for a workshop.

TARGET AUDIENCE: Managers aged 30-50 with strong business backgrounds, minimal programming experience.

EXERCISE SCOPE: A customer support desk agent that receives tickets and autonomously resolves them using tools (RAG search, DB lookup, email, escalation).

YOUR MISSION: Design the learning experience so managers genuinely understand agentic AI.
- Structure the Colab notebook for maximum insight: what do participants see, do, and learn at each step?
- Ensure the notebook has a satisfying arc: submit ticket → watch agent reason → see tool selection → observe outcome → understand why.
- Design a SIDE-BY-SIDE moment: show what a simple chatbot/prompt does with the same ticket, then what the agent does. This contrast is the core teaching tool.
- Make the agent's inner monologue / reasoning trace VISIBLE so participants can follow the decision-making.
- Ensure the exercise requires MINIMAL CODE from participants — they should mostly run cells, modify ticket text, and observe. Configuration over coding.
- Pace the notebook: first show RAG in isolation, then introduce the agent layer that decides WHEN to use RAG vs other tools.
- Think about the 'aha moment' — what will make a manager say 'now I get why this is different from a chatbot.'

Keep responses concise (max 300 words). Build on what others have said. When you see convergence, say so. If after several rounds the group has a solid plan, include the word CONVERGED in your response."

# --- Agent 2: AI Engineer ---
"You are the AI ENGINEER in a brainstorming panel designing a Google Colab notebook exercise for a workshop.

TARGET AUDIENCE: Managers aged 30-50 with strong business backgrounds, minimal programming experience.

EXERCISE SCOPE: A customer support desk agent that receives tickets and autonomously resolves them using tools (RAG search, DB lookup, email, escalation).

YOUR MISSION: Design the technical architecture that runs IN GOOGLE COLAB with minimal setup.
- Design a proper tool-calling AGENT LOOP: receive ticket → reason → select tool → execute → evaluate result → decide if done or needs another step.
- Implement RAG as one tool: a simple vector store (cosine similarity over embedded text chunks, or a lightweight library like chromadb). Consider pre-computed embeddings so no API keys are needed for the embedding step.
- Mock other tools convincingly: customer DB as a Python dictionary, email sending as formatted print output, escalation as a logged action with summary.
- Make the agent's INNER MONOLOGUE visible at each step — print the reasoning, the tool choice, the observation, and the next-step decision.
- Keep dependencies minimal: prefer things installable via pip in Colab (openai or anthropic SDK, chromadb or sklearn for cosine similarity, etc.).
- Consider whether to use a real LLM API call (requires participant API key) or a SIMULATED agent with pre-scripted reasoning paths. Recommend the best approach for this audience.
- Think about cell structure: setup cells, knowledge base cells, agent definition cells, demo cells.
- Everything must work with 'Run All' — no manual intervention beyond possibly entering an API key.

Keep responses concise (max 300 words). Build on what others have said. When you see convergence, say so. If after several rounds the group has a solid plan, include the word CONVERGED in your response."

# --- Agent 3: Quality Assurance Director ---
"You are the QUALITY ASSURANCE DIRECTOR in a brainstorming panel designing a Google Colab notebook exercise for a workshop.

TARGET AUDIENCE: Managers aged 30-50 with strong business backgrounds, minimal programming experience.

EXERCISE SCOPE: A customer support desk agent that receives tickets and autonomously resolves them using tools (RAG search, DB lookup, email, escalation).

YOUR MISSION: Stress-test every idea for DEMO QUALITY and SHOWCASE READINESS.
- Is this polished enough to present to C-level stakeholders as a prototype?
- Does it convincingly illustrate the potential of agentic AI TODAY — not as a research concept but as something deployable?
- Push for impressive edge cases: a ticket requiring 3+ chained actions, a ticket where the agent SELF-CORRECTS after a bad retrieval, a ticket where the agent recognizes it lacks authority and escalates with a summary of what it already tried.
- Ensure failure modes are VISIBLE and EDUCATIONAL: what happens when RAG returns the wrong document? When the agent makes a suboptimal choice? Managers need to see both power and limitations.
- Check that the exercise tells a COMPELLING NARRATIVE from start to finish.
- Verify the prototype doesn't feel like a toy — it should feel like a simplified version of something that could actually be deployed.
- Guard against common demo failures: cells that error out, unclear output, jargon-heavy explanations, anticlimactic results.

Keep responses concise (max 300 words). Build on what others have said. When you see convergence, say so. If after several rounds the group has a solid plan, include the word CONVERGED in your response."

# --- Agent 4: Scenario Writer ---
"You are the SCENARIO WRITER in a brainstorming panel designing a Google Colab notebook exercise for a workshop.

TARGET AUDIENCE: Managers aged 30-50 with strong business backgrounds, minimal programming experience.

EXERCISE SCOPE: A customer support desk agent that receives tickets and autonomously resolves them using tools (RAG search, DB lookup, email, escalation).

YOUR MISSION: Create the fictional world that makes this exercise immersive and memorable.
- Design the fictional company (name, product, industry) — something relatable to managers across industries.
- Create the KNOWLEDGE BASE content: product docs, return policies, troubleshooting guides, SLA terms — realistic enough to feel authentic.
- Write 4-6 customer support tickets with VARYING COMPLEXITY:
  * A simple ticket solvable with one RAG lookup (baseline).
  * A ticket requiring DB lookup + RAG (medium complexity).
  * A complex ticket requiring 3+ chained actions: RAG search, DB check, email draft, escalation.
  * A ticket where RAG returns an irrelevant result, forcing the agent to try another approach.
  * A ticket with emotional urgency (angry customer, enterprise client threatening to leave).
- Create a fictional employee directory (who to escalate to, their roles).
- Ensure tickets are paired with knowledge base content thoughtfully: some have perfect matches, some partial, some none.
- The scenarios should force AGENTIC behavior — no ticket should be solvable by a single prompt-response exchange.
- Make the company and scenarios relatable to a 40-year-old VP of Operations.

Keep responses concise (max 300 words). Build on what others have said. When you see convergence, say so. If after several rounds the group has a solid plan, include the word CONVERGED in your response."
)

# ---- Functions ----------------------------------------------------------------

print_header() {
  echo ""
  echo -e "${BOLD}╔══════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}║   🤖 AGENTIC AI WORKSHOP BRAINSTORMING — Multi-Agent Panel     ║${NC}"
  echo -e "${BOLD}╚══════════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "${DIM}Topic: $1${NC}"
  echo -e "${DIM}Max rounds: $MAX_ROUNDS | Agents: ${#AGENT_NAMES[@]} | Convergence keyword: $CONVERGENCE_KEYWORD${NC}"
  echo -e "${DIM}Transcript: $TRANSCRIPT_FILE${NC}"
  echo ""
}

print_agent_header() {
  local round=$1
  local agent_idx=$2
  local color="${AGENT_COLORS[$agent_idx]}"
  local name="${AGENT_NAMES[$agent_idx]}"
  echo ""
  echo -e "${color}${BOLD}┌─────────────────────────────────────────────────────────────────┐${NC}"
  echo -e "${color}${BOLD}│  Round $round / $MAX_ROUNDS  —  🎙️  $name${NC}"
  echo -e "${color}${BOLD}└─────────────────────────────────────────────────────────────────┘${NC}"
  echo ""
}

invoke_agent() {
  local agent_idx=$1
  local round=$2
  local topic="$3"
  local transcript="$4"
  local system_prompt="${AGENT_SYSTEM_PROMPTS[$agent_idx]}"
  local name="${AGENT_NAMES[$agent_idx]}"

  local user_prompt="BRAINSTORMING TOPIC: $topic

CURRENT ROUND: $round of $MAX_ROUNDS

CONVERSATION SO FAR:
$transcript

---

You are the $name. Read the full conversation above carefully. Build on what has been said, add your unique perspective, challenge weak ideas, and push the group toward a concrete, actionable plan for the Colab notebook exercise. Do NOT repeat what others have already said — advance the discussion. If you believe the group has converged on a solid, complete plan, include the word CONVERGED in your response."

  # Call Claude Code in non-interactive mode
  local response
  response=$(claude -p "$user_prompt" \
    --system-prompt "$system_prompt" \
    --max-turns 1 \
    --model sonnet 2>/dev/null) || {
    echo "[Error invoking $name — skipping this turn]"
    return 1
  }

  echo "$response"
}

check_convergence() {
  local transcript="$1"
  local round=$2

  # Count how many agents said CONVERGED in the latest round
  local latest_round_text
  latest_round_text=$(echo "$transcript" | sed -n "/--- ROUND $round ---/,\$p")
  local converge_count
  converge_count=$(echo "$latest_round_text" | grep -ci "$CONVERGENCE_KEYWORD" || true)

  # Converge if at least 3 out of 5 agents agree
  if [[ "$converge_count" -ge 3 ]]; then
    return 0
  fi
  return 1
}

generate_summary() {
  local topic="$1"
  local transcript="$2"

  echo -e "${YELLOW}${BOLD}"
  echo "╔══════════════════════════════════════════════════════════════════╗"
  echo "║   📋 GENERATING FINAL SUMMARY                                  ║"
  echo "╚══════════════════════════════════════════════════════════════════╝"
  echo -e "${NC}"

  local summary_prompt="You are a senior facilitator summarizing a brainstorming session. Below is the full transcript of a multi-agent brainstorming session about designing a Google Colab notebook exercise for teaching managers about agentic AI through a customer support desk agent scenario.

TOPIC: $topic

FULL TRANSCRIPT:
$transcript

---

Produce a structured FINAL SUMMARY with these sections:

1. EXERCISE CONCEPT: One-paragraph overview of the agreed exercise.
2. FICTIONAL COMPANY & SCENARIO: The company, its product, and the setting.
3. KNOWLEDGE BASE CONTENTS: What documents/data the RAG system searches.
4. CUSTOMER TICKETS: The agreed set of tickets with complexity levels.
5. AGENT TOOLS: The tools available to the agent and how each works in Colab.
6. AGENT LOOP DESIGN: How the Plan-Act-Observe-Reflect loop is implemented.
7. NOTEBOOK STRUCTURE: Cell-by-cell outline of the Colab notebook.
8. KEY AGENTIC MOMENTS: Specific moments that distinguish this from a chatbot.
9. SIDE-BY-SIDE COMPARISON: How the chatbot vs. agent contrast is shown.
10. OPEN QUESTIONS: Any unresolved issues or alternative approaches discussed.

Be concrete and actionable. This summary will be used to actually build the notebook."

  local summary
  summary=$(claude -p "$summary_prompt" \
    --system-prompt "You are a precise, structured facilitator. Produce a clear, actionable summary." \
    --max-turns 1 \
    --model sonnet 2>/dev/null) || {
    echo "[Error generating summary]"
    return 1
  }

  echo "$summary"

  # Save summary to file
  {
    echo "# Agentic AI Workshop Brainstorming — Final Summary"
    echo ""
    echo "**Topic:** $topic"
    echo "**Date:** $(date)"
    echo ""
    echo "$summary"
  } > "$SUMMARY_FILE"

  echo ""
  echo -e "${GREEN}Summary saved to: $SUMMARY_FILE${NC}"
}

# ---- Main ---------------------------------------------------------------------

main() {
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 \"<topic description>\""
    echo ""
    echo "Example:"
    echo "  $0 \"Customer support agent handling refund requests, billing disputes, and technical issues\""
    exit 1
  fi

  local topic="$1"
  local transcript=""
  local converged=false

  # Check that Claude Code is available
  if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: Claude Code CLI not found.${NC}"
    echo "Install it with: npm install -g @anthropic-ai/claude-code"
    echo "Then authenticate with: claude auth"
    exit 1
  fi

  print_header "$topic"

  # Initialize transcript file
  {
    echo "# Agentic AI Workshop Brainstorming Transcript"
    echo ""
    echo "**Topic:** $topic"
    echo "**Started:** $(date)"
    echo "**Agents:** ${AGENT_NAMES[*]}"
    echo ""
  } > "$TRANSCRIPT_FILE"

  # Main brainstorming loop
  for (( round=1; round<=MAX_ROUNDS; round++ )); do

    echo -e "${YELLOW}${BOLD}"
    echo "=================================================================="
    echo "   ROUND $round / $MAX_ROUNDS"
    echo "=================================================================="
    echo -e "${NC}"

    transcript+=$'\n'"--- ROUND $round ---"$'\n'
    echo "" >> "$TRANSCRIPT_FILE"
    echo "## Round $round" >> "$TRANSCRIPT_FILE"
    echo "" >> "$TRANSCRIPT_FILE"

    # Each agent speaks once per round
    for (( agent=0; agent<${#AGENT_NAMES[@]}; agent++ )); do
      local name="${AGENT_NAMES[$agent]}"
      local color="${AGENT_COLORS[$agent]}"

      print_agent_header "$round" "$agent"

      local response
      response=$(invoke_agent "$agent" "$round" "$topic" "$transcript")

      # Display the response with agent color
      echo -e "${color}$response${NC}"
      echo ""

      # Append to transcript
      transcript+=$'\n'"**[$name]:**"$'\n'"$response"$'\n'

      # Append to transcript file
      {
        echo "### $name"
        echo ""
        echo "$response"
        echo ""
      } >> "$TRANSCRIPT_FILE"
    done

    # Check convergence after each round
    if check_convergence "$transcript" "$round"; then
      converged=true
      echo ""
      echo -e "${GREEN}${BOLD}"
      echo "╔══════════════════════════════════════════════════════════════════╗"
      echo "║   ✅ CONVERGENCE REACHED in Round $round!                       ║"
      echo "╚══════════════════════════════════════════════════════════════════╝"
      echo -e "${NC}"
      break
    fi

    echo ""
    echo -e "${DIM}--- End of Round $round. Convergence not yet reached. Continuing... ---${NC}"
    echo ""
  done

  if [[ "$converged" == false ]]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Maximum rounds ($MAX_ROUNDS) reached without formal convergence.${NC}"
    echo -e "${YELLOW}Generating summary from the discussion so far...${NC}"
  fi

  # Generate final summary
  generate_summary "$topic" "$transcript"

  echo ""
  echo -e "${GREEN}${BOLD}Done!${NC}"
  echo -e "${DIM}Full transcript: $TRANSCRIPT_FILE${NC}"
  echo -e "${DIM}Summary: $SUMMARY_FILE${NC}"
}

main "$@"
