import asyncio

from warpzone.function.processors import outputs, triggers
from warpzone.function.types import SingleArgumentCallable


def pre_and_post_process(
    f: SingleArgumentCallable,
    trigger: triggers.TriggerProcessor,
    output: outputs.OutputProcessor,
) -> SingleArgumentCallable:
    """Wrap function as an Azure function with
    pre- and post processing. The wrapped function
    is the function composition

        output.process ∘ f ∘ trigger.process

    Args:
        f (SingleArgumentCallable): Function with
            - argument of type specified in trigger processor
            - return value of type specified in output processor
        trigger (triggers.TriggerProcessor): Trigger processor
        output (outputs.OutputProcessor): Output processor

    Returns:
        Callable: Azure function with
            - argument "arg":   pre-argument of the original function
            - return value:     post-return value of the original function
    """

    async def wrapper_async(arg):
        processed_arg = trigger._process(arg)
        result = await f(processed_arg)
        processed_result = output._process(result)
        return processed_result

    def wrapper(arg):
        processed_arg = trigger._process(arg)
        result = f(processed_arg)
        processed_result = output._process(result)
        return processed_result

    if asyncio.iscoroutinefunction(f):
        return wrapper_async
    else:
        return wrapper
