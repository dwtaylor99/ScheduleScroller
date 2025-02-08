import openai


# Set up the model and prompt
ENGINE_CHATGPT = "gpt-3.5-turbo"
ENGINE_CHATGPT_4 = "gpt-4"
ENGINE_DAVINCI = "davinci"
ENGINE_DAVINCI_003 = "text-davinci-003"
MODEL_ENGINE = ENGINE_CHATGPT

SYSTEM_PROMPT = """You are MovieVox, a chatbot on the streaming site Twitch.tv with extensive knowledge of the 
television and streaming show "Mystery Science Theater 3000". Please limit replies to 450 characters or fewer."""

is_api_key_set = False


def set_api_key():
    global is_api_key_set

    api_key = ""
    try:
        with open("data/openai_key.txt", "r") as f:
            api_key = f.readlines()[0]
            f.close()
    except FileNotFoundError as e:
        print(e)

    if api_key != "":
        openai.api_key = api_key
        is_api_key_set = True


def generate_response(prompt: str) -> str:
    if not is_api_key_set:
        set_api_key()

    response = ""
    if is_api_key_set:
        try:
            completion = openai.chat.completions.create(
                model=MODEL_ENGINE,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            response = completion.choices[0].message.content
            # for choice in completion.choices:
            #     response += choice.message.content
        except openai.RateLimitError as e:
            print(e)
    else:
        print("Could not set the API key. Check if the 'data/openai_key.txt' file exists.")

    return response


if __name__ == '__main__':
    print(generate_response("What is the Twitch channel?"))
