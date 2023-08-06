from typing import Any

from invoker_terminal import (
    InvokerNetworkFileInput,
    InvokerNetworkNumberInput,
    InvokerNetworkRangeInput,
    InvokerNetworkSelectInput,
    InvokerNetworkTextInput,
    InvokerOutput,
    invoker,
    invoker_input,
)


@invoker_input
class AsampleClass:
    count = InvokerNetworkNumberInput(
        description="count variable used in the model",
        required=True,
        minNum=100,
        maxNum=1000,
    )

    selectedValue = InvokerNetworkSelectInput(
        description="Important selections need to be done",
        required=True,
        options=["options1", "options2", "options3", "options4"],
    )

    count2 = InvokerNetworkNumberInput(
        description="another variable but required",
        required=True,
        minNum=100,
        maxNum=1000,
    )
    prompt = InvokerNetworkTextInput(
        description="my description here",
        required=True,
        minChar=10,
        maxChar=12,
        textarea=False,
    )
    prompt2 = InvokerNetworkTextInput(
        description="Prompt to execute in the model",
        required=True,
        textarea=True,
    )

    sliderval = InvokerNetworkRangeInput(
        description="Slider value", required=True, min=0, max=100, step=25
    )

    profilepicture = InvokerNetworkFileInput(
        description="Your profile picture", required=True
    )


@invoker(
    name="Web LLM",
    tags=["LLM", "15B Params", "4-bit Quantization"],
    description="This project brings language model chats directly onto web browsers. Everything runs inside the browser with no server support and accelerated with WebGPU. We can bring a lot of fun opportunities to build AI assistants for everyone and enable privacy while enjoying GPU acceleration.",
)
def invoke(input: AsampleClass):
    print("I got invoked")
    newCount = input.count * 200
    newPrompt = ""
    newPrompt += input.prompt
    newPrompt += input.prompt2
    InvokerOutput.addText("new count is {}".format(newCount))
    InvokerOutput.addText("new Prompt is {}".format(newPrompt))
    InvokerOutput.addText("my content is here", "5.txt")
