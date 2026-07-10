from browser_use import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os

class WrappedChatOpenAI:
    def __init__(self, model_name, api_key):
        self._llm = ChatOpenAI(model=model_name, api_key=api_key)
        self.provider = "openai"  # This is what browser-use was looking for

    def __getattr__(self, name):
        return getattr(self._llm, name)

    async def ainvoke(self, *args, **kwargs):
        return await self._llm.ainvoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        return self._llm.invoke(*args, **kwargs)

async def main():
    # Load environment variables from .env.browseruse or .env
    print("Loading environment variables...")
    load_dotenv("D:\\workspace\\my-trae-helper\\.env.browseruse")
    load_dotenv("D:\\workspace\\my-trae-helper\\.env")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"Found API Key: {api_key[:5]}...")
    else:
        print("No OPENAI_API_KEY found in environment.")
        return

    # Task description
    task = (
        "Go to https://civitai.com/user/LatentHeart/images. "
        "Scroll down to load several images. "
        "Download the first 3 images you see. "
        "For each image, save it to the current directory with names: image_1.jpg, image_2.jpg, image_3.jpg. "
        "Ensure the downloads are successful."
    )

    print(f"Starting task: {task}")
    
    # Use WrappedChatOpenAI to satisfy browser_use requirement
    llm = WrappedChatOpenAI(model_name="gpt-4o", api_key=api_key)

    agent = Agent(
        task=task,
        llm=llm,
    )

    try:
        history = await agent.run()
        print("Task completed successfully.")
        print("Final result:", history.final_result())
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
