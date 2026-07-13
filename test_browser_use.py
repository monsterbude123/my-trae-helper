from browser_use import Agent
from browser_use.beta import ChatBrowserUse
from dotenv import load_dotenv
import asyncio
import os

async def main():
    # Load environment variables
    load_dotenv("D:\\workspace\\my-trae-helper\\.env.browseruse")
    load_dotenv("D:\\workspace\\my-trae-helper\\.env")
    
    # Use ChatBrowserUse
    llm = ChatBrowserUse()

    agent = Agent(
        task="Go to https://civitai.com/user/LatentHeart/images and tell me the page title.",
        llm=llm,
    )

    print("Starting task...")
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
