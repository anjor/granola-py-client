"""
Utility functions for granola-client.
"""

from typing import Dict, Any


def convert_prosemirror_to_markdown(prosemirror_json: Dict[str, Any]) -> str:
    """
    Convert ProseMirror JSON to Markdown format.
    This is based on reverse-engineering the Granola format.

    Args:
        prosemirror_json: The ProseMirror document JSON structure

    Returns:
        str: Markdown representation of the document
    """

    def process_node(node: Dict[str, Any], depth: int = 0) -> str:
        node_type = node.get("type", "")
        content = node.get("content", [])
        text = node.get("text", "")
        marks = node.get("marks", [])
        attrs = node.get("attrs", {})

        # Handle text nodes with marks
        if node_type == "text" or text:
            formatted_text = text
            for mark in marks:
                mark_type = mark.get("type", "")
                if mark_type == "bold":
                    formatted_text = f"**{formatted_text}**"
                elif mark_type == "italic":
                    formatted_text = f"*{formatted_text}*"
                elif mark_type == "code":
                    formatted_text = f"`{formatted_text}`"
                elif mark_type == "strike":
                    formatted_text = f"~~{formatted_text}~~"
                elif mark_type == "link":
                    href = mark.get("attrs", {}).get("href", "")
                    formatted_text = f"[{formatted_text}]({href})"
            return formatted_text

        # Handle different node types
        result = []

        if node_type == "doc":
            # Process all child nodes
            for child in content:
                result.append(process_node(child, depth))

        elif node_type == "paragraph":
            # Join text content and add double newline
            para_content = "".join(process_node(child, depth) for child in content)
            if para_content:  # Only add non-empty paragraphs
                result.append(para_content + "\n")

        elif node_type == "heading":
            level = attrs.get("level", 1)
            heading_text = "".join(process_node(child, depth) for child in content)
            result.append("#" * level + " " + heading_text + "\n")

        elif node_type == "bulletList":
            for item in content:
                result.append(process_node(item, depth))

        elif node_type == "orderedList":
            for i, item in enumerate(content, 1):
                # Pass the order number in attrs for listItem to use
                item_attrs = item.get("attrs", {})
                item_attrs["order"] = i
                item["attrs"] = item_attrs
                result.append(process_node(item, depth))

        elif node_type == "listItem":
            # Process list item content
            item_content = []
            for child in content:
                item_content.append(process_node(child, depth + 1))

            # Format based on parent list type (detect by order attr)
            order = attrs.get("order")
            if order:
                prefix = f"{order}. "
            else:
                prefix = "- "

            # Add proper indentation
            indent = "  " * depth
            formatted_content = "".join(item_content).strip()
            result.append(indent + prefix + formatted_content + "\n")

        elif node_type == "codeBlock":
            language = attrs.get("language", "")
            code_content = "".join(process_node(child, depth) for child in content)
            result.append(f"```{language}\n{code_content}\n```\n")

        elif node_type == "blockquote":
            quote_content = "".join(process_node(child, depth) for child in content)
            # Add > prefix to each line
            quoted_lines = ["> " + line for line in quote_content.strip().split("\n")]
            result.append("\n".join(quoted_lines) + "\n")

        elif node_type == "horizontalRule":
            result.append("---\n")

        elif node_type == "hardBreak":
            result.append("  \n")  # Markdown hard break

        else:
            # For unknown types, just process children
            for child in content:
                result.append(process_node(child, depth))

        return "".join(result)

    # Start processing from the root
    return process_node(prosemirror_json).strip()
