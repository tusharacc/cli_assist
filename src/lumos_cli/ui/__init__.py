"""
User interface components for Lumos CLI
"""

from .console import console, create_header, create_welcome_panel
from .footer import show_footer, show_status_footer, show_quick_reference
from .panels import create_command_help_panel, create_status_panel, create_config_panel
from .input_prompt import display_claude_style_prompt, show_intent_shortcuts, get_user_input_with_shortcuts

__all__ = [
    'console',
    'create_header',
    'create_welcome_panel',
    'show_footer',
    'show_status_footer', 
    'show_quick_reference',
    'create_command_help_panel',
    'create_status_panel',
    'create_config_panel',
    'display_claude_style_prompt',
    'show_intent_shortcuts',
    'get_user_input_with_shortcuts'
]
