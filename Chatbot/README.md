This is a very basic chatbot with whiie loop and openAI api.

## step to build a chatbot
### step - 1
- Get api key from open ai.com
- Store the key somewhere safe better store as a environ *user variable* under the name : OPENAI_API_KEY
- Learn how to get the key whenever you want .
  
  ``` cmd
  echo %OPENAI_API_KEY%
  ```
### step -2 
- **Install** openai if not installed before . then import it.
  
  ```pip
  pip install openai
  ```
- **check** whether it is installed properly by running
  
  ```pip
  openai -V
  openai --version
  ```
