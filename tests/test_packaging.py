def test_package_importable():
    """Verify the package can be imported after installation."""
    import agents

    assert hasattr(agents, "__version__")
    assert agents.__version__ == "0.1.0"


def test_package_exports():
    """Verify expected exports are available and functional."""
    from agents import (
        TOOL_DEFINITIONS,
        ModelFormat,
        ToolDefinition,
        ToolParameter,
        detect_model_format,
        get_tool_by_name,
        get_tools_by_category,
        get_tools_by_permission,
        get_tools_for_model,
        render_anthropic_tools,
        render_ollama_tools,
        render_openai_tools,
        render_tools,
    )

    assert ModelFormat.OPENAI == "openai"
    assert ModelFormat.ANTHROPIC == "anthropic"
    assert ModelFormat.OLLAMA == "ollama"

    tool = ToolDefinition(name="test_tool", description="A test tool")
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"

    param = ToolParameter(
        name="arg", type="string", description="An argument", required=True
    )
    assert param.name == "arg"
    assert param.type == "string"
    assert param.required is True

    assert isinstance(TOOL_DEFINITIONS, list)

    fmt = detect_model_format("gpt-4")
    assert fmt == ModelFormat.OPENAI

    tool_def = ToolDefinition(name="my_tool", description="desc")
    result = get_tool_by_name("my_tool")
    assert result is None

    category_tools = get_tools_by_category("test")
    assert isinstance(category_tools, list)

    perm_tools = get_tools_by_permission("read")
    assert isinstance(perm_tools, list)

    model_tools = get_tools_for_model("gpt-4")
    assert isinstance(model_tools, list)

    rendered = render_tools([tool_def], ModelFormat.OPENAI)
    assert isinstance(rendered, list)

    rendered_ant = render_anthropic_tools([tool_def])
    assert isinstance(rendered_ant, list)

    rendered_open = render_openai_tools([tool_def])
    assert isinstance(rendered_open, list)

    rendered_oll = render_ollama_tools([tool_def])
    assert isinstance(rendered_oll, list)


def test_package_functionality():
    """Verify package functions work correctly."""
    from agents import (
        TOOL_DEFINITIONS,
        ModelFormat,
        detect_model_format,
        render_tools,
    )

    fmt = detect_model_format("gpt-4")
    assert fmt == ModelFormat.OPENAI

    fmt = detect_model_format("claude-3")
    assert fmt == ModelFormat.ANTHROPIC

    fmt = detect_model_format("ollama/llama2")
    assert fmt == ModelFormat.OLLAMA

    rendered = render_tools(TOOL_DEFINITIONS, ModelFormat.OPENAI)
    assert isinstance(rendered, list)
