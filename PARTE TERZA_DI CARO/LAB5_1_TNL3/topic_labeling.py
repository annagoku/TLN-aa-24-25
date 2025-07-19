from rich import print
import torch


def label_all_topics(topic_model, pipe, num_keywords=10, num_docs=3):
    results = []

    for topic_id in topic_model.get_topics():
        if topic_id == -1:
            continue

        topic_keywords = topic_model.get_topic(topic_id)[:num_keywords]
        keywords = [kw for kw, _ in topic_keywords]
        topic_docs = topic_model.get_representative_docs()[topic_id][:num_docs]

        print(f"\n[Topic {topic_id}]")
        print(f"🔑 Keywords: {', '.join(keywords)}\n")

        print("📄 Representative abstracts:")
        for i, doc in enumerate(topic_docs):
            print(f"{i+1}. {doc[:200]}...")

        final_label = None

        while True:
            prompt = input(
                "\n📝 Enter a custom prompt to generate the label (or type 'exit' to quit):\n> "
            ).strip()

            if prompt.lower() == "exit":
                return results

            if not prompt:
                print("⚠️ Invalid prompt. Please try again.")
                continue

            full_prompt = f"{prompt} Keywords: {', '.join(keywords)}"
            messages = [{"role": "user", "content": full_prompt}]

            print(f"\n📨 Final prompt:\n{full_prompt}")
            print("⏳ Generating label...")

            try:
                output = pipe(messages)

                # Gestione robusta del formato dell'output
                if isinstance(output[0]["generated_text"], str):
                    full_text = output[0]["generated_text"]
                elif isinstance(output[0]["generated_text"], list):
                    # Se è una lista di messaggi (es. con 'role'/'content')
                    full_text = output[0]["generated_text"][0].get("content", "")
                else:
                    raise ValueError("Unexpected output format from pipeline.")

                # Rimozione del prompt iniziale (se incluso nella risposta)
                if full_text.startswith(full_prompt):
                    label = full_text[len(full_prompt):].strip()
                else:
                    label = full_text.strip()

                print(f"\n🏷️ Generated label: {label}")

                satisfied = input("✅ Are you satisfied with this label? (y/n): ").strip().lower()
                if satisfied == "y":
                    final_label = label
                    break
                else:
                    print("🔁 Try again with a new prompt.")

            except Exception as e:
                print(f"❌ Error during generation: {e}")

        results.append({
            "topic_id": topic_id,
            "keywords": keywords,
            "label": final_label
        })

    return results
