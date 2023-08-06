def inject_func_as_unbound_method(class_, func, method_name=None):
         #   This is actually quite simple
        if method_name is None:
            method_name = get_funcname(func)
        setattr(class_, method_name, func)

def e(message, exit_code=None):
    # Print an error log message.
    print_log(message, YELLOW, BOLD)
    if exit_code is not None:
        sys.exit(exit_code)