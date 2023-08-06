from .mdforest import *
from .tree.types import *

def treeify(name:str="[document]", md:str="", *args, **kwargs) -> MarkdownForest:
    """
    Converts markdown file to a Python object (MarkdownForest).
    """
    
    return mdtreeify(name, md, *args, **kwargs)

def markdownify(tree:MarkdownForest, *args, **kwargs) -> str:
    """
    Converts Python object (MarkdownForest) to markdown file.
    """
    
    return mdtextify(tree, *args, **kwargs)

def clean_markdown(md:str) -> str:
    """
    Cleans markdown file of bold and italics formatting.
    """
    
    # Remove the metadata
    _, markdown_text = find_metadata(md)
    
    # Remove links
    markdown_text = re.sub(r'!\[(.*?)\]\((.*?)\)', '', markdown_text)
    markdown_text = re.sub(r'\[(.*?)\]\((.*?)\)', '', markdown_text)
    
    # Remove bold and italics formatting
    markdown_text = re.sub(r'\*\*(.*?)\*\*', r'\1', markdown_text)
    markdown_text = re.sub(r'__(.*?)__', r'\1', markdown_text)
    markdown_text = re.sub(r'\*(.*?)\*', r'\1', markdown_text)
    markdown_text = re.sub(r'_(.*?)_', r'\1', markdown_text)
    
    return markdown_text
    
