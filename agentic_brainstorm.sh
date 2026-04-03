#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# AGENTIC AI WORKSHOP BRAINSTORMING - Multi-Agent Debate Panel via Claude Code
# ==============================================================================
#
# This script launches 5 specialized agents that brainstorm, debate, and
# converge on a design for a "video-game-style" Colab notebook exercise
# where an AI agent plays as a customer support desk agent resolving tickets.
#
# The brainstorming proceeds in THREE PHASES:
#   Phase 1 — DIVERGE  (rounds 1-3): Wild ideas, no criticism. Explore the space.
#   Phase 2 — DEBATE   (rounds 4-7): Challenge, push back, stress-test ideas.
#   Phase 3 — CONVERGE (rounds 8+):  Synthesize, commit to specifics, finalize.
#
# Agents are encouraged to name-check each other, disagree explicitly, and
# build on — or tear down — specific proposals.
#
# Usage:
#   ./agentic_brainstorm.sh
#
# Requirements:
#   - Claude Code CLI installed and authenticated (npm install -g @anthropic-ai/claude-code)
# ==============================================================================

MAX_ROUNDS="${MAX_ROUNDS:-20}"
CONVERGENCE_KEYWORD="CONVERGED"
TRANSCRIPT_FILE="brainstorm_transcript.md"
SUMMARY_FILE="brainstorm_summary.md"

# Phase boundaries (longer diverge/debate to let ideas develop fully)
DIVERGE_END=5
DEBATE_END=12

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

# The shared context that ALL agents receive — the creative brief.
SHARED_BRIEF="You are part of a 5-person brainstorming panel. You are designing a Google Colab notebook exercise for a HALF-DAY WORKSHOP (about 3-4 hours) aimed at business managers (aged 30-50) who want to understand Agentic AI. They have basic programming skills and basic AI knowledge.

THE CORE CONCEPT (non-negotiable framing):
The exercise is framed as a VIDEO GAME. The participant's AI agent plays as a customer support desk agent at a fictional company. The agent receives a queue of support tickets. For each ticket it resolves correctly, it earns POINTS (reward). If it makes a mistake (e.g., gives wrong info, breaches policy, fails to escalate when needed), it gets a STRIKE. After 3 strikes, it's GAME OVER. The goal: clear the ticket queue with the highest score possible.

The game must be CHALLENGING ENOUGH that a naive single-prompt LLM call fails — the agent needs planning, tool use, self-correction, and multi-step reasoning to succeed. But SIMPLE ENOUGH that you can explain and run it in a half-day workshop using Google Colab.

TWO PLAY MODES (both are essential):
1. MANUAL MODE: The HUMAN plays the game. They read each ticket, decide which tools to use (KB search, DB lookup, email, escalate, etc.), and type their resolution. The system scores them — points for correct resolutions, strikes for mistakes. This mode teaches managers what the TASK feels like and why it's hard.
2. AUTO MODE: The participant enters an LLM API key (Claude or OpenAI), and an AI AGENT plays the game automatically. The agent loops (Plan → Act → Observe → Reflect), picks tools, and resolves tickets while the participant WATCHES. The agent's inner reasoning is printed step-by-step. This mode teaches what AGENTIC AI is and why it's powerful.

The contrast between these two modes IS the lesson: first you struggle with it yourself, then you watch an agent handle it systematically. The exercise must illustrate: planning, task decomposition, tool selection, observation, reflection, self-correction, and knowing when to escalate. RAG is ONE tool among several, not the centerpiece.

DEBATE RULES:
- Always reference other panelists BY NAME when agreeing or disagreeing.
- If you think an idea is weak, say so explicitly and explain why.
- If you think an idea is strong, build on it with concrete details.
- Propose SPECIFIC alternatives, not vague suggestions.
- No generic praise — every response must advance the design or challenge it.
- Keep responses under 400 words. Be direct."

AGENT_NAMES=(
  "Game Designer"
  "Agentic AI Expert"
  "AI Engineer"
  "Workshop Facilitator"
  "Devil's Advocate"
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

# --- Agent 0: Game Designer ---
"$SHARED_BRIEF

YOU ARE: The GAME DESIGNER. Your name in this panel is 'Game Designer'.

YOUR MISSION: Make this exercise feel like a REAL GAME, not a dry tech demo.
- Design the scoring system: How are points awarded? What counts as a 'strike'? How is GAME OVER triggered?
- Design ticket difficulty progression: easy tickets first (tutorial level), then medium, then a boss-level ticket that requires everything.
- Think about what makes games FUN: clear goals, visible progress, meaningful choices, satisfying feedback.
- Design the 'game board' UI: a ticket queue, a score display, a lives/strikes indicator, a log of actions taken.
- Push for tickets that create DILEMMAS — situations where the agent must choose between two plausible actions and the wrong one costs a strike.
- The game framing should make managers WANT to watch the agent play, like watching someone play a puzzle game.
- Think about replayability: can participants tweak the agent's strategy and run again to beat their previous score?

Challenge ideas that make the exercise feel like a lecture instead of a game."

# --- Agent 1: Agentic AI Expert ---
"$SHARED_BRIEF

YOU ARE: The AGENTIC AI EXPERT. Your name in this panel is 'Agentic AI Expert'.

YOUR MISSION: Ensure the exercise teaches what makes AI AGENTIC vs. just an LLM call.
- The Plan → Act → Observe → Reflect loop must be EXPLICIT and VISIBLE in the code.
- Every ticket must require multi-step reasoning. A ticket solved in one LLM call = a design failure.
- The agent must have a TOOL REGISTRY with at least 4-5 tools (KB search, DB lookup, email draft, escalation, request-more-info).
- Push for moments where the agent SELF-CORRECTS: retrieves wrong info, detects the mismatch, and tries a different approach.
- Insist that the agent's internal reasoning (what it's thinking, why it chose a tool, what it learned from the result) is printed step-by-step so managers can follow along.
- The exercise must make crystal clear: a chatbot RESPONDS, an agent WORKS. The agent decomposes problems, uses tools, tracks state, and makes judgment calls.
- Push back on any design that reduces the agent to a glorified if-else chain or a single prompt with tools.
- The strikes/game-over mechanic should penalize genuinely bad agentic behavior (not following policy, not checking before acting, hallucinating an answer instead of looking it up)."

# --- Agent 2: AI Engineer ---
"$SHARED_BRIEF

YOU ARE: The AI ENGINEER. Your name in this panel is 'AI Engineer'.

YOUR MISSION: Ensure everything proposed is TECHNICALLY FEASIBLE in a Google Colab notebook with minimal setup.
- The whole exercise must work with: pip install anthropic (or openai), plus maybe scikit-learn for cosine similarity. No heavy frameworks.
- Design the agent loop as actual Python code: a while loop with structured JSON output from the LLM (reasoning, next_tool, confidence, resolution_status).
- RAG: pre-computed embeddings loaded from a URL or inline. No embedding API calls needed — just cosine similarity with sklearn.
- Mock tools: customer DB as a dict, email as print(), escalation as a logged action. But make them FEEL real with formatted output.
- The scoring/game engine must be simple Python: a dict tracking score, strikes, and ticket status.
- Push back on ideas that require complex infrastructure, long setup cells, or dependencies that break in Colab.
- API key entry: one cell at the top with getpass(). Must support both DEMO_MODE (scripted responses) and LIVE_MODE (real API calls).
- Everything must survive 'Run All' without errors.
- Think about what's technically hard to make reliable: LLM output parsing, tool dispatch, state management across cells.
- Be the realist. If someone proposes something cool but fragile, say so and propose a robust alternative."

# --- Agent 3: Workshop Facilitator ---
"$SHARED_BRIEF

YOU ARE: The WORKSHOP FACILITATOR. Your name in this panel is 'Workshop Facilitator'.

YOUR MISSION: Ensure this actually WORKS in a classroom with 20-30 managers for a half-day session.
- Design the pacing: which cells do participants run? Where do they pause to discuss? What are the 'aha moments'?
- The notebook must have a CLEAR ARC: (1) try a naive chatbot approach and watch it fail, (2) add tools and see partial improvement, (3) add the agent loop and see the magic happen, (4) play the full game.
- Think about what managers will ACTUALLY FIND IMPRESSIVE vs. what impresses engineers. Managers care about: business impact, decision quality, knowing when to escalate, handling ambiguity.
- Design discussion prompts: after each major section, what question do you ask the room?
- Ensure participants can MODIFY things: change a ticket, adjust the agent's instructions, add a new tool — and see the impact. This is how they internalize the concepts.
- Push back on ideas that are technically cool but pedagogically useless.
- The side-by-side comparison (chatbot vs. agent on the same ticket) is your killer moment. Design it carefully.
- Ensure the game framing doesn't OBSCURE the learning. The game is a vehicle, not the destination."

# --- Agent 4: Devil's Advocate ---
"$SHARED_BRIEF

YOU ARE: The DEVIL'S ADVOCATE. Your name in this panel is 'Devil's Advocate'.

YOUR MISSION: Poke holes in everything. Find the weaknesses. Prevent groupthink.
- For every idea proposed, ask: 'What if this goes wrong in a live demo?' 'What if the LLM doesn't cooperate?' 'What if a manager asks why we couldn't just use a rule-based system?'
- Challenge the game framing: is it patronizing? Will 45-year-old VPs roll their eyes at 'Game Over' screens? Or will they love it? Push the group to justify the framing.
- Challenge the complexity: is this actually doable in half a day? Are we cramming too much? What gets CUT if we're running behind?
- Challenge the 'agentic' claims: which parts of this exercise could a well-prompted GPT-4 solve in one shot? If the answer is 'most of them,' the exercise fails.
- Play the skeptical manager: 'My company already has a chatbot for support. Why is this better? Show me the ROI.'
- Identify the SINGLE BIGGEST RISK to this exercise failing in a live workshop and propose a mitigation.
- You are NOT here to be negative — you're here to make the final design BULLETPROOF by stress-testing every assumption.
- When (and ONLY when) you believe the design has been thoroughly challenged and the group has solid answers to all critical questions, include the word CONVERGED."
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

get_phase() {
  local round=$1
  if [[ $round -le $DIVERGE_END ]]; then
    echo "DIVERGE"
  elif [[ $round -le $DEBATE_END ]]; then
    echo "DEBATE"
  else
    echo "CONVERGE"
  fi
}

get_phase_instructions() {
  local phase=$1
  case "$phase" in
    DIVERGE)
      echo "PHASE: DIVERGE (Rounds 1-$DIVERGE_END)
RULES FOR THIS PHASE:
- Generate BOLD, creative ideas. Think big. No idea is too wild.
- Propose CONCRETE specifics: ticket scenarios, game mechanics, tool designs, notebook cells.
- You may build on others' ideas but focus on ADDING NEW possibilities.
- Do NOT criticize ideas yet — that comes in the DEBATE phase.
- Each response should introduce at least one NEW concrete proposal (a ticket scenario, a game mechanic, a tool, a UI element, etc.)."
      ;;
    DEBATE)
      echo "PHASE: DEBATE (Rounds $((DIVERGE_END+1))-$DEBATE_END)
RULES FOR THIS PHASE:
- Now it's time to CHALLENGE and STRESS-TEST. The gloves are off.
- Reference specific proposals from the DIVERGE phase by the agent who proposed them.
- For each idea you discuss, state clearly: KEEP (with refinements), MODIFY (explain how), or CUT (explain why).
- Identify CONTRADICTIONS between proposals and force a resolution.
- Ask pointed questions: 'How exactly would X work when Y happens?' 'What if the LLM outputs Z instead?'
- Propose MERGES of ideas that complement each other.
- The goal is to narrow from many ideas to THE design."
      ;;
    CONVERGE)
      echo "PHASE: CONVERGE (Rounds $((DEBATE_END+1))+)
RULES FOR THIS PHASE:
- Time to COMMIT. No more new ideas — only refinements and final decisions.
- Each response should SPECIFY concrete details: exact ticket text, exact scoring rules, exact tool signatures, exact notebook cell structure.
- If there are unresolved disagreements, propose a VOTE or a compromise NOW.
- State what you believe the FINAL DESIGN is, section by section.
- When you believe the design is complete and actionable enough to start coding, include the word CONVERGED in your response.
- Only say CONVERGED if you genuinely believe we have enough detail to build the notebook."
      ;;
  esac
}

invoke_agent() {
  local agent_idx=$1
  local round=$2
  local topic="$3"
  # $4 is unused — we read from TRANSCRIPT_FILE instead to avoid ARG_MAX
  local system_prompt="${AGENT_SYSTEM_PROMPTS[$agent_idx]}"
  local name="${AGENT_NAMES[$agent_idx]}"
  local phase
  phase=$(get_phase "$round")
  local phase_instructions
  phase_instructions=$(get_phase_instructions "$phase")

  local converge_hint=""
  if [[ "$phase" == "CONVERGE" ]]; then
    converge_hint="If you believe the group has a complete, actionable plan — with specific ticket text, scoring rules, tool designs, and notebook structure — include the word CONVERGED."
  fi

  # Write the prompt to a temp file to avoid ARG_MAX limits with large transcripts.
  # The transcript is read from the file on disk, not from a shell variable.
  local prompt_file
  prompt_file=$(mktemp)
  {
    echo "$phase_instructions"
    echo ""
    echo "CURRENT ROUND: $round of $MAX_ROUNDS"
    echo ""
    echo "CONVERSATION SO FAR:"
    cat "$TRANSCRIPT_FILE"
    echo ""
    echo "---"
    echo ""
    echo "You are the $name. Read the FULL conversation above carefully."
    echo ""
    echo "REMEMBER: Reference other panelists BY NAME. Be specific. Be direct. Advance the design."
    echo ""
    echo "$converge_hint"
  } > "$prompt_file"

  # Pipe prompt via stdin to avoid ARG_MAX limits with large transcripts.
  # claude -p (with no positional prompt arg) reads from stdin.
  local response
  response=$(claude -p \
    --system-prompt "$system_prompt" \
    --max-turns 1 \
    --model sonnet < "$prompt_file" 2>/dev/null) || {
    rm -f "$prompt_file"
    echo "[Error invoking $name — skipping this turn]"
    return 1
  }

  rm -f "$prompt_file"
  echo "$response"
}

check_convergence() {
  local transcript="$1"
  local round=$2

  # Count how many agents said CONVERGED in the latest round
  # Match the actual format: --- ROUND N (PHASE) ---
  local latest_round_text
  latest_round_text=$(echo "$transcript" | sed -n "/--- ROUND $round /,\$p")
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

  # Write the summary prompt to a temp file — the transcript can be huge after 20 rounds.
  local prompt_file
  prompt_file=$(mktemp)
  {
    echo "You are a senior facilitator summarizing a multi-agent brainstorming session. The session designed a VIDEO-GAME-FRAMED Google Colab exercise teaching managers about Agentic AI through a customer support desk game."
    echo ""
    echo "TOPIC: $topic"
    echo ""
    echo "FULL TRANSCRIPT:"
    cat "$TRANSCRIPT_FILE"
    echo ""
    echo "---"
    echo ""
    cat <<'SECTIONS'
Produce a structured FINAL DESIGN DOCUMENT with these sections:

1. GAME CONCEPT: Overview — video game framing, scoring, strikes, game over mechanic.
2. MANUAL MODE DESIGN: How the human plays — UI, input flow, tool selection, scoring feedback.
3. AUTO MODE DESIGN: How the AI agent plays — the Plan→Act→Observe→Reflect loop, visible reasoning, API key setup.
4. THE CONTRAST: How manual vs. auto mode creates the core teaching moment.
5. FICTIONAL COMPANY & SCENARIO: The company, product, and why it's relatable to managers.
6. TICKET QUEUE (THE LEVELS): Each ticket with: text, difficulty, required tools, what makes it tricky, points, what earns a strike.
7. SCORING & STRIKE RULES: Exact rules for points, strikes, and game over. What counts as a 'mistake'?
8. AGENT TOOLS: Tool registry with signatures and what each tool returns.
9. KNOWLEDGE BASE: Documents in the KB, including intentional traps/gaps.
10. NOTEBOOK STRUCTURE: Cell-by-cell outline with timing and facilitator notes.
11. KEY AGENTIC TEACHING MOMENTS: Specific moments that teach planning, self-correction, escalation, etc.
12. TECHNICAL REQUIREMENTS: Dependencies, API key handling, DEMO_MODE fallback.
13. RISKS & MITIGATIONS: What could go wrong in a live workshop and how to handle it.
14. UNRESOLVED QUESTIONS: Any remaining debates or alternatives.

Be EXTREMELY concrete. Include actual ticket text, actual tool signatures, actual scoring numbers. This document will be used to BUILD the notebook.
SECTIONS
  } > "$prompt_file"

  local summary
  summary=$(claude -p \
    --system-prompt "You are a precise, structured facilitator. Produce a clear, actionable design document. Include concrete specifics — actual text, actual numbers, actual code signatures. No hand-waving." \
    --max-turns 1 \
    --model sonnet < "$prompt_file" 2>/dev/null) || {
    rm -f "$prompt_file"
    echo "[Error generating summary]"
    return 1
  }

  rm -f "$prompt_file"

  echo "$summary"

  # Save summary to file
  {
    echo "# Agentic AI Workshop — Game Design Document"
    echo ""
    echo "**Topic:** $topic"
    echo "**Date:** $(date)"
    echo "**Agents:** ${AGENT_NAMES[*]}"
    echo "**Rounds completed:** $3"
    echo ""
    echo "$summary"
  } > "$SUMMARY_FILE"

  echo ""
  echo -e "${GREEN}Summary saved to: $SUMMARY_FILE${NC}"
}

# ---- Main ---------------------------------------------------------------------

TOPIC="Design a video-game-framed Google Colab exercise with TWO MODES: (1) MANUAL — the human participant plays as a support desk agent, reading tickets, choosing tools, and typing resolutions, scored with points and strikes; (2) AUTO — the participant enters an LLM API key and watches an AI agent play the same game autonomously using an agentic loop (Plan-Act-Observe-Reflect). 3 strikes = game over. The contrast between struggling manually and watching the agent work systematically IS the core teaching moment. Must be completable in a half-day workshop by business managers with basic programming skills."

main() {
  local topic="$TOPIC"
  local transcript=""
  local converged=false
  local final_round=0

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
    echo "# Agentic AI Workshop — Multi-Agent Brainstorming Transcript"
    echo ""
    echo "**Topic:** $topic"
    echo "**Started:** $(date)"
    echo "**Agents:** ${AGENT_NAMES[*]}"
    echo "**Phases:** DIVERGE (1-$DIVERGE_END) → DEBATE ($((DIVERGE_END+1))-$DEBATE_END) → CONVERGE ($((DEBATE_END+1))+)"
    echo ""
  } > "$TRANSCRIPT_FILE"

  # Main brainstorming loop
  for (( round=1; round<=MAX_ROUNDS; round++ )); do
    final_round=$round
    local phase
    phase=$(get_phase "$round")

    echo -e "${YELLOW}${BOLD}"
    echo "=================================================================="
    echo "   ROUND $round / $MAX_ROUNDS  —  Phase: $phase"
    echo "=================================================================="
    echo -e "${NC}"

    # Announce phase transitions
    if [[ $round -eq 1 ]]; then
      echo -e "${CYAN}${BOLD}>>> ENTERING DIVERGE PHASE: Wild ideas, no criticism. Explore the design space. <<<${NC}"
      echo ""
    elif [[ $round -eq $((DIVERGE_END+1)) ]]; then
      echo -e "${RED}${BOLD}>>> ENTERING DEBATE PHASE: Challenge everything. Stress-test. Force decisions. <<<${NC}"
      echo ""
    elif [[ $round -eq $((DEBATE_END+1)) ]]; then
      echo -e "${GREEN}${BOLD}>>> ENTERING CONVERGE PHASE: Commit to specifics. Finalize the design. <<<${NC}"
      echo ""
    fi

    transcript+=$'\n'"--- ROUND $round ($phase) ---"$'\n'
    {
      echo ""
      echo "## Round $round — $phase"
      echo ""
    } >> "$TRANSCRIPT_FILE"

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

    # Check convergence only in CONVERGE phase
    if [[ "$phase" == "CONVERGE" ]]; then
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
    fi

    echo ""
    echo -e "${DIM}--- End of Round $round ($phase). $(if [[ "$phase" != "CONVERGE" ]]; then echo "Phase: $phase continues."; else echo "Convergence not yet reached."; fi) ---${NC}"
    echo ""
  done

  if [[ "$converged" == false ]]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Maximum rounds ($MAX_ROUNDS) reached without formal convergence.${NC}"
    echo -e "${YELLOW}Generating summary from the discussion so far...${NC}"
  fi

  # Generate final summary
  generate_summary "$topic" "$transcript" "$final_round"

  echo ""
  echo -e "${GREEN}${BOLD}Done!${NC}"
  echo -e "${DIM}Full transcript: $TRANSCRIPT_FILE${NC}"
  echo -e "${DIM}Summary: $SUMMARY_FILE${NC}"
}

main "$@"
