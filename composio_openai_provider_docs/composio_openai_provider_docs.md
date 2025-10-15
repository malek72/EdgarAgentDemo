# OpenAI Providers

The OpenAI Provider is the default provider for the Composio SDK. It transforms Composio tools into a format compatible with OpenAI's function calling capabilities through both the Responses and Chat Completion APIs.

## Setup

By default, the OpenAI Provider is installed when you install the Composio SDK. You can also install it manually:

<CodeGroup>
  ```bash title="Python" for="python"
  pip install composio_openai
  ```

  ```bash title="TypeScript" for="typescript"
  npm install @composio/openai
  ```
</CodeGroup>

## Responses API

The Responses API is the recommended way to build more agentic flows with the OpenAI API.
Read more about it in the [OpenAI documentation](https://platform.openai.com/docs/api-reference/responses)

<Note>
  Before executing any tools that require authentication (like Gmail), you'll need to:

  1. [Create an Auth Configuration](/docs/authenticating-tools#creating-an-auth-config) for your integration
  2. [Set up a Connected Account](/docs/authenticating-tools#connecting-an-account) for the user.
</Note>

<CodeGroup>
  ```python Python title="Python" maxLines=40 
  from openai import OpenAI
  from composio import Composio
  from composio_openai import OpenAIResponsesProvider

  # Initialize Composio client with OpenAI Provider
  composio = Composio(provider=OpenAIResponsesProvider())
  openai = OpenAI()

  # Make sure to create an auth config and a connected account for the user with gmail toolkit
  # Make sure to replace "your-user-id" with the actual user ID
  user_id = "your-user-id"

  tools = composio.tools.get(user_id=user_id, toolkits=["GMAIL"], limit = 100)

  response = openai.responses.create(
      model="gpt-5",
      tools=tools,
      input=[
          {
              "role": "user",
              "content": "Send an email to soham.g@composio.dev with the subject 'Running OpenAI Provider snippet' and body 'Hello from the code snippet in openai docs'"
          }
      ]
  )

  # Execute the function calls
  result = composio.provider.handle_tool_calls(response=response, user_id=user_id)
  print(result)

  ```

  ```typescript TypeScript title="TypeScript" maxLines=40 
  import OpenAI from 'openai';
  import { Composio } from '@composio/core';
  import { OpenAIResponsesProvider } from '@composio/openai';

  // Initialize Composio client with OpenAI Provider
  const composio = new Composio({ 
      provider: new OpenAIResponsesProvider(), 
  });
  const openai = new OpenAI({});

  // Make sure to create an auth config and a connected account for the user with gmail toolkit
  // Make sure to replace "your-user-id" with the actual user ID
  const userId = "your-user-id";

  async function main() {
      try {
          const tools = await composio.tools.get(userId, {tools: ["GMAIL_SEND_EMAIL"]});

          const response = await openai.responses.create({
              model: "gpt-5",
              tools: tools,
              input: [
                  {
                      role: "user", 
                      content: "Send an email to soham.g@composio.dev with the subject 'Running OpenAI Provider snippet' and body 'Hello from the code snippet in openai docs'"
                  },
              ],
          });

          // Execute the function calls
          const result = await composio.provider.handleToolCalls(userId, response.output);
          console.log(result);
      } catch (error) {
          console.error('Error:', error);
      }
  }

  main();
  ```
</CodeGroup>

## Chat Completion API

The Chat Completion API generates a model response from a list of messages. Read more about it in the [OpenAI documentation](https://platform.openai.com/docs/api-reference/chat).
The OpenAI Chat Provider is the default provider used by Composio SDK, but you can also explicitly initialise it.

<Note>
  Before executing any tools that require authentication (like Gmail), you'll need to:

  1. [Create an Auth Configuration](/docs/authenticating-tools#creating-an-auth-config) for your integration
  2. [Set up a Connected Account](/docs/authenticating-tools#connecting-an-account) for the user.
</Note>

<CodeGroup>
  ```python Python title="Python" maxLines=40 
  from openai import OpenAI
  from composio import Composio
  from composio_openai import OpenAIProvider

  # Initialize Composio client with OpenAI Provider
  composio = Composio(provider=OpenAIProvider())
  openai = OpenAI()

  # Make sure to create an auth config and a connected account for the user with gmail toolkit
  # Make sure to replace "your-user-id" with the actual user ID
  user_id = "your-user-id"

  tools = composio.tools.get(user_id=user_id, toolkits=["GMAIL"], limit = 100))

  response = openai.chat.completions.create(
      model="gpt-5",
      tools=tools,
      messages=[
          {"role": "user", "content": "Send an email to soham.g@composio.dev with the subject 'Running OpenAI Provider snippet' and body 'Hello from the code snippet in openai docs'"},
      ],
  )

  # Execute the function calls
  result = composio.provider.handle_tool_calls(response=response, user_id=user_id)
  print(result)
  ```

  ```typescript TypeScript title="TypeScript" maxLines=40 
  import OpenAI from 'openai';
  import { Composio } from '@composio/core';
  import { OpenAIProvider } from '@composio/openai';

  // Initialize Composio client with OpenAI Provider
  const composio = new Composio({ 
      provider: new OpenAIProvider(), 
  });

  const openai = new OpenAI();

  // Make sure to create an auth config and a connected account for the user with gmail toolkit
  // Make sure to replace "your-user-id" with the actual user ID
  const userId = "your-user-id";

  async function main() {
      try {
          const tools = await composio.tools.get(userId, {tools: ["GMAIL_SEND_EMAIL"]});

          const response = await openai.chat.completions.create({
              model: "gpt-5",
              tools: tools,
              messages: [
                  {
                      role: "user", 
                      content: "Send an email to soham.g@composio.dev with the subject 'Running OpenAI Provider snippet' and body 'Hello from the code snippet in openai docs'"
                  },
              ],
          });

          // Execute the function calls
          const result = await composio.provider.handleToolCalls(userId, response);
          console.log(result);
      } catch (error) {
          console.error('Error:', error);
      }
  }

  main();

  ```
</CodeGroup>

## Modifiers

Modifiers are functions that can be used to intercept and optionally **modify** the schema, the tool call request and the response from the tool call.

OpenAI provider modifiers are the standard framework modifiers.
Read more here: [Modifying tool schemas](/docs/modifying-tool-schemas)