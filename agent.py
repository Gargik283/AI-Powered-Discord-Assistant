import os
import io
import re
import urllib.parse

import discord
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool
from tavily import TavilyClient
from groq import Groq


# ============================================================
# API KEYS
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")


# ============================================================
# TAVILY
# ============================================================

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


@tool
def surfInternet(query: str):
    """Use this tool to surf the Internet and get the latest information."""
    result = tavily_client.search(query=query)
    return str(result)


# ============================================================
# IMAGE GENERATION
# ============================================================

async def rawGenerateAndSendImage(
    prompt: str,
    discord_message: discord.Message
):
    """Generate an image and send it directly to Discord."""

    import aiohttp

    if discord_message is None:
        return "Error: Could not access Discord message context."

    if not POLLINATIONS_API_KEY:
        return (
            "Error: POLLINATIONS_API_KEY is missing from the .env file."
        )

    try:

        # ----------------------------------------------------
        # CLEAN PROMPT
        # ----------------------------------------------------

        cleaned_prompt = prompt.strip(
            "[]()\"' "
        )

        if not cleaned_prompt:
            return (
                "Error: The image generation prompt was empty."
            )

        # ----------------------------------------------------
        # ENCODE PROMPT
        # ----------------------------------------------------

        encoded_prompt = urllib.parse.quote(
            cleaned_prompt,
            safe=""
        )

        # ----------------------------------------------------
        # POLLINATIONS IMAGE URL
        # ----------------------------------------------------

        image_url = (
            f"https://gen.pollinations.ai/image/"
            f"{encoded_prompt}"
            f"?model=flux"
            f"&width=1024"
            f"&height=1024"
            f"&nologo=true"
        )

        # ----------------------------------------------------
        # AUTHENTICATION
        # ----------------------------------------------------

        headers = {
            "Authorization": (
                f"Bearer {POLLINATIONS_API_KEY}"
            )
        }

        # ----------------------------------------------------
        # REQUEST IMAGE
        # ----------------------------------------------------

        timeout = aiohttp.ClientTimeout(
            total=180
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                image_url,
                headers=headers
            ) as response:

                # ------------------------------------------------
                # AUTH ERROR
                # ------------------------------------------------

                if response.status == 401:

                    return (
                        "Image generation failed: "
                        "Pollinations API key is missing or invalid. "
                        "Check POLLINATIONS_API_KEY in your .env file."
                    )

                # ------------------------------------------------
                # PAYMENT/BALANCE ERROR
                # ------------------------------------------------

                if response.status == 402:

                    return (
                        "Image generation failed: "
                        "Pollinations accepted the API key, "
                        "but the account/key does not have enough "
                        "available image-generation budget."
                    )

                # ------------------------------------------------
                # OTHER HTTP ERROR
                # ------------------------------------------------

                if response.status != 200:

                    error_text = await response.text()

                    return (
                        f"Failed to generate image. "
                        f"HTTP Status: {response.status}\n"
                        f"{error_text[:500]}"
                    )

                # ------------------------------------------------
                # CHECK CONTENT TYPE
                # ------------------------------------------------

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                ).lower()

                if not content_type.startswith("image/"):

                    response_text = await response.text()

                    return (
                        "Image generation service returned "
                        "something other than an image.\n"
                        f"Content-Type: {content_type}\n"
                        f"Response: {response_text[:500]}"
                    )

                # ------------------------------------------------
                # READ IMAGE
                # ------------------------------------------------

                image_data = await response.read()

                if not image_data:

                    return (
                        "Image generation returned an empty image."
                    )

                image_bytes = io.BytesIO(
                    image_data
                )

                image_bytes.seek(0)

                # ------------------------------------------------
                # SEND TO DISCORD
                # ------------------------------------------------

                discord_file = discord.File(
                    fp=image_bytes,
                    filename="generated_image.png"
                )

                await discord_message.channel.send(
                    file=discord_file
                )

                return (
                    "Image successfully generated "
                    "and sent to the channel."
                )

    except aiohttp.ClientError as e:

        return (
            f"Image generation network error: {str(e)}"
        )

    except Exception as e:

        return (
            f"Failed to generate image due to error: {str(e)}"
        )


# ============================================================
# GROQ CLIENT
# ============================================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# GROQ AGENT
# ============================================================

class PureNativeGroqAgent:

    def __init__(
        self,
        client,
        text_tools
    ):

        self.client = client

        self.text_tools = {
            tool.name: tool
            for tool in text_tools
        }

        # Store the latest Discord message here.
        # This avoids depending completely on LangChain config.
        self.discord_message = None

    # ========================================================
    # INVOKE
    # ========================================================

    async def ainvoke(
        self,
        input_data: dict,
        config: dict = None,
        discord_message=None,
        **kwargs
    ):

        # ----------------------------------------------------
        # DISCORD MESSAGE
        # ----------------------------------------------------

        if discord_message is not None:
            self.discord_message = discord_message

        # ----------------------------------------------------
        # EXTRACT USER MESSAGE
        # ----------------------------------------------------

        user_msg_list = input_data.get(
            "messages",
            []
        )

        user_message = ""

        if isinstance(
            user_msg_list,
            list
        ) and user_msg_list:

            last_msg = user_msg_list[-1]

            # Tuple:
            # ("user", "hello")
            if isinstance(
                last_msg,
                tuple
            ):

                if len(last_msg) >= 2:

                    user_message = str(
                        last_msg[1]
                    )

                else:

                    user_message = str(
                        last_msg[0]
                    )

            # Dictionary
            elif isinstance(
                last_msg,
                dict
            ):

                user_message = str(
                    last_msg.get(
                        "content",
                        ""
                    )
                )

            # LangChain message
            elif hasattr(
                last_msg,
                "content"
            ):

                user_message = str(
                    last_msg.content
                )

            else:

                user_message = str(
                    last_msg
                )

        else:

            user_message = str(
                user_msg_list
            )

        # ----------------------------------------------------
        # GROQ REQUEST
        # ----------------------------------------------------

        try:

            chat_completion = (
                self.client
                .chat
                .completions
                .create(
                    model="openai/gpt-oss-120b",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful Discord assistant.\n\n"

                                "IMAGE REQUESTS:\n"
                                "If the user asks for a picture, "
                                "drawing, image, illustration, "
                                "artwork, photo, or anything visual, "
                                "you MUST generate an image tool call.\n\n"

                                "Create a detailed image prompt. "
                                "Include the subject, appearance, "
                                "colors, lighting, composition, "
                                "background, textures, perspective, "
                                "and visual quality.\n\n"

                                "Then respond ONLY using:\n"
                                "USE_TOOL: generateAndSendImage "
                                "[detailed image prompt]\n\n"

                                "INTERNET REQUESTS:\n"
                                "If the user asks for current "
                                "information, recent information, "
                                "news, or asks to search the Internet, "
                                "respond ONLY using:\n"
                                "USE_TOOL: surfInternet "
                                "[search query]\n\n"

                                "NORMAL REQUESTS:\n"
                                "For everything else, respond normally."
                            )
                        },

                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],

                    temperature=0.7
                )
            )

            # IMPORTANT:
            # choices is a list.
            ai_response = (
                chat_completion
                .choices[0]
                .message
                .content
                .strip()
            )

        except Exception as e:

            return {
                "messages": [
                    {
                        "content": (
                            f"AI Generation failed: {str(e)}"
                        )
                    }
                ]
            }

        # ====================================================
        # TOOL DETECTION
        # ====================================================

        if "USE_TOOL:" in ai_response:

            try:

                match = re.search(
                    r"USE_TOOL:\s*(\w+)\s+(.*)",
                    ai_response,
                    re.DOTALL
                )

                if match:

                    tool_name = (
                        match
                        .group(1)
                        .strip()
                    )

                    tool_arg = (
                        match
                        .group(2)
                        .strip()
                    )

                else:

                    tool_part = (
                        ai_response
                        .split(
                            "USE_TOOL:",
                            1
                        )[1]
                        .strip()
                    )

                    if " " in tool_part:

                        tool_name, tool_arg = (
                            tool_part.split(
                                " ",
                                1
                            )
                        )

                    else:

                        tool_name = tool_part
                        tool_arg = ""

                # Remove surrounding brackets
                tool_arg = tool_arg.strip(
                    "[]()\"' "
                )

                # =================================================
                # IMAGE TOOL
                # =================================================

                if tool_name == (
                    "generateAndSendImage"
                ):

                    if self.discord_message is None:

                        return {
                            "messages": [
                                {
                                    "content": (
                                        "Error: Could not access "
                                        "Discord message context."
                                    )
                                }
                            ]
                        }

                    tool_result = (
                        await rawGenerateAndSendImage(
                            tool_arg,
                            self.discord_message
                        )
                    )

                    return {
                        "messages": [
                            {
                                "content": tool_result
                            }
                        ]
                    }

                # =================================================
                # INTERNET SEARCH
                # =================================================

                elif tool_name in self.text_tools:

                    target_tool = (
                        self.text_tools[
                            tool_name
                        ]
                    )

                    tool_result = (
                        target_tool.invoke(
                            {
                                "query": tool_arg
                            }
                        )
                    )

                    final_completion = (
                        self.client
                        .chat
                        .completions
                        .create(
                            model="openai/gpt-oss-120b",

                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Summarize the search data "
                                        "clearly and accurately. "
                                        "Answer the original question "
                                        "using the search data."
                                    )
                                },

                                {
                                    "role": "user",
                                    "content": (
                                        f"Search Data:\n"
                                        f"{tool_result}\n\n"
                                        f"Original Question:\n"
                                        f"{user_message}"
                                    )
                                }
                            ],

                            temperature=0.3
                        )
                    )

                    return {
                        "messages": [
                            {
                                "content": (
                                    final_completion
                                    .choices[0]
                                    .message
                                    .content
                                    .strip()
                                )
                            }
                        ]
                    }

            except Exception as tool_err:

                return {
                    "messages": [
                        {
                            "content": (
                                "Tool execution processing "
                                f"failed: {str(tool_err)}"
                            )
                        }
                    ]
                }

        # ====================================================
        # NORMAL RESPONSE
        # ====================================================

        return {
            "messages": [
                {
                    "content": ai_response
                }
            ]
        }


# ============================================================
# CREATE AGENT
# ============================================================

agent = PureNativeGroqAgent(
    client=groq_client,
    text_tools=[
        surfInternet
    ]
)