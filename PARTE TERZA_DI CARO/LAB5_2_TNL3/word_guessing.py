from rich import print
import torch


def interactive_guessing(def_dict, pipe, max_per_concept=5):
    from itertools import islice

    results = []
    conversation = []
    interaction_log = {}  # ⬅️ Log delle interazioni

    for concept, definitions in def_dict.items():
        print(f"\n🎯 Target concept: {concept}")
        clean_defs = [d.strip() for d in definitions if d.strip()]
        defs_to_try = list(islice(clean_defs, max_per_concept))
        def_index = 0
        last_guess = None
        interaction_log[concept] = []

        while def_index < len(defs_to_try):
            definition = defs_to_try[def_index]
            print(f"\n📄 Definition {def_index+1} of {len(defs_to_try)}:\n\"{definition}\"")

            if def_index == 0:
                print("📌 This definition will be automatically concatenated to your prompt.")
                use_definition = "y"
            else:
                use_definition = input(
                    "🔧 Do you want to concatenate the definition to your prompt? (y/n): "
                ).strip().lower()
                if use_definition not in ("y", "n"):
                    print("⚠️ Invalid input, defaulting to 'y'")
                    use_definition = "y"

            user_prompt = input("📝 Write your prompt (or type 'exit' to quit):\n> ").strip()
            if user_prompt.lower() == "exit":
                print("👋 Exiting.")
                return results, interaction_log

            full_prompt = f"{user_prompt}\nDefinition: {definition}" if use_definition == "y" else user_prompt
            conversation.append({"role": "user", "content": full_prompt})

            print("\n🤖 Model is guessing...")
            try:
                output = pipe(conversation)

                if isinstance(output[0]["generated_text"], str):
                    guess = output[0]["generated_text"].strip()
                else:
                    assistant_msgs = [
                        m.get("content", "") for m in output[0]["generated_text"]
                        if m.get("role") == "assistant"
                    ]
                    guess = assistant_msgs[-1].strip() if assistant_msgs else ""

                last_guess = guess
                print(f"\n🔍 Model guessed: {guess}")
                conversation.append({"role": "assistant", "content": guess})

                satisfied = input("✅ Are you satisfied with this answer? (y/n): ").strip().lower()
                action_taken = "end" if satisfied == "y" else ""

                if satisfied == "y":
                    final_label = guess
                    interaction_log[concept].append({
                        "definition": definition,
                        "prompt": full_prompt,
                        "model_guess": guess,
                        "satisfied": True,
                        "action": "end"
                    })
                    break  # passa al prossimo concetto
                else:
                    next_action = input(
                        "\n🔁 What do you want to do next?\n"
                        " - Type 'nextdef' to try with another definition\n"
                        " - Type 'prompt' to rewrite the prompt for the SAME definition\n> "
                    ).strip().lower()

                    if next_action not in ("nextdef", "prompt"):
                        print("⚠️ Invalid input. Moving to next definition.")
                        next_action = "nextdef"

                    interaction_log[concept].append({
                        "definition": definition,
                        "prompt": full_prompt,
                        "model_guess": guess,
                        "satisfied": False,
                        "action": next_action
                    })

                    if next_action == "nextdef":
                        def_index += 1
                    elif next_action == "prompt":
                        continue

            except Exception as e:
                print(f"❌ Error during generation: {e}")
                interaction_log[concept].append({
                    "definition": definition,
                    "prompt": full_prompt,
                    "model_guess": "ERROR",
                    "satisfied": False,
                    "action": "error"
                })
                def_index += 1

        results.append({
            "definition": definition,
            "true_label": concept,
            "predicted_label": last_guess,
            "final_label": last_guess,
            "user_prompt": full_prompt
        })

    return results, interaction_log



