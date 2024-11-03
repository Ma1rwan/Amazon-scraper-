import datetime
from colorama import init, Fore, Style

init(autoreset=True)


class logger:
    def __init__(self, identifier='AMZN'):
        self.identifier = identifier

    def log(self, status, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if status == "error":
            formatted_status = f"{Fore.RED}ERROR{Style.RESET_ALL}"
        elif status == "success":
            formatted_status = f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}"
        elif status == "info":
            formatted_status = f"{Fore.BLUE}INFO{Style.RESET_ALL}"

        log_entry = (f"[{Fore.WHITE}{timestamp}{Style.RESET_ALL}] | "
                     f"{formatted_status} | {Fore.YELLOW}{self.identifier}{Style.RESET_ALL} | "
                     f"{Fore.WHITE}{message}{Style.RESET_ALL}")

        print(log_entry)


# Example usage
if __name__ == "__main__":
    log_instance = logger(identifier='AMZN')
    log_instance.log("success", "Page loaded successfully!")
