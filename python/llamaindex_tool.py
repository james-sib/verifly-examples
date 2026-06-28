#!/usr/bin/env python3
"""
Verifly + LlamaIndex — expose email verification as a LlamaIndex tool.

`llama-index-tools-verifly` provides `VeriflyToolSpec`. Call `.to_tool_list()`
and hand the result to any LlamaIndex agent (FunctionAgent, ReActAgent, ...),
or call the spec methods directly.

Setup:
    pip install llama-index-tools-verifly
    export VERIFLY_API_KEY=vf_...        # get one free at https://verifly.email
Run:
    python llamaindex_tool.py

Docs: https://pypi.org/project/llama-index-tools-verifly/
"""
import os
import sys

from llama_index.tools.verifly import VeriflyToolSpec

if not os.environ.get("VERIFLY_API_KEY"):
    sys.exit("Set VERIFLY_API_KEY first (free key at https://verifly.email).")

# api_key defaults to the VERIFLY_API_KEY env var if omitted.
spec = VeriflyToolSpec()

# Tools ready to hand to a LlamaIndex agent.
tools = spec.to_tool_list()
print("tools:", [t.metadata.name for t in tools])

# --- Call the tool directly (returns a llama_index Document) ------------
for email in ("founder@stripe.com", "noreply@github.com"):
    doc = spec.verify_email(email)
    print(f"\n{email}:\n  {doc.text}")

# Real output:
#   tools: ['verify_email']
#   founder@stripe.com:
#     founder@stripe.com: risky (Catch-all server - cannot confirm individual address) - recommendation: risky

# --- Hand the tool to a real agent (optional, needs an LLM) -------------
if os.environ.get("OPENAI_API_KEY"):
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.openai import OpenAI

    agent = FunctionAgent(
        tools=tools,
        llm=OpenAI(model="gpt-4o-mini"),
        system_prompt="You verify email addresses before any outreach.",
    )
    import asyncio
    answer = asyncio.run(
        agent.run("Is 'founder@stripe.com' safe to cold-email? Use the tool.")
    )
    print("\nAGENT:", answer)
else:
    print("\n(Set OPENAI_API_KEY to also run a full FunctionAgent.)")
