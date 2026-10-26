from agent import ESP32Agent
from llm_client import MODEL


def main():
   agent = ESP32Agent()

   print("ESP32 AI Agent uruchomiony!")
   print(f"Model: {MODEL}")
   print("Wpisz exit, aby zakończyć.\n")

   while True:
       try:
           text = input("Ty: ").strip()

           if text.lower() in {"exit", "quit"}:
               break

           if not text:
               continue

           answer = agent.chat(text)
           print(f"\nAgent: {answer}\n")

       except KeyboardInterrupt:
           print("\nZakończono.")
           break

       except Exception as exc:
           print(f"\nBłąd: {exc}\n")


if __name__ == "__main__":
   main()
