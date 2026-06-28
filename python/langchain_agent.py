#!/usr/bin/env python3
"""
Verifly + LangChain — give an agent the power to verify an email before it acts.

`langchain-verifly` ships a ready-made BaseTool, `VeriflyEmailVerifier`. Bind it
to any tool-calling LLM and the model can check deliverability on its own — e.g.
to refuse a fake signup, or to clean a lead before drafting an outreach email.

Setup:
    pip install langchain-verifly langchain-core
    export VERIFLY_API_KEY=vf_...        # get one free at https://verifly.email
Run:
    python langchain_agent.py

The first half runs with NO LLM key (it calls the tool directly, exactly as an
agent would). The second half wires the tool into a real tool-calling LLM and
only runs if OPENAI_API_KEY is set.

Docs: https://pypi.org/project/langchain-verifly/
"""
import os
import sys

from langchain_verifly import VeriflyEmailVerifier

if not os.environ.get("VERIFLY_API_KEY"):
    sys.exit("Set VERIFLY_API_KEY first (free key at https://verifly.email).")

# The tool reads VERIFLY_API_KEY from the env by default.
verifier = VeriflyEmailVerifier()
print(f"tool name : {verifier.name}")
print(f"tool desc : {verifier.description[:80]}...\n")

# --- 1) Direct tool call (this is what the agent invokes) ---------------
for email in ("founder@stripe.com", "noreply@github.com", "test@gmial.com"):
    out = verifier.invoke({"email": email})  # returns a dict
    print(f"{email:>26}  ->  {out['result']:<14} ({out['recommendation']})")
# Real output:
#         founder@stripe.com  ->  risky          (risky)
#         noreply@github.com  ->  undeliverable  (do_not_send)
#             test@gmial.com  ->  undeliverable  (do_not_send)

# --- 2) Full agent loop (optional, needs an LLM) ------------------------
if os.environ.get("OPENAI_API_KEY"):
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage, ToolMessage

    llm = init_chat_model("gpt-4o-mini", model_provider="openai")
    llm_with_tools = llm.bind_tools([verifier])

    messages = [HumanMessage(
        "A user is trying to sign up with 'test@gmial.com'. "
        "Verify it and tell me whether to accept the signup."
    )]
    ai = llm_with_tools.invoke(messages)
    messages.append(ai)

    # Run whatever tool calls the model decided to make.
    for call in ai.tool_calls:
        result = verifier.invoke(call["args"])
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    final = llm_with_tools.invoke(messages)
    print("\nAGENT VERDICT:\n" + final.content)
else:
    print("\n(Set OPENAI_API_KEY to also run the full LLM agent loop.)")
