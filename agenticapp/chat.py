"""Interactive CLI chat over the logging guidelines."""
import argparse

import config
import rag


def answer(question: str, n_results: int, theme: str | None, doc_type: str | None,
           show_sources: bool) -> None:
    hits = rag.search(question, n_results=n_results, theme=theme, doc_type=doc_type)
    if not hits:
        print("No matching guidelines found.")
        return

    for text in rag.stream_answer(question, hits):
        print(text, end="", flush=True)
    print()

    if show_sources:
        print("\nSources:")
        for index, hit in enumerate(hits, start=1):
            print(f"  [{index}] {hit.source}  (distance {hit.distance:.3f})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="*", help="Ask once and exit.")
    parser.add_argument("-k", "--n-results", type=int, default=config.DEFAULT_N_RESULTS)
    parser.add_argument("--theme")
    parser.add_argument("--doc-type", choices=["guideline", "example", "theme", "literature",
                                               "occurrence"])
    parser.add_argument("--no-sources", action="store_true")
    args = parser.parse_args()

    show_sources = not args.no_sources

    if args.question:
        answer(" ".join(args.question), args.n_results, args.theme, args.doc_type, show_sources)
        return

    print(f"Logging guidelines chat ({config.OLLAMA_MODEL}). Empty line to quit.\n")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            break
        answer(question, args.n_results, args.theme, args.doc_type, show_sources)
        print()


if __name__ == "__main__":
    main()
