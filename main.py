import openai
import json

GPT_MODEL = "gpt-3.5-turbo-0125"  # $0.5/1 Million Tokens
# GPT_MODEL = "gpt-4o" # $5/1 Million Tokens


class Context:
    def __init__(self, context_file):
        self.contexts = {}
        with open(context_file, "r") as f:
            self.contexts = json.load(f)

    def get_relevant_context(self, user_input):
        for keyword in self.contexts:
            if keyword in user_input.lower():
                return self.contexts[keyword]
        return ""


class GPT_Narrator:
    def __init__(self, context):
        self.context = context

    def modify_system_message(
        self, base_context, assistant_response, additional_context
    ):
        modification_prompt = f"""
        The current system message for an RPG game is as follows:
        ---
        System message: '{base_context}'
        ---
        The game's output indicates a potential change in the setting. Here is the new setting:
        ---
        Previous output: '{assistant_response}'
        ---
        Incorporate the new setting into the system message. If any context needs to be updated
        (e.g., location changes, new items, or interactions), adjust the system message accordingly.
        Remove any outdated or irrelevant information. Do not include actions for the user to take.
        Here is the additional context to include in the story:
        ---
        Additional Context: '{additional_context}'
        ---
        Provide the updated system message incorporating all necessary changes:
        """

        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
                You are an assistant that modifies context.
                Update the system message based on the new game output and additional context. Ensure all changes are accurately reflected.
                Allow room for the story to develop, add interesting and humorous details to the setting.
                Keep track of the user's inventory.
                """,
                },
                {"role": "user", "content": modification_prompt},
            ],
            stream=False,
        )

        modified_system_message = response.choices[0].message.content
        return modified_system_message

    def stream_response(self, *messages):
        messages_list = (
            list(messages[0]) if isinstance(messages[0], list) else list(messages)
        )
        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=messages_list,
            stream=True,
        )

        concat_response = ""
        for chunk in response:
            content = chunk.choices[0].delta.content
            content = content if content else ""
            print(content, end="")
            concat_response += content

        return concat_response

    def game_loop(self):
        base_context = """
        This is a game. You are an role playing game master. You present the user with an update to the
        story, their current surroundings, and a list of actions they can take.
        In the style of the old text-based games like "Zork".
        If an action is not valid, say "I don't understand that" or "You can't go that way" or "I don't see that here".
        When the user talks to someone, they must speak. Do not speak on their behalf.
        Here is the setting: The user starts in a bustling city center. They are seated outside at a cafe. The sun shines brightly, a crisp, clear day.
        They have no money on them, but they do have a pocket knife and a croissant.
        """

        initial_message = [{"role": "system", "content": base_context}]
        assistant_response = self.stream_response(initial_message)

        current_context = base_context
        message_history = initial_message
        message_history.append({"role": "assistant", "content": assistant_response})

        while True:
            user_input = input("\n> ")

            additional_context = self.context.get_relevant_context(user_input)

            current_context = self.modify_system_message(
                current_context, assistant_response, additional_context
            )
            system_message = {"role": "system", "content": current_context}
            user_message = {"role": "user", "content": user_input}

            assistant_response = self.stream_response(system_message, user_message)

            message_history.append(system_message)
            message_history.append(user_message)
            message_history.append({"role": "assistant", "content": assistant_response})

            with open("history.txt", "a") as file:
                for message in message_history:
                    file.write(str(message) + "\n")

            message_history = []


if __name__ == "__main__":
    cntx = Context("out_of_earth_context.json")
    obj = GPT_Narrator(cntx)
    obj.game_loop()
