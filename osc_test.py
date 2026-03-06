import os
import sys
import base64


def osc52_copy(text: str):
    """
    Attempts to copy text to the local system clipboard using OSC 52.
    Handles wrapping for terminal multiplexers like tmux and screen.
    """
    # 1. Base64 encode the payload (required by the OSC 52 protocol)
    b64_payload = base64.b64encode(text.encode("utf-8")).decode("ascii")

    # 2. Standard OSC 52 sequence: ESC ] 52 ; c ; <payload> BEL
    # \x1b is ESC, \x07 is BEL (the standard terminator)
    osc_seq = f"\x1b]52;c;{b64_payload}\x07"

    # 3. Handle Multiplexers (tmux/screen)
    # Multiplexers often 'swallow' escape codes unless they are wrapped
    # in a special pass-through sequence.
    term = os.environ.get("TERM", "").lower()

    if "TMUX" in os.environ:
        # tmux wrap: ESC P tmux ; ESC <sequence> ESC \
        final_seq = f"\x1bPtmux;\x1b{osc_seq}\x1b\\"
        print("Detected: tmux (using pass-through wrapping)")
    elif term.startswith("screen"):
        # GNU Screen wrap: ESC P <sequence> ESC \
        final_seq = f"\x1bP{osc_seq}\x1b\\"
        print("Detected: GNU Screen (using pass-through wrapping)")
    else:
        # Standard terminal
        final_seq = osc_seq
        print(f"Detected: Standard Terminal (TERM={term})")

    # 4. Write directly to stdout and flush immediately
    sys.stdout.write(final_seq)
    sys.stdout.flush()


if __name__ == "__main__":
    test_string = (
        "Hello from OSC 52! (Copied at " + os.popen("date").read().strip() + ")"
    )

    print("-" * 50)
    print("OSC 52 Clipboard Test Script")
    print("-" * 50)
    print(f"Attempting to copy: '{test_string}'")

    osc52_copy(test_string)

    print("\n" + "=" * 50)
    print("FINISHED: The escape sequence has been sent to your terminal.")
    print("=" * 50)
    print("HOW TO VERIFY:")
    print(
        "1. Switch to a DIFFERENT application (e.g., your browser, Notes, or a text editor)."
    )
    print("2. Use your standard 'Paste' command (Cmd+V or Ctrl+V).")
    print("-" * 50)
    print(
        "NOTE: If it doesn't work, your terminal emulator (e.g., iTerm2, Kitty, Windows Terminal)"
    )
    print("might have 'Allow OSC 52' disabled in its settings.")
    print("-" * 50)
