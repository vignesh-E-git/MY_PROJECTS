from openai import OpenAI
client = OpenAI()
print(".... welcome to simple chatbot ... ")
print("rules : ")
print("1. it cant remember past")
print('2. exit to end chat')
print("start chating :) ")

user_input = input("")
while user_input != "exit":
    response = client.responses.create(
        model = "gpt-5-nano",
        input = user_input ,
        store = True
    )
    print(response.output_text)
    user_input = input("")
