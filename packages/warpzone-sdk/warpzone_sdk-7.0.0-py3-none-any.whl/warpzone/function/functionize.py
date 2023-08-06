from typing import Callable

import typeguard

from warpzone.function import monitor, process, signature
from warpzone.function.processors import outputs, triggers
from warpzone.function.types import SingleArgumentCallable


def functionize(
    f: SingleArgumentCallable,
    trigger: triggers.TriggerProcessor,
    output: outputs.OutputProcessor,
) -> Callable:
    """Wrap function as an Azure function.

    Args:
        f (SingleArgumentCallable): Function with
            - argument of type specified in trigger processor
            - return value of type specified in output processor
        trigger (triggers.TriggerProcessor): Trigger processor
        output (outputs.OutputProcessor): Output processor

    Returns:
        Callable: Azure function with
            - argument
                name: "<trigger.binding_name>"
                annotation: "<trigger.arg_type>"
                description: pre-argument of the original function
            - argument
                name: "context"
                annotation: "azure.functions.Context"
                description: Azure function context
            - return value
                annotation: "<output.return_type>"
                description: post-return value of the original function
    """
    typeguard.check_type(f, SingleArgumentCallable)

    main = process.pre_and_post_process(f, trigger, output)

    main = monitor.monitor(main)
    main = signature.redefine_signature(main, trigger, output)
    return main
