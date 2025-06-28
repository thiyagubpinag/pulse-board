"""
PulseBoard AskManager - Modernized and Modularized
A team health and sprint management AI assistant
"""


# ==== Main Application ====

from create_interface import create_interface


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True,
    )