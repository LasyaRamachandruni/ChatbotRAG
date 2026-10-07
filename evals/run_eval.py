"""Offline evaluation of retrieval and refusals.

    python evals/run_eval.py                    # BM25 retrieval, no LLM needed
    RETRIEVER=hybrid python evals/run_eval.py   # BM25 + MiniLM embeddings
    python evals/run_eval.py --generate         # also call the configured LLM

Metrics
  hit@3 (file)       in-scope questions whose expected file is among the top 3 chunks
  hit@3 (chunk)      stricter: the expected table row / section is among the top 3
  refusal accuracy   out-of-scope questions the bot declines to answer
  false refusals     in-scope questions the bot wrongly declines
  grounded answers   (--generate) in-scope answers that survive the grounding check
                     and cite the expected file
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from llm import get_llm  # noqa: E402
from rag import answer  # noqa: E402
from retrieval import build_retriever  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="also run the LLM step")
    parser.add_argument("--out", help="write the report to this Markdown file")
    args = parser.parse_args()

    questions = [json.loads(line) for line in (ROOT / "evals/questions.jsonl").read_text().splitlines() if line]
    retriever = build_retriever()
    llm = None
    if args.generate:
        configured = get_llm()
        if configured is None:
            sys.exit("--generate needs an LLM provider (see README)")
        llm_name, llm = configured

    rows = []
    hits = chunk_hits = in_scope = refused_ok = out_scope = false_refusals = grounded = 0
    for q in questions:
        top = retriever.search(q["question"], k=3)
        sources = [h.chunk.source for h in top]
        expected = q["expected_source"]
        if expected is None:
            out_scope += 1
            ok = not top
            refused_ok += ok
        else:
            in_scope += 1
            hits += expected in sources
            ok = (expected, q["expected_section"]) in [(h.chunk.source, h.chunk.section) for h in top]
            chunk_hits += ok
            false_refusals += not top
        note = ""
        if llm is not None and expected is not None:
            result = answer(q["question"], retriever, llm)
            good = result.mode == "generated" and expected in [s for _, s in result.sources]
            grounded += good
            note = f"{result.mode}: {result.text}"
        want = f'{expected} / {q["expected_section"]}' if expected else "(refuse)"
        got = "; ".join(f"{h.chunk.source} / {h.chunk.section}" for h in top) or "(refused)"
        rows.append((ok, q["question"], want, got, note))

    lines = [
        f"Retriever: {retriever.mode}, {len(retriever.chunks)} chunks, {len(questions)} questions",
        "",
        f"- hit@3 (file): {hits}/{in_scope} = {hits / in_scope:.0%}",
        f"- hit@3 (chunk): {chunk_hits}/{in_scope} = {chunk_hits / in_scope:.0%}",
        f"- refusal accuracy (out of scope): {refused_ok}/{out_scope} = {refused_ok / out_scope:.0%}",
        f"- false refusals (in scope): {false_refusals}/{in_scope}",
    ]
    if llm is not None:
        lines.append(f"- grounded answers citing the expected file ({llm_name}): "
                     f"{grounded}/{in_scope} = {grounded / in_scope:.0%}")
    lines += ["", "pass = expected chunk in the top 3, or correctly refused.", "", "| pass | question | expected | top-3 retrieved |", "|---|---|---|---|"]
    for ok, question, expected, got, note in rows:
        lines.append(f"| {'yes' if ok else 'NO'} | {question} | {expected} | {got} |")
        if note:
            lines.append(f"| | {note} | | |")
    report = "\n".join(lines)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n")


if __name__ == "__main__":
    main()
