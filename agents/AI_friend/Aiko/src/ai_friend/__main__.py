from pathlib import Path

from ai_friend.bootstrap import build_runtime


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    runtime = build_runtime(project_root)
    print("Aiko ai-friend generic runtime")
    print('Type "exit" to quit.\n')
    while True:
        try:
            user_input = input("You > ")
        except EOFError:
            break
        if user_input.strip().lower() == "exit":
            break
        response = runtime.process_text(user_input)
        print(f"{runtime.character.profile().identity.name} > {response.content}\n")


if __name__ == "__main__":
    main()

